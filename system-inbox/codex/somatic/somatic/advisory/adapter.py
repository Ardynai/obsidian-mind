"""Consent-gated OpenAI-compatible AI advisory adapter.

Sends a user's own data packet to a configured model endpoint and returns an
informational, evidence-graded :class:`~somatic.safety.core.AdvisoryResult`.
Requires ``AI_ADVISORY`` consent before any network call. Stdlib only.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import AI_ADVISORY
from somatic.net.ssrf import is_blocked_ip, parse_host_ip
from somatic.safety.core import (
    EMERGENCY_GUIDANCE,
    INFORMATIONAL_NOTICE,
    PROFESSIONAL_ROUTING,
    AdvisoryFramingError,
    AdvisoryResult,
    EvidenceGrade,
    emergency_screen,
    frame_advisory,
    require_consent,
)

from .models import DEFAULT_CHAT_PATH, OPENAI_COMPATIBLE, get_model_option

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RESPONSE_BYTES = 2_000_000

SYSTEM_PROMPT = (
    "You are an INFORMATIONAL health decision-support assistant. "
    "Never diagnose, prescribe, or give dosing instructions. "
    "Frame findings as 'your data suggests' or "
    "'it may be worth discussing X with a licensed professional'. "
    "Include an evidence grade (strong, moderate, limited, preliminary, or none). "
    "Always recommend confirming findings with a licensed professional. "
    "Respond with plain informational text only."
)

SAFE_FALLBACK_SUMMARY = (
    "The model response could not be framed as informational decision-support. "
    "Please consult a licensed professional about your data and question."
)


class AdvisoryConfigError(ValueError):
    """Raised when advisory model configuration is missing or unsafe."""


class AdvisoryHttpError(RuntimeError):
    """Raised when the model endpoint returns an unusable response."""


@dataclass(frozen=True)
class AdvisoryModelConfig:
    """Runtime configuration for an OpenAI-compatible advisory endpoint."""

    model_url: str
    model: str
    model_key: str = ""
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    option_id: str = OPENAI_COMPATIBLE.id
    chat_path: str = DEFAULT_CHAT_PATH

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> AdvisoryModelConfig:
        env = os.environ if environ is None else environ
        option_id = str(env.get("SOMATIC_ADVISORY_MODEL_OPTION", OPENAI_COMPATIBLE.id)).strip()
        option = get_model_option(option_id) or OPENAI_COMPATIBLE
        model = str(env.get("SOMATIC_ADVISORY_MODEL", "")).strip()
        if not model and option.model:
            model = option.model
        timeout_raw = str(env.get("SOMATIC_ADVISORY_TIMEOUT_SECONDS", "")).strip()
        try:
            timeout_seconds = float(timeout_raw) if timeout_raw else DEFAULT_TIMEOUT_SECONDS
        except ValueError:
            timeout_seconds = DEFAULT_TIMEOUT_SECONDS
        return cls(
            model_url=str(env.get("SOMATIC_ADVISORY_MODEL_URL", "")).strip(),
            model=model,
            model_key=str(env.get("SOMATIC_ADVISORY_MODEL_KEY", "")).strip(),
            timeout_seconds=timeout_seconds,
            option_id=option.id,
            chat_path=option.default_path or DEFAULT_CHAT_PATH,
        )

    def validate(self) -> None:
        if not self.model_url:
            raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL_URL is required")
        if not self.model:
            raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL is required")
        parsed = urllib_parse.urlsplit(self.model_url)
        if parsed.scheme not in {"http", "https"}:
            raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL_URL must use http or https")
        if not parsed.hostname:
            raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL_URL must include a host")
        if parsed.username or parsed.password:
            raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL_URL must not embed credentials")
        _assert_model_host_allowed(parsed, self.model_key)
        if self.timeout_seconds <= 0:
            raise AdvisoryConfigError("advisory timeout_seconds must be positive")


class AdvisoryModelClient:
    """Consent-gated client for OpenAI-compatible chat completions."""

    def __init__(self, config: AdvisoryModelConfig) -> None:
        config.validate()
        self._config = config

    def analyze(
        self,
        ledger: ConsentLedger,
        data_packet: dict[str, Any],
        question: str,
    ) -> AdvisoryResult:
        """Analyze a user data packet behind ``AI_ADVISORY`` consent."""

        require_consent(ledger, AI_ADVISORY)
        if not isinstance(data_packet, dict):
            raise TypeError("data_packet must be a dict")
        packet_json = json.dumps(data_packet, sort_keys=True, ensure_ascii=False)
        screen_text = f"{question}\n{packet_json}"
        emergency = emergency_screen(screen_text)
        if emergency.triggered:
            return AdvisoryResult(
                summary=emergency.guidance or EMERGENCY_GUIDANCE,
                evidence_grade=EvidenceGrade.NONE,
                sources=("emergency-screen",),
                professional_routing=PROFESSIONAL_ROUTING,
                informational_notice=INFORMATIONAL_NOTICE,
                consent_scope=AI_ADVISORY.id,
            )

        request_body = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\nUser data packet (JSON):\n{packet_json}"
                    ),
                },
            ],
            "temperature": 0,
        }
        assistant_text = self._post_chat(request_body)
        output_emergency = emergency_screen(assistant_text)
        if output_emergency.triggered:
            return AdvisoryResult(
                summary=output_emergency.guidance or EMERGENCY_GUIDANCE,
                evidence_grade=EvidenceGrade.NONE,
                sources=("emergency-screen", "model-output"),
                professional_routing=PROFESSIONAL_ROUTING,
                informational_notice=INFORMATIONAL_NOTICE,
                consent_scope=AI_ADVISORY.id,
            )
        grade = _parse_evidence_grade(assistant_text) or EvidenceGrade.LIMITED
        sources = (
            f"model:{self._config.model}",
            f"endpoint-option:{self._config.option_id}",
            "user-data-packet",
        )
        try:
            return frame_advisory(
                summary=assistant_text,
                evidence_grade=grade,
                sources=sources,
                consent_scope=AI_ADVISORY,
            )
        except AdvisoryFramingError:
            return AdvisoryResult(
                summary=SAFE_FALLBACK_SUMMARY,
                evidence_grade=EvidenceGrade.NONE,
                sources=("advisory-framing-fallback", *sources),
                professional_routing=PROFESSIONAL_ROUTING,
                informational_notice=INFORMATIONAL_NOTICE,
                consent_scope=AI_ADVISORY.id,
            )

    def _post_chat(self, request_body: dict[str, Any]) -> str:
        url = _join_base_url(self._config.model_url, self._config.chat_path)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._config.model_key:
            headers["Authorization"] = f"Bearer {self._config.model_key}"
        body = json.dumps(request_body).encode("utf-8")
        request = urllib_request.Request(url, data=body, headers=headers, method="POST")
        opener = urllib_request.build_opener(_NoRedirectHandler)
        try:
            with opener.open(  # nosec B310
                request,
                timeout=self._config.timeout_seconds,
            ) as response:
                raw = response.read(DEFAULT_MAX_RESPONSE_BYTES + 1)
        except urllib_error.HTTPError as exc:
            raise AdvisoryHttpError(
                f"advisory model HTTP request failed with status {exc.code}"
            ) from exc
        except urllib_error.URLError as exc:
            raise AdvisoryHttpError("advisory model HTTP request failed") from exc
        if len(raw) > DEFAULT_MAX_RESPONSE_BYTES:
            raise AdvisoryHttpError("advisory model response exceeded configured maximum")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AdvisoryHttpError("advisory model response was not valid JSON") from exc
        text = _extract_assistant_text(payload)
        if not text:
            raise AdvisoryHttpError("advisory model response missing assistant message text")
        return text


def _join_base_url(base_url: str, path: str) -> str:
    parsed_path = urllib_parse.urlsplit(path)
    if parsed_path.scheme or parsed_path.netloc:
        raise AdvisoryConfigError("advisory chat path must be relative")
    base = base_url.rstrip("/")
    suffix = path if path.startswith("/") else f"/{path}"
    if base.endswith("/v1") and suffix.startswith("/v1/"):
        suffix = suffix[3:]
    return f"{base}{suffix}"


class _NoRedirectHandler(urllib_request.HTTPRedirectHandler):
    """Refuse redirects so Authorization cannot follow a cross-origin hop."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        raise AdvisoryHttpError("advisory model HTTP redirects are not followed")


_METADATA_HOSTS = {"metadata.google.internal", "metadata", "metadata.google.com"}


def _assert_model_host_allowed(parsed: urllib_parse.SplitResult, model_key: str) -> None:
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        raise AdvisoryConfigError("SOMATIC_ADVISORY_MODEL_URL must include a host")
    ip = parse_host_ip(host)
    if host in _METADATA_HOSTS or is_blocked_ip(ip):
        raise AdvisoryConfigError("advisory model URL host is not allowed")
    loopback = host == "localhost" or (ip is not None and ip.is_loopback)
    if parsed.scheme != "https" and not loopback:
        if model_key:
            raise AdvisoryConfigError(
                "SOMATIC_ADVISORY_MODEL_KEY requires https or a loopback host"
            )
        raise AdvisoryConfigError("advisory model URL host is not allowed")
    if ip is not None and is_blocked_ip(ip):
        raise AdvisoryConfigError("advisory model URL host is not allowed")


def _extract_assistant_text(payload: object) -> str:
    if not isinstance(payload, dict):
        return ""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
    text = first.get("text")
    if isinstance(text, str):
        return text.strip()
    return ""


_GRADE_PATTERN = re.compile(
    r"\bevidence\s*grade\s*[:=]?\s*(strong|moderate|limited|preliminary|none)\b",
    re.IGNORECASE,
)


def _parse_evidence_grade(text: str) -> str | None:
    match = _GRADE_PATTERN.search(str(text or ""))
    if not match:
        return None
    return match.group(1).lower()
