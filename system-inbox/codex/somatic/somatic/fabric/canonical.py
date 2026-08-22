import json


MAX_FABRIC_INTEGER = 2**53 - 1


class FabricJsonError(ValueError):
    """Raised when a value cannot be represented as Fabric JSON."""


class FabricIntegerError(FabricJsonError):
    """Raised when Fabric JSON contains a non-integer or out-of-range number."""


def validate_integer_only_json(value, path="$"):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        _validate_json_string(value, path)
        return None
    if isinstance(value, int):
        if value < 0 or value > MAX_FABRIC_INTEGER:
            raise FabricIntegerError(f"{path} integer is outside [0, 2^53-1]")
        return None
    if isinstance(value, float):
        raise FabricIntegerError(f"{path} contains float; Fabric JSON permits integers only")
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_integer_only_json(item, f"{path}[{index}]")
        return None
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise FabricJsonError(f"{path} contains non-string object key {key!r}")
            _validate_json_string(key, f"{path} object key {key!r}")
            validate_integer_only_json(item, f"{path}.{key}")
        return None
    raise FabricJsonError(f"{path} contains unsupported JSON value {type(value).__name__}")


def validate_raw_json_numbers(raw_json):
    if not isinstance(raw_json, str):
        raise FabricJsonError("Fabric JSON input must be text")

    index = 0
    in_string = False
    escaped = False
    while index < len(raw_json):
        char = raw_json[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            index += 1
            continue
        if char == "+" and index + 1 < len(raw_json) and raw_json[index + 1].isdigit():
            raise FabricIntegerError("Fabric JSON numbers must not use plus signs")
        if char == "-" or char.isdigit():
            index = _validate_number_lexeme(raw_json, index)
            continue
        index += 1


def loads_fabric_json(raw_json):
    validate_raw_json_numbers(raw_json)
    parsed = json.loads(raw_json, object_pairs_hook=_reject_duplicate_object_pairs)
    validate_integer_only_json(parsed)
    return parsed


def canonical_dumps(value):
    """Return RFC 8785/JCS canonical JSON for Fabric-supported values."""
    validate_integer_only_json(value)
    return _serialize_canonical(value)


def canonical_bytes(value):
    return canonical_dumps(value).encode("utf-8")


def signing_payload(value):
    if not isinstance(value, dict):
        raise FabricJsonError("Fabric signing payload requires a top-level object")
    payload = dict(value)
    payload["signatures"] = []
    return canonical_bytes(payload)


def _validate_number_lexeme(raw_json, start):
    index = start
    if raw_json[index] == "-":
        raise FabricIntegerError("Fabric JSON numbers must be non-negative integers")

    if raw_json[index] == "0":
        index += 1
        if index < len(raw_json) and raw_json[index].isdigit():
            raise FabricIntegerError("Fabric JSON numbers must not use leading zeros")
    else:
        while index < len(raw_json) and raw_json[index].isdigit():
            index += 1

    if index < len(raw_json) and raw_json[index] == ".":
        raise FabricIntegerError("Fabric JSON numbers must not use decimal fractions")
    if index < len(raw_json) and raw_json[index] in {"e", "E"}:
        raise FabricIntegerError("Fabric JSON numbers must not use exponents")
    if index < len(raw_json) and raw_json[index] in {"+", "-"}:
        raise FabricIntegerError("Fabric JSON numbers must not use signs")

    value = int(raw_json[start:index])
    if value > MAX_FABRIC_INTEGER:
        raise FabricIntegerError("$ integer is outside [0, 2^53-1]")
    return index


def _serialize_canonical(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _quote_string(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ",".join(_serialize_canonical(item) for item in value) + "]"
    if isinstance(value, dict):
        items = []
        for key in sorted(value.keys(), key=_utf16_sort_key):
            items.append(f"{_quote_string(key)}:{_serialize_canonical(value[key])}")
        return "{" + ",".join(items) + "}"
    raise FabricJsonError(f"$ contains unsupported JSON value {type(value).__name__}")


def _quote_string(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _utf16_sort_key(value):
    return value.encode("utf-16-be", "surrogatepass")


def _validate_json_string(value, path):
    for index, char in enumerate(value):
        codepoint = ord(char)
        if 0xD800 <= codepoint <= 0xDFFF:
            raise FabricJsonError(f"{path}[{index}] contains invalid Unicode surrogate")


def _reject_duplicate_object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise FabricJsonError(f"Fabric JSON contains duplicate object key {key!r}")
        result[key] = value
    return result
