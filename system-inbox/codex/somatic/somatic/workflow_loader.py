import json
from pathlib import Path

from .contracts import MOCK_PROVIDER_FILES, REQUIRED_WORKFLOW_FIELDS, SUPPORTED_WORKFLOW_MODES
from .sensors.registry import validate_sensor_evidence_workflow_config


class WorkflowValidationError(ValueError):
    """Raised when a workflow fixture does not match the Phase 1A contract."""


def load_workflow(path):
    workflow_path = Path(path)
    workflow = parse_simple_yaml(workflow_path.read_text(encoding="utf-8"))
    validate_workflow(workflow, workflow_path)
    return workflow


def validate_workflow(workflow, source_path=None):
    missing = [field for field in REQUIRED_WORKFLOW_FIELDS if field not in workflow]
    if missing:
        location = f" in {source_path}" if source_path else ""
        raise WorkflowValidationError(
            f"Workflow{location} missing required fields: {', '.join(missing)}"
        )

    mode = workflow.get("mode")
    if mode not in SUPPORTED_WORKFLOW_MODES:
        raise WorkflowValidationError("Workflow mode invalid: workflow_mode_unsupported")

    for field in ("stages", "inputs", "providers", "artifacts"):
        if not isinstance(workflow.get(field), list):
            raise WorkflowValidationError(f"Workflow field {field!r} must be a list")

    if not isinstance(workflow.get("safety_profile"), dict):
        raise WorkflowValidationError("Workflow field 'safety_profile' must be an object")

    sensor_evidence_validation = validate_sensor_evidence_workflow_config(workflow)
    if not sensor_evidence_validation.valid:
        raise WorkflowValidationError(
            "Workflow sensor evidence config invalid: "
            + ", ".join(sensor_evidence_validation.errors)
        )

    return workflow


def load_mock_provider_metadata(workflow, repo_root):
    root = Path(repo_root)
    loaded = {}
    for provider in workflow.get("providers", []):
        provider_class = provider.get("class")
        provider_ref = provider.get("ref")
        filename = MOCK_PROVIDER_FILES.get(provider_class)
        if not filename:
            continue
        provider_path = root / "fixtures" / "providers" / filename
        if not provider_path.exists():
            raise FileNotFoundError(
                f"Missing mock provider fixture for {provider_class}: {provider_path}"
            )
        loaded[provider_ref] = json.loads(provider_path.read_text(encoding="utf-8"))
    return loaded


def parse_simple_yaml(text):
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise WorkflowValidationError("Tabs are not supported in workflow fixtures")
        lines.append((indent, raw.strip()))
    if not lines:
        return {}
    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise WorkflowValidationError("Unexpected trailing YAML content")
    return value


def _parse_block(lines, index, indent):
    if index >= len(lines):
        return {}, index
    if lines[index][0] < indent:
        return {}, index
    if lines[index][1].startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_dict(lines, index, indent)


def _parse_dict(lines, index, indent):
    result = {}
    while index < len(lines):
        line_indent, stripped = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise WorkflowValidationError(f"Unexpected indentation before {stripped!r}")
        if stripped.startswith("- "):
            break
        key, raw_value = _split_key_value(stripped)
        index += 1
        if raw_value == "":
            if index < len(lines) and lines[index][0] > line_indent:
                value, index = _parse_block(lines, index, lines[index][0])
            else:
                value = {}
        else:
            value = _parse_scalar(raw_value)
        result[key] = value
    return result, index


def _parse_list(lines, index, indent):
    result = []
    while index < len(lines):
        line_indent, stripped = lines[index]
        if line_indent < indent:
            break
        if line_indent != indent or not stripped.startswith("- "):
            break
        item_text = stripped[2:].strip()
        index += 1
        if item_text == "":
            if index < len(lines) and lines[index][0] > line_indent:
                item, index = _parse_block(lines, index, lines[index][0])
            else:
                item = None
            result.append(item)
            continue
        if _looks_like_key_value(item_text):
            key, raw_value = _split_key_value(item_text)
            item = {}
            if raw_value == "":
                if index < len(lines) and lines[index][0] > line_indent:
                    value, index = _parse_block(lines, index, lines[index][0])
                else:
                    value = {}
            else:
                value = _parse_scalar(raw_value)
            item[key] = value
            if index < len(lines) and lines[index][0] > line_indent:
                continuation, index = _parse_block(lines, index, lines[index][0])
                if isinstance(continuation, dict):
                    item.update(continuation)
                else:
                    item.setdefault("items", continuation)
            result.append(item)
        else:
            result.append(_parse_scalar(item_text))
    return result, index


def _looks_like_key_value(text):
    if ":" not in text:
        return False
    key, _ = text.split(":", 1)
    return bool(key.strip()) and " " not in key.strip()


def _split_key_value(text):
    if ":" not in text:
        raise WorkflowValidationError(f"Expected key/value line, got {text!r}")
    key, value = text.split(":", 1)
    key = key.strip()
    if not key:
        raise WorkflowValidationError(f"Empty key in line {text!r}")
    return key, value.strip()


def _parse_scalar(value):
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith("[") and value.endswith("]"):
        return [_parse_scalar(part.strip()) for part in value[1:-1].split(",") if part.strip()]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value
