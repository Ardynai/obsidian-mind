from pathlib import Path


DEFAULT_LOCUS_CONTENT_FABRIC_PATHS = (
    "C:/AI/locus/electron/content-fabric",
    "C:/AI/locus/electron/server/routes/fabric.ts",
    "C:/AI/locus/electron/server/stream.ts",
    "C:/AI/locus/tests/content/content-fabric.test.ts",
    "C:/AI/locus/tests/security/content-fabric-security.test.ts",
)

DEFAULT_METADATA_FIELDS = (
    "schemaVersion",
    "id",
    "version",
    "class",
    "type",
    "license",
)


def describe_interop_fixture_locations(repo_root=None):
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    interop_dir = root / "fixtures" / "fabric" / "interop"
    return {
        "somatic_interop_dir": _posix(interop_dir),
        "somatic_locus_placeholder": _posix(interop_dir / "locus-fixtures-placeholder.md"),
        "somatic_fixture_placeholder": _posix(
            interop_dir / "somatic-fixtures-placeholder.md"
        ),
        "somatic_generated_pack": _posix(interop_dir / "somatic-generated-pack.json"),
        "somatic_generated_keyring": _posix(interop_dir / "somatic-generated-keyring.json"),
        "somatic_generated_catalog": _posix(interop_dir / "somatic-generated-catalog.json"),
        "somatic_generated_metadata": _posix(
            interop_dir / "somatic-generated-metadata.json"
        ),
        "locus_expected_paths": DEFAULT_LOCUS_CONTENT_FABRIC_PATHS,
    }


def compare_fixture_metadata(left, right, fields=DEFAULT_METADATA_FIELDS):
    matching = []
    different = []
    missing = []

    for field in fields:
        left_has = field in left
        right_has = field in right
        if not left_has or not right_has:
            missing.append(field)
        elif left[field] == right[field]:
            matching.append(field)
        else:
            different.append(field)

    return {
        "matching": tuple(sorted(matching)),
        "different": tuple(sorted(different)),
        "missing": tuple(sorted(missing)),
    }


def _posix(path):
    return str(path).replace("\\", "/")
