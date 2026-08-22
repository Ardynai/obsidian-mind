FABRIC_SCHEMA_VERSION = "1.0.0"

FABRIC_CLASSES = frozenset(("data", "code"))

FABRIC_DATA_TYPES = frozenset(
    (
        "model",
        "asset-3d",
        "asset-audio",
        "asset-video",
        "asset-image",
        "dataset",
        "document",
        "theme",
    )
)

FABRIC_CODE_TYPES = frozenset(("skill", "mcp-server", "plugin", "connector", "agent"))

FABRIC_TYPES = FABRIC_DATA_TYPES | FABRIC_CODE_TYPES

FABRIC_HARNESSES = frozenset(
    (
        "*",
        "locus",
        "multiverse",
        "kortex-audio",
        "locus-evolution-lab",
        "ardynos",
        "somatic",
    )
)

CONTENT_FABRIC_INTEROP_TARGETS = frozenset(
    (
        "locus",
        "multiverse",
        "kortex-audio",
        "locus-evolution-lab",
        "somatic",
        "ardynos",
    )
)

PUBLIC_LICENSE_ALLOWLIST = frozenset(
    (
        "MIT",
        "Apache-2.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "ISC",
        "MPL-2.0",
        "LGPL-3.0-or-later",
        "GPL-2.0-or-later",
        "GPL-3.0-or-later",
        "AGPL-3.0-or-later",
        "Unlicense",
        "CC0-1.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CC-BY-NC-4.0",
        "LicenseRef-Multiverse-Open",
    )
)

TYPE_INSTALL_DIR = {
    "model": "models",
    "asset-3d": "assets",
    "asset-audio": "assets",
    "asset-video": "assets",
    "asset-image": "assets",
    "dataset": "datasets",
    "document": "documents",
    "theme": "themes",
    "skill": "skills",
    "mcp-server": "mcp",
    "plugin": "plugins",
    "connector": "connectors",
    "agent": "agents",
}

PACK_REQUIRED_FIELDS = (
    "schemaVersion",
    "id",
    "name",
    "version",
    "class",
    "type",
    "license",
    "publisher",
    "harnesses",
    "transport",
    "files",
    "createdAt",
    "signatures",
)
