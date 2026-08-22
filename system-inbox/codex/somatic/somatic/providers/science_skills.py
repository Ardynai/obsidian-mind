from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class SkillLookupRequest:
    task: str
    organism: str | None = None
    modality: str | None = None
    tags: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ScienceSkillRecord:
    id: str
    name: str
    description: str
    input_requirements: tuple[str, ...] = ()
    output_artifacts: tuple[str, ...] = ()
    safety_notes: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class DatabaseConnectorRecord:
    id: str
    name: str
    description: str
    source_skill_id: str
    domains: tuple[str, ...] = ()
    auth_notes: tuple[str, ...] = ()
    safety_notes: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


class ScienceSkillProvider(Protocol):
    provider_id: str
    offline_supported: bool

    def lookup(self, request: SkillLookupRequest) -> list[ScienceSkillRecord]:
        """Find Somatic-compatible skills without executing external tools."""
        ...

    def describe(self, skill_id: str) -> ScienceSkillRecord:
        """Return static skill metadata for planning and review."""
        ...
