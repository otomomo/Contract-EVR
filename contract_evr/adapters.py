"""Project adapter protocol and in-memory fixture adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class ProjectDataset:
    project_id: str
    opinions: tuple[Mapping[str, Any], ...]
    packages: tuple[Mapping[str, Any], ...]
    source_units: tuple[Mapping[str, Any], ...]


class ProjectAdapter(Protocol):
    name: str
    version: str

    def load(self) -> ProjectDataset: ...


@dataclass(frozen=True, slots=True)
class FixtureAdapter:
    fixture: Mapping[str, Any]
    name: str = "fixture"
    version: str = "1"

    def load(self) -> ProjectDataset:
        project_id = str(self.fixture["project_id"])
        return ProjectDataset(
            project_id=project_id,
            opinions=tuple(self.fixture.get("opinions", ())),
            packages=tuple(self.fixture.get("packages", ())),
            source_units=tuple(self.fixture.get("source_units", ())),
        )


def require_unique_ids(records: Sequence[Mapping[str, Any]], key: str) -> None:
    values = [str(record[key]) for record in records]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {key}")
