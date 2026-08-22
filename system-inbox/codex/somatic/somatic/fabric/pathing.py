from somatic.fabric.spec import TYPE_INSTALL_DIR


class FabricPathError(ValueError):
    """Raised when a Fabric payload path escapes its allowed shape."""


def path_error(value):
    if not isinstance(value, str) or not value:
        return "path must be a non-empty string"
    if value.startswith(("/", "\\")):
        return "path must be relative"
    if len(value) >= 2 and value[1] == ":" and value[0].isalpha():
        return "path must not contain a Windows drive"
    if "\\" in value or "\0" in value:
        return "path must use POSIX separators and contain no NUL"
    if any(segment in {"", ".", ".."} for segment in value.split("/")):
        return "path must not contain empty, . or .. segments"
    return None


def validate_payload_path(value):
    error = path_error(value)
    if error:
        raise FabricPathError(error)
    return value


def type_install_root(fabric_type):
    try:
        return TYPE_INSTALL_DIR[fabric_type]
    except KeyError as exc:
        raise FabricPathError(f"Unknown Fabric type: {fabric_type}") from exc


def validate_install_target_for_type(fabric_type, install_target):
    validate_payload_path(install_target)
    root = type_install_root(fabric_type)
    return f"{root}/{install_target}"


def path_confinement_errors(manifest):
    errors = []
    files = manifest.get("files", [])
    fabric_type = manifest.get("type")
    if not isinstance(files, list):
        return ["files must be a list for path confinement precheck"]
    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"files[{index}] must be an object")
            continue
        for field in ("path", "installTarget"):
            error = path_error(entry.get(field))
            if error:
                errors.append(f"files[{index}].{field} is not confined: {error}")
        if isinstance(entry.get("installTarget"), str):
            try:
                validate_install_target_for_type(fabric_type, entry["installTarget"])
            except FabricPathError as exc:
                errors.append(f"files[{index}].installTarget is not confined: {exc}")
    return errors
