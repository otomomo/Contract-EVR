"""Deterministic source-role classification and qualification."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .domain import QualifiedSource, SourceRole


@dataclass(frozen=True, slots=True)
class SourcePolicy:
    version: str = "contract_evr.source_policy.v1"
    controlled_attachment_allowlist: frozenset[str] = frozenset()

    _review_markers = (
        "评审意见书",
        "评审意见",
        "审查意见",
        "核查意见",
        "核实意见",
        "专家意见",
    )
    _approval_markers = ("批复", "审批意见", "验收意见", "备案证明")
    _response_markers = (
        "评审意见回复",
        "意见回复表",
        "修改说明",
        "专家修改意见",
        "专家修改说明",
        "回复说明",
    )

    @staticmethod
    def _path_text(unit: Mapping[str, Any]) -> str:
        path = unit.get("section_path", [])
        if isinstance(path, str):
            path = [path]
        title = unit.get("document_title", "")
        return " / ".join([str(title), *(str(part) for part in path)]).strip(" / ")

    @staticmethod
    def _explicit_role(unit: Mapping[str, Any]) -> SourceRole | None:
        value = unit.get("source_role")
        if value is None:
            return None
        try:
            return SourceRole(str(value))
        except ValueError:
            return SourceRole.UNKNOWN

    def classify(self, unit: Mapping[str, Any]) -> SourceRole:
        """Classify role with disqualifying context taking precedence."""

        path_text = self._path_text(unit)
        if any(marker in path_text for marker in self._response_markers):
            return SourceRole.RESPONSE_OR_MODIFICATION_STATEMENT
        if any(marker in path_text for marker in self._review_markers):
            return SourceRole.REVIEW_OPINION
        if any(marker in path_text for marker in self._approval_markers):
            return SourceRole.VERIFICATION_OR_APPROVAL

        explicit = self._explicit_role(unit)
        if explicit is not None and explicit is not SourceRole.UNKNOWN:
            return explicit

        modality = str(unit.get("modality", unit.get("content_type", ""))).lower()
        document_role = str(unit.get("document_role", "")).lower()
        attachment_id = str(unit.get("attachment_id", ""))
        if attachment_id and attachment_id in self.controlled_attachment_allowlist:
            return SourceRole.CONTROLLED_ATTACHMENT_SUBSTANCE
        if document_role in {"revised_plan", "current_plan"}:
            if modality in {"table", "table_cell"}:
                return SourceRole.REVISED_PLAN_TABLE
            if modality in {"figure", "image", "diagram"}:
                return SourceRole.REVISED_PLAN_FIGURE
            return SourceRole.REVISED_PLAN_BODY
        return explicit or SourceRole.UNKNOWN

    def qualify(self, unit: Mapping[str, Any]) -> QualifiedSource:
        role = self.classify(unit)
        eligible = role in {
            SourceRole.REVISED_PLAN_BODY,
            SourceRole.REVISED_PLAN_TABLE,
            SourceRole.REVISED_PLAN_FIGURE,
            SourceRole.CONTROLLED_ATTACHMENT_SUBSTANCE,
        }
        reason = (
            "role_is_eligible_plan_substance"
            if eligible
            else f"role_is_context_or_unqualified:{role.value}"
        )
        return QualifiedSource(role, eligible, reason)

    def filter_eligible(self, units: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        return [unit for unit in units if self.qualify(unit).eligible_as_completion_evidence]
