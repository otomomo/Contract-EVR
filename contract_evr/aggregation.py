"""Deterministic claim-to-package aggregation and immutable overlays."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .canonical import sha256_value
from .domain import ClaimLabel, LogicOperator, PackageLabel
from .errors import ContractValidationError


def _labels(values: Mapping[str, str | ClaimLabel]) -> dict[str, ClaimLabel]:
    if not values:
        raise ContractValidationError("claim_labels cannot be empty")
    try:
        return {key: ClaimLabel(value) for key, value in values.items()}
    except ValueError as exc:
        raise ContractValidationError(f"unknown claim label: {exc}") from exc


def aggregate_claims(
    operator: str | LogicOperator,
    claim_labels: Mapping[str, str | ClaimLabel],
) -> PackageLabel:
    """Aggregate labels with NOT_APPLICABLE removed before truth evaluation."""

    op = LogicOperator(operator)
    labels = list(_labels(claim_labels).values())
    active = [label for label in labels if label is not ClaimLabel.NOT_APPLICABLE]
    if not active:
        return PackageLabel.NOT_APPLICABLE

    if op is LogicOperator.ALL_OF:
        if ClaimLabel.CONTRADICTED in active:
            return PackageLabel.CONTRADICTED
        if ClaimLabel.UNCERTAIN in active:
            return PackageLabel.UNCERTAIN
        if all(label is ClaimLabel.ENTAILED for label in active):
            return PackageLabel.SUFFICIENT
        if all(label is ClaimLabel.NOT_FOUND for label in active):
            return PackageLabel.INSUFFICIENT
        return PackageLabel.PARTIAL

    if ClaimLabel.ENTAILED in active:
        return PackageLabel.SUFFICIENT
    if ClaimLabel.PARTIALLY_ENTAILED in active:
        return PackageLabel.PARTIAL
    if ClaimLabel.UNCERTAIN in active:
        return PackageLabel.UNCERTAIN
    if all(label is ClaimLabel.CONTRADICTED for label in active):
        return PackageLabel.CONTRADICTED
    return PackageLabel.INSUFFICIENT


def build_tombstone(
    *,
    project_id: str,
    opinion_id: str,
    requirement_id: str,
    retired_claim_ids: list[str],
    reason: str,
    source_contract_id: str,
) -> dict[str, Any]:
    if not retired_claim_ids:
        raise ContractValidationError("a tombstone must retire at least one claim")
    return {
        "schema_version": "contract_evr.record.v1",
        "record_type": "retired_tombstone",
        "project_id": project_id,
        "opinion_id": opinion_id,
        "requirement_id": requirement_id,
        "retired_claim_ids": sorted(set(retired_claim_ids)),
        "reason": reason,
        "source_contract_id": source_contract_id,
    }


def apply_override(
    original: Mapping[str, Any],
    envelope: Mapping[str, Any],
    *,
    allowed_fields: frozenset[str],
) -> dict[str, Any]:
    if sha256_value(original) != envelope.get("old_value_hash"):
        raise ContractValidationError("override predecessor hash mismatch")
    changes = envelope.get("field_changes")
    if not isinstance(changes, Mapping) or not changes:
        raise ContractValidationError("override field_changes must be non-empty")
    unknown = set(changes) - set(allowed_fields)
    if unknown:
        raise ContractValidationError(f"override attempted unauthorized fields: {sorted(unknown)}")
    result = deepcopy(dict(original))
    result.update(changes)
    return result
