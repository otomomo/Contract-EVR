"""Deterministic fixture/replay runtime with immutable materialization."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from .adapters import ProjectAdapter, require_unique_ids
from .aggregation import aggregate_claims
from .audit import materialize_immutable_json, materialize_immutable_jsonl
from .canonical import sha256_value
from .contracts import validate
from .errors import ContractValidationError, SourcePolicyError
from .providers import ProviderRequest, StructuredProvider, validate_candidate_bound_response
from .source_policy import SourcePolicy


def _claim_records(packages: tuple[Mapping[str, Any], ...]) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    pairs = []
    for package in packages:
        for claim in package["claims"]:
            pairs.append((package, claim))
    return pairs


def execute(
    *,
    adapter: ProjectAdapter,
    provider: StructuredProvider,
    source_policy: SourcePolicy,
    candidate_ids_by_claim: Mapping[str, list[str]],
    output_dir: str | Path | None = None,
    run_id: str = "fixture-run",
) -> dict[str, Any]:
    if provider.external_calls != 0:
        raise ContractValidationError("fixture/replay runtime forbids external provider calls")
    dataset = adapter.load()
    require_unique_ids(dataset.packages, "requirement_id")
    require_unique_ids(dataset.source_units, "source_unit_id")
    source_by_id = {str(unit["source_unit_id"]): unit for unit in dataset.source_units}

    judgements: list[dict[str, Any]] = []
    labels_by_requirement: dict[str, dict[str, str]] = defaultdict(dict)
    package_by_requirement = {str(package["requirement_id"]): package for package in dataset.packages}

    for package, claim in _claim_records(dataset.packages):
        claim_id = str(claim["claim_id"])
        raw_candidates = list(candidate_ids_by_claim.get(claim_id, []))
        missing = [candidate for candidate in raw_candidates if candidate not in source_by_id]
        if missing:
            raise ContractValidationError(f"unknown candidate ids for {claim_id}: {missing}")
        qualified = [
            candidate
            for candidate in raw_candidates
            if source_policy.qualify(source_by_id[candidate]).eligible_as_completion_evidence
        ]
        request = ProviderRequest(
            logical_call_id=f"claim:{claim_id}:judgement",
            task="claim_judgement",
            payload={
                "project_id": dataset.project_id,
                "claim_id": claim_id,
                "required_result": claim["required_result"],
                "candidate_ids": qualified,
            },
        )
        response = provider.call(request)
        validate_candidate_bound_response(request, response)
        payload = dict(response.payload)
        selected = list(payload.get("selected_evidence_unit_ids", []))
        for selected_id in selected:
            qualification = source_policy.qualify(source_by_id[selected_id])
            if not qualification.eligible_as_completion_evidence:
                raise SourcePolicyError(f"ineligible selected evidence: {selected_id}")
        record = {
            "schema_version": "contract_evr.record.v1",
            "record_type": "claim_judgement",
            "project_id": dataset.project_id,
            "claim_id": claim_id,
            "label": payload["label"],
            "selected_evidence_unit_ids": selected,
            "reasoning": payload["reasoning"],
            "extensions": {
                "request_hash": request.request_hash,
                "provider": response.provider_name,
                "provider_digest": response.provider_digest,
            },
        }
        validate(record, "engine_record")
        judgements.append(record)
        labels_by_requirement[str(package["requirement_id"])][claim_id] = record["label"]

    aggregations = []
    for requirement_id, claim_labels in sorted(labels_by_requirement.items()):
        package = package_by_requirement[requirement_id]
        record = {
            "schema_version": "contract_evr.record.v1",
            "record_type": "package_aggregation",
            "project_id": dataset.project_id,
            "requirement_id": requirement_id,
            "operator": package["operator"],
            "claim_labels": dict(sorted(claim_labels.items())),
            "package_label": aggregate_claims(package["operator"], claim_labels).value,
        }
        validate(record, "engine_record")
        aggregations.append(record)

    result: dict[str, Any] = {
        "run_id": run_id,
        "status": "passed",
        "mode": provider.name,
        "project_id": dataset.project_id,
        "counts": {
            "opinions": len(dataset.opinions),
            "packages": len(dataset.packages),
            "claims": len(judgements),
            "source_units": len(dataset.source_units),
        },
        "execution_counters": {"model_calls": 0, "retrieval_calls": 0},
        "claim_judgements": judgements,
        "package_aggregations": aggregations,
    }
    result["canonical_result_sha256"] = sha256_value(result)

    if output_dir is not None:
        target = Path(output_dir)
        claim_hash = materialize_immutable_jsonl(target / "claim_judgements.jsonl", judgements)
        package_hash = materialize_immutable_jsonl(target / "package_aggregations.jsonl", aggregations)
        run_manifest = {key: value for key, value in result.items() if key not in {"claim_judgements", "package_aggregations"}}
        run_manifest["outputs"] = {
            "claim_judgements.jsonl": claim_hash,
            "package_aggregations.jsonl": package_hash,
        }
        materialize_immutable_json(target / "run_manifest.json", run_manifest)
    return result
