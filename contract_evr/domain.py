"""Stable enums and small immutable domain values."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SourceRole(StrEnum):
    REVISED_PLAN_BODY = "revised_plan_body"
    REVISED_PLAN_TABLE = "revised_plan_table"
    REVISED_PLAN_FIGURE = "revised_plan_figure"
    CONTROLLED_ATTACHMENT_SUBSTANCE = "controlled_attachment_substance"
    EXPERT_REQUIREMENT = "expert_requirement"
    REVIEW_OPINION = "review_opinion"
    VERIFICATION_OR_APPROVAL = "verification_or_approval"
    RESPONSE_OR_MODIFICATION_STATEMENT = "response_or_modification_statement"
    UNKNOWN = "unknown"


class ClaimLabel(StrEnum):
    ENTAILED = "ENTAILED"
    PARTIALLY_ENTAILED = "PARTIALLY_ENTAILED"
    CONTRADICTED = "CONTRADICTED"
    NOT_FOUND = "NOT_FOUND"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNCERTAIN = "UNCERTAIN"


class PackageLabel(StrEnum):
    SUFFICIENT = "sufficient"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    CONTRADICTED = "contradicted"
    NOT_APPLICABLE = "not_applicable"
    UNCERTAIN = "uncertain"
    RETIRED = "retired_non_binding_context"


class LogicOperator(StrEnum):
    ALL_OF = "ALL_OF"
    ANY_OF = "ANY_OF"


@dataclass(frozen=True, slots=True)
class QualifiedSource:
    role: SourceRole
    eligible_as_completion_evidence: bool
    policy_reason: str
