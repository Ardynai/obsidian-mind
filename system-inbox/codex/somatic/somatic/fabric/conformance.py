from dataclasses import dataclass

from somatic.fabric.canonical import FabricJsonError, validate_integer_only_json
from somatic.fabric.manifest import license_gate_errors
from somatic.fabric.pathing import path_confinement_errors, path_error
from somatic.fabric.signing import code_signature_threshold_errors


MAX_FABRIC_INTEGER = 2**53 - 1


@dataclass(frozen=True)
class FabricPrecheckResult:
    valid: bool
    errors: tuple[str, ...]


def integer_only_json_errors(value, path="$"):
    try:
        validate_integer_only_json(value, path=path)
        return []
    except FabricJsonError as exc:
        return [str(exc)]


def basic_conformance_precheck(manifest):
    errors = []
    errors.extend(integer_only_json_errors(manifest))
    errors.extend(path_confinement_errors(manifest))
    errors.extend(code_signature_threshold_errors(manifest))
    errors.extend(license_gate_errors(manifest))
    return FabricPrecheckResult(valid=not errors, errors=tuple(errors))
