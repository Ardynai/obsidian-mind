"""Consent-gated safety core for informational advisory framing.

This module enables evidence-graded, professionally routed decision-support on
a user's own data behind explicit consent. It enforces informational framing on
OUTPUT — it does not block advisory capability when consent is granted.

Language scope: English plus first-class Spanish and French red-flag /
emergency and advisory-framing lexicons (NFKC-normalized). Other languages
remain a known limit, not a silent pass. Crisis routing defaults to the US 988
Suicide & Crisis Lifeline and switches to a locale-appropriate line where known
(US 988 press 2 for Spanish; Spain 024; France 3114); callers elsewhere should
use local emergency services.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from somatic.consent.ledger import ConsentLedger
from somatic.consent.scopes import ConsentScope, resolve_scope

INFORMATIONAL_NOTICE = (
    "Informational only — not a diagnosis or treatment. Confirm with a licensed professional."
)
PROFESSIONAL_ROUTING = (
    "Discuss these informational findings with a licensed clinician or other "
    "qualified professional before acting on them."
)
EMERGENCY_GUIDANCE = (
    "Seek immediate/emergency care. If this is a medical emergency, call your "
    "local emergency number now."
)
CRISIS_GUIDANCE = (
    "If you are thinking about suicide or self-harm, contact a crisis line now. "
    "In the US, call or text 988 (Suicide & Crisis Lifeline). "
    "If you are in immediate danger, call your local emergency number."
)
CRISIS_GUIDANCE_ES = (
    "Busca ayuda ahora: si piensas en quitarte la vida o hacerte daño, contacta "
    "una línea de crisis. En EE. UU., llama o envía un mensaje al 988 y oprime 2 "
    "para español. En España, llama al 024. En Francia, llama al 3114. "
    "Si estás en peligro inmediato, llama al número de emergencias local."
)
CRISIS_GUIDANCE_FR = (
    "Cherchez de l'aide maintenant : si vous pensez au suicide ou à vous faire du "
    "mal, contactez une ligne d'écoute. En France, appelez le 3114 (numéro "
    "national de prévention du suicide). Aux États-Unis, appelez ou envoyez un "
    "SMS au 988. En cas de danger immédiat, appelez votre numéro d'urgence local."
)
EMERGENCY_GUIDANCE_ES = (
    "Busca atención de emergencia ahora. Si es una emergencia médica, llama a tu "
    "número de emergencias local."
)
EMERGENCY_GUIDANCE_FR = (
    "Consultez en urgence. S'il s'agit d'une urgence médicale, appelez votre "
    "numéro d'urgence local."
)
LANGUAGE_SCOPE = "english-spanish-french"
CRISIS_LINE_POLICY = "us-988-default"

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff\u2060\u00ad"), None)


class EvidenceGrade:
    """Evidence-strength labels for advisory outputs."""

    STRONG = "strong"
    MODERATE = "moderate"
    LIMITED = "limited"
    PRELIMINARY = "preliminary"
    NONE = "none"

    ALL = (STRONG, MODERATE, LIMITED, PRELIMINARY, NONE)


@dataclass(frozen=True)
class AdvisoryResult:
    """Informational advisory payload with evidence grade and routing."""

    summary: str
    evidence_grade: str
    sources: tuple[str, ...]
    professional_routing: str
    informational_notice: str
    consent_scope: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_grade": self.evidence_grade,
            "sources": list(self.sources),
            "professional_routing": self.professional_routing,
            "informational_notice": self.informational_notice,
            "consent_scope": self.consent_scope,
        }


@dataclass(frozen=True)
class EmergencyResult:
    """Outcome of a pre-analysis emergency red-flag screen.

    ``locale`` records which lexicon matched ("en", "es", "fr") so callers can
    surface locale-appropriate crisis routing; "en" remains the default.
    """

    triggered: bool
    guidance: str
    kind: str = "none"
    locale: str = "en"


class ConsentRequiredError(PermissionError):
    """Raised when a required consent scope is not granted."""

    def __init__(self, scope_id: str) -> None:
        self.scope_id = scope_id
        super().__init__(f"consent required for scope: {scope_id}")


class AdvisoryFramingError(ValueError):
    """Raised when advisory text uses authoritative diagnosis/prescription phrasing."""


def require_consent(ledger: ConsentLedger, scope: ConsentScope | str) -> None:
    """Return None when ``scope`` is granted; otherwise raise :class:`ConsentRequiredError`."""

    resolved = resolve_scope(scope)
    if not ledger.is_granted(resolved):
        raise ConsentRequiredError(resolved.id)


def normalize_scan_text(text: str) -> str:
    """NFKC-normalize, turn zero-width points into separators, squeeze letters.

    Zero-width characters are replaced with a space (not deleted) so invisible
    characters cannot fuse red-flag words into one token in any language.
    Spaced-out letter runs ("c h e s t", Latin or accented) are squeezed back
    into words.
    """

    normalized = unicodedata.normalize("NFKC", str(text or ""))
    normalized = normalized.translate({code: " " for code in _ZERO_WIDTH})
    normalized = re.sub(r"\s+", " ", normalized)
    squeezed = re.sub(
        r"(?<![^\W\d_])(?:[^\W\d_] ){2,}[^\W\d_](?![^\W\d_])",
        lambda match: match.group(0).replace(" ", ""),
        normalized,
    )
    return squeezed


_BENIGN_YOU_HAVE = (
    "been",
    "had",
    "not",
    "logged",
    "done",
    "seen",
    "noticed",
    "reported",
    "slept",
    "tracked",
    "recorded",
    "measured",
    "noted",
    "listed",
    "entered",
)
_YOU_HAVE_BLOCK = "|".join(_BENIGN_YOU_HAVE)

# Medical emergencies. Bare "stroke" / "heart attack" fire unless they sit in a
# benign metric/risk/sport phrase ("stroke rate", "heart attack risk/score",
# "rowing stroke").
_HEART_ATTACK_TOKEN = re.compile(r"\bheart\s*attacks?\b", re.IGNORECASE)
_HEART_ATTACK_BENIGN_TAIL = re.compile(r"\s+(?:risk|score)s?\b", re.IGNORECASE)
_STROKE_TOKEN = re.compile(r"\bstroke\b", re.IGNORECASE)
_STROKE_BENIGN_TAIL = re.compile(r"\s+(?:rate|count|volume)s?\b", re.IGNORECASE)
_STROKE_BENIGN_HEAD = re.compile(r"\b(?:rowing|swim(?:ming)?)\s+$", re.IGNORECASE)

_MEDICAL_EMERGENCY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bchest\s*pain\b",
        r"\bcrushing\s+(?:chest\s+)?pressure\b",
        r"\bpressure\s+in\s+my\s+chest\b",
        r"\bdifficulty\s+breathing\b",
        r"\bshort(?:ness)?\s+of\s+breath\b",
        r"\bcan'?t\s+breathe\b",
        r"\b(?:having|have)\s+(?:a\s+)?heart\s*attack\b",
        r"\b(?:having|have)\s+(?:a\s+)?stroke\b",
        r"\bfacial\s+droop\b",
        r"\barm\s+weakness\b",
        r"\bspeech\s+(?:slurred|difficulty|trouble)\b",
        r"\bsudden\s+numbness\b",
        r"\b(?:one|left|right)[\s-]+sided\s+(?:weakness|numbness)\b",
        r"\banaphylaxis\b",
        r"\bsevere\s+allergic\s+reaction\b",
        r"\bthroat\s+(?:closing|swelling)\b",
        r"\bsevere\s+bleeding\b",
        r"\buncontrolled\s+bleeding\b",
        r"\bloss\s+of\s+consciousness\b",
        r"\b(?:passed|pass(?:ing)?)\s+out\b",
        r"\bfaint(?:ed|ing)\b",
        r"\bseizure\b",
        r"\bconvuls(?:ion|ing)\b",
        r"\boverdose\b",
        r"\btook\s+(?:too\s+many|\d+)\s+(?:pills|tylenol|acetaminophen|aspirin)\b",
        r"\bcough(?:ing)?\s+up\s+blood\b",
        r"\bhemoptysis\b",
        r"\bblack\s+and\s+tarry\s+stool\b",
        r"\btarry\s+stool\b",
        r"\bmelena\b",
        r"\bworst\s+headache\s+of\s+my\s+life\b",
        r"\bthunderclap\s+headache\b",
    )
)

_CRISIS_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bsuicidal\b",
        r"\bkill\s+myself\b",
        r"\bwant\s+to\s+die\b",
        r"\bend\s+my\s+life\b",
        r"\bself[\s-]*harm\s+thoughts?\b",
        r"\bdon'?t\s+want\s+to\s+be\s+alive\b",
        r"\bthinking\s+about\s+suicide\b",
        r"\bbetter\s+off\s+dead\b",
    )
)

# Spanish red flags. Additive: no English pattern above is weakened or removed.
_MEDICAL_EMERGENCY_PATTERNS_ES: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bdolor\s+(?:en|de)\s+(?:el\s+)?pecho\b",
        r"\bopresi[oó]n\s+en\s+el\s+pecho\b",
        r"\bdificultad\s+para\s+respirar\b",
        r"\bno\s+puedo\s+respirar\b",
        r"\bme\s+est(?:á|a)\s+dando\s+un\s+infarto\b",
        r"\bataque\s+al?\s+coraz[oó]n\b",
        r"\bparo\s+card[ií]aco\b",
        r"\bderrame\s+cerebral\b",
        r"\baccidente\s+cerebrovascular\b",
        r"\bpar[aá]lisis\s+facial\b",
        r"\bentumecimiento\s+(?:s[úu]bito|repentino)\b",
        r"\bdebilidad\s+de\s+un\s+lado\b",
        r"\bconvulsi(?:ones|ón)\b",
        r"\bsobredosis\b",
        r"\btom[eé]\s+\d+\s+(?:pastillas|comprimidos)\b",
        r"\btosiendo\s+sangre\b",
        r"\bsangre\s+al\s+toser\b",
        r"\bescupo\s+con\s+sangre\b",
        r"\bsangrado\s+(?:abundante|que\s+no\s+se\s+detiene)\b",
        r"\bhemorragia\b",
        r"\bperd[ií]\s+el\s+conocimiento\b",
        r"\bme\s+desmay[eé]\b",
        r"\breacci[oó]n\s+al[eé]rgica\s+grave\b",
        r"\banafilaxia\b",
        r"\bse\s+me\s+cierra\s+la\s+garganta\b",
        r"\bel\s+peor\s+dolor\s+de\s+cabeza\s+de\s+mi\s+vida\b",
    )
)

_CRISIS_PATTERNS_ES: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bsuicid(?:arme|arse|io|ida)\b",
        r"\bpensamientos\s+suicidas\b",
        r"\bpensando\s+en\s+suicidarme\b",
        r"\bmatarme\b",
        r"\bquitarme\s+la\s+vida\b",
        r"\bquiero\s+morir\b",
        r"\bno\s+quiero\s+vivir\b",
        r"\bno\s+quiero\s+estar\s+vivo\b",
        r"\bquiero\s+hacerme\s+da[nñ]o\b",
        r"\bquiero\s+lastimarme\b",
        r"\bautolesi[oó]n\b",
    )
)

# French red flags. Additive.
_MEDICAL_EMERGENCY_PATTERNS_FR: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bdouleur\s+[àa]\s+la\s+poitrine\b",
        r"\bdouleur\s+thoracique\b",
        r"\boppression\s+dans\s+la\s+poitrine\b",
        r"\bdifficult[eé]s?\s+[àa]\s+respirer\b",
        r"\bje\s*n'?arrive\s+pas\s*[àa]\s+respirer\b",
        r"\bj'[eé]touff(?:e|es)\b",
        r"\bcrise\s+cardiaque\b",
        r"\binfarctus\b",
        r"\barr[eê]t\s+cardiaque\b",
        r"\bje\s+fais\s+un\s+avc\b",
        r"\baccident\s+vasculaire\s+c[eé]r[eé]bral\b",
        r"\bparalysie\s+faciale\b",
        r"\bengourdissement\s+soudain\b",
        r"\bfaiblesse\s+d'un\s+c[oô]t[eé]\b",
        r"\bconvulsions?\b",
        r"\bsurdose\b",
        r"\bj'ai\s+(?:pris|aval[eé])\s+\d+\s+comprim[eé]s\b",
        r"\bje\s+crache\s+du\s+sang\b",
        r"\bvomir\s+du\s+sang\b",
        r"\bh[eé]morragie\b",
        r"\bsaignement\s+(?:abondant|qui\s+ne\s+s'arr[eê]te\s+pas)\b",
        r"\bj'ai\s+perdu\s+connaissance\b",
        r"\bje\s+m'[eé]vanouis\b",
        r"\br[eé]action\s+allergique\s+grave\b",
        r"\banaphylaxie\b",
        r"\bma\s+gorge\s+se\s+ferme\b",
        r"\ble\s+pire\s+mal\s+de\s+t[eê]te\s+de\s+ma\s+vie\b",
    )
)

_CRISIS_PATTERNS_FR: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bme\s+suicider\b",
        r"\bpens[eé]es?\s+suicidaires\b",
        r"\bpenser\s+au\s+suicide\b",
        r"\bme\s+tuer\b",
        r"\bmettre\s+fin\s+[àa]\s+mes\s+jours\b",
        r"\bje\s+veux\s+mourir\b",
        r"\bje\s+ne\s+veux\s+plus\s+vivre\b",
        r"\bje\s+veux\s+me\s+faire\s+du\s+mal\b",
        r"\bm'automutiler\b",
    )
)

# Authoritative diagnosis / dosing. Avoid matching metric names and the
# informational "your data suggests …" phrasing the adapter system prompt uses.
_AUTHORITATIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        rf"\byou\s+have\s+(?:a\s+|an\s+)?(?!{_YOU_HAVE_BLOCK}\b)[a-z]",
        r"\byou\s+have\s+been\s+diagnosed\b",
        r"\byou\s+likely\s+have\b",
        r"\byou\s+probably\s+have\b",
        r"\bdiagnosed\s+with\b",
        r"\bdiagnosis\s+is\b",
        r"\bthis\s+confirms\s+(?:you\s+have|a\s+diagnosis)\b",
        r"\byour\s+results\s+indicate\b",
        r"\bresults\s+indicate\s+(?:that\s+)?you\s+have\b",
        r"\bconsistent\s+with\s+(?:a\s+)?(?:diagnosis|cancer|diabetes|hypothyroidism)\b",
        r"\bsuggests?\s+(?:that\s+)?you\s+have\b",
        r"\btake\s+\d+(?:\.\d+)?\s*(?:mg|milligrams?|mcg|ug|ml)\b",
        r"\b(?:i\s+|we\s+)?recommend\s+\d+(?:\.\d+)?\s*(?:mg|milligrams?)\b",
        r"\bstart\s+[a-z][a-z\-]{2,40}\s+\d+(?:\.\d+)?\s*(?:mg|milligrams?)\b",
        r"\b(?:i|we)\s+prescribe\b",
        r"\bprescribed\s+(?!dose\b)[a-z]",
        r"\bstop\s+taking\s+(?:your\s+)?(?:current\s+)?(?:medication|meds|pills|[a-z]+)\b",
        r"\byou\s+must\s+take\b",
        r"(?m)^\s*diagnosis\s*:\s+\S",
        r"\bdiagnosis:\s+[a-z]",
        r"(?m)^\s*take\s+\d+(?:\.\d+)?\s*(?:mg|mcg|ug|ml)\b",
    )
)

# Spanish / French advisory-framing denylists. Additive; English unchanged.
_AUTHORITATIVE_PATTERNS_ES: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:tienes|usted\s+tiene)\s+(?:el\s+)?c[aá]ncer\b",
        r"\b(?:tienes|usted\s+tiene)\s+diabetes\b",
        r"\ble\s+diagnostico\s+(?:con\s+)?[a-z]",
        r"\bel\s+diagn[oó]stico\s+es\b",
        r"\besto\s+confirma\s+(?:tu\s+)?diagn[oó]stico\b",
        r"\btus\s+resultados\s+indican\b",
        r"\bdebes?\s+tomar\s+\d+\s*(?:mg|miligramos?)\b",
        r"\btoma\s+\d+(?:\.\d+)?\s*(?:mg|miligramos?|mcg|ml)\b",
        r"\brecomiendo\s+\d+(?:\.\d+)?\s*(?:mg|miligramos?)\b",
        r"\bte\s+receto\b",
        r"\ble\s+receto\b",
        r"\bdeja\s+de\s+tomar\s+tu\s+(?:medicaci[oó]n|medicamento|pastillas)\b",
        r"(?m)^\s*diagn[oó]stico\s*:\s+\S",
    )
)

_AUTHORITATIVE_PATTERNS_FR: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bvous\s+avez\s+un\s+cancer\b",
        r"\bvous\s+avez\s+(?:le\s+)?diab[eè]te\b",
        r"\bvous\s+[eê]tes\s+atteint\s+d[e']\b",
        r"\ble\s+diagnostic\s+est\s+pos[eé]\b",
        r"\bvotre\s+diagnostic\s*:\s*\S",
        r"\bces\s+résultats\s+indiquent\b",
        r"\bprenez\s+\d+(?:\.\d+)?\s*(?:mg|milligrammes?)\b",
        r"\bje\s+vous\s+prescris\b",
        r"\bje\s+recommande\s+\d+(?:\.\d+)?\s*(?:mg|milligrammes?)\b",
        r"\barr[eê]tez\s+votre\s+traitement\b",
        r"\bvous\s+devez\s+prendre\b",
        r"(?m)^\s*diagnostic\s*:\s+\S",
    )
)


def emergency_screen(text: str) -> EmergencyResult:
    """Scan ``text`` for emergency red flags before analysis.

    Callers should short-circuit when ``triggered`` is True and surface
    ``guidance`` instead of continuing advisory analysis. English, Spanish,
    and French lexicons are checked; suicidal ideation routes to the
    locale-appropriate crisis line (US 988 default, 988 press 2 for Spanish,
    Spain 024, France 3114). Risk-trend questions and bare metric names such
    as "stroke rate" or "ritmo cardiaco" should not trigger.
    """

    haystack = normalize_scan_text(text)
    for patterns, guidance in (
        (_CRISIS_PATTERNS, CRISIS_GUIDANCE),
        (_CRISIS_PATTERNS_ES, CRISIS_GUIDANCE_ES),
        (_CRISIS_PATTERNS_FR, CRISIS_GUIDANCE_FR),
    ):
        for pattern in patterns:
            if pattern.search(haystack):
                locale = _locale_for(patterns)
                return EmergencyResult(
                    triggered=True, guidance=guidance, kind="crisis", locale=locale
                )
    medical = (
        (_MEDICAL_EMERGENCY_PATTERNS, EMERGENCY_GUIDANCE),
        (_MEDICAL_EMERGENCY_PATTERNS_ES, EMERGENCY_GUIDANCE_ES),
        (_MEDICAL_EMERGENCY_PATTERNS_FR, EMERGENCY_GUIDANCE_FR),
    )
    for patterns, guidance in medical:
        for pattern in patterns:
            if pattern.search(haystack):
                locale = _locale_for(patterns)
                return EmergencyResult(
                    triggered=True, guidance=guidance, kind="medical", locale=locale
                )
    if _has_emergency_heart_attack(haystack) or _has_emergency_stroke(haystack):
        return EmergencyResult(triggered=True, guidance=EMERGENCY_GUIDANCE, kind="medical")
    return EmergencyResult(triggered=False, guidance="", kind="none")


def _locale_for(patterns: tuple[re.Pattern[str], ...]) -> str:
    if patterns is _CRISIS_PATTERNS_ES or patterns is _MEDICAL_EMERGENCY_PATTERNS_ES:
        return "es"
    if patterns is _CRISIS_PATTERNS_FR or patterns is _MEDICAL_EMERGENCY_PATTERNS_FR:
        return "fr"
    return "en"


def _has_emergency_heart_attack(haystack: str) -> bool:
    for match in _HEART_ATTACK_TOKEN.finditer(haystack):
        if _HEART_ATTACK_BENIGN_TAIL.match(haystack[match.end() :]):
            continue
        return True
    return False


def _has_emergency_stroke(haystack: str) -> bool:
    for match in _STROKE_TOKEN.finditer(haystack):
        if _STROKE_BENIGN_HEAD.search(haystack[: match.start()]):
            continue
        if _STROKE_BENIGN_TAIL.match(haystack[match.end() :]):
            continue
        return True
    return False


def _structural_authoritative(text: str) -> bool:
    """Catch model-shaped lines like ``Diagnosis: X.`` or ``Take N mg.``."""

    for line in str(text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if lower.startswith("diagnosis:") and len(stripped) > 10:
            return True
        if lower.startswith("take ") and any(unit in lower for unit in (" mg", " mcg", " ml")):
            return True
    return False


def frame_advisory(
    summary: str,
    evidence_grade: str,
    sources: tuple[str, ...] | list[str],
    consent_scope: ConsentScope | str,
    *,
    authoritative_scan: bool = True,
) -> AdvisoryResult:
    """Build an informational :class:`AdvisoryResult`.

    Raises :class:`AdvisoryFramingError` when ``summary`` contains authoritative
    diagnosis, prescription, or dosing phrasing. Capability is not blocked —
    only non-informational OUTPUT framing is rejected. Engine-authored templates
    should pass ``authoritative_scan=False`` so user-controlled metric names
    cannot crash the analyze path; the adapter still scans model output.
    """

    resolved = resolve_scope(consent_scope)
    grade = str(evidence_grade)
    if grade not in EvidenceGrade.ALL:
        raise AdvisoryFramingError(f"unknown evidence grade: {grade}")
    text = str(summary or "").strip()
    if not text:
        raise AdvisoryFramingError("advisory summary must be non-empty")
    if authoritative_scan:
        haystack = normalize_scan_text(text)
        for patterns in (
            _AUTHORITATIVE_PATTERNS,
            _AUTHORITATIVE_PATTERNS_ES,
            _AUTHORITATIVE_PATTERNS_FR,
        ):
            for pattern in patterns:
                if pattern.search(haystack):
                    raise AdvisoryFramingError(
                        "advisory summary uses authoritative diagnosis or prescription phrasing"
                    )
        if _structural_authoritative(text):
            raise AdvisoryFramingError(
                "advisory summary uses authoritative diagnosis or prescription phrasing"
            )
    source_tuple = tuple(str(item) for item in sources)
    return AdvisoryResult(
        summary=text,
        evidence_grade=grade,
        sources=source_tuple,
        professional_routing=PROFESSIONAL_ROUTING,
        informational_notice=INFORMATIONAL_NOTICE,
        consent_scope=resolved.id,
    )
