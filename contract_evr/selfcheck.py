"""Installed-package self-check with no project data or external calls."""

from __future__ import annotations

from .adapters import FixtureAdapter
from .aggregation import aggregate_claims, build_tombstone
from .contracts import validate
from .domain import PackageLabel, SourceRole
from .providers import FakeProvider
from .runtime import execute
from .source_policy import SourcePolicy


def run_self_check() -> dict[str, object]:
    policy = SourcePolicy()
    body = {
        "source_unit_id": "demo-body",
        "document_role": "revised_plan",
        "section_path": ["Chapter"],
        "content_type": "text",
    }
    review = {
        "source_unit_id": "demo-review",
        "document_role": "revised_plan",
        "section_path": ["评审意见书"],
        "content_type": "text",
    }
    fixture = {
        "project_id": "self-check",
        "opinions": [{"opinion_id": "op-1"}],
        "packages": [
            {
                "requirement_id": "rq-1",
                "operator": "ALL_OF",
                "claims": [{"claim_id": "c-1", "required_result": "demo"}],
            }
        ],
        "source_units": [body, review],
    }
    provider = FakeProvider(
        {
            "claim:c-1:judgement": {
                "label": "ENTAILED",
                "selected_evidence_unit_ids": ["demo-body"],
                "reasoning": "installed-package self-check",
            }
        }
    )
    result = execute(
        adapter=FixtureAdapter(fixture),
        provider=provider,
        source_policy=policy,
        candidate_ids_by_claim={"c-1": ["demo-body", "demo-review"]},
        run_id="installed-package-self-check",
    )
    tombstone = build_tombstone(
        project_id="self-check",
        opinion_id="op-2",
        requirement_id="rq-2",
        retired_claim_ids=["c-2"],
        reason="non-binding fixture",
        source_contract_id="fixture-contract",
    )
    validate(tombstone, "engine_record")
    checks = {
        "body_source_eligible": policy.qualify(body).eligible_as_completion_evidence,
        "review_source_denied": policy.qualify(review).role is SourceRole.REVIEW_OPINION
        and not policy.qualify(review).eligible_as_completion_evidence,
        "fixture_runtime_passed": result["status"] == "passed",
        "fixture_package_sufficient": result["package_aggregations"][0]["package_label"]
        == PackageLabel.SUFFICIENT.value,
        "all_of_truth_table": aggregate_claims(
            "ALL_OF", {"a": "ENTAILED", "b": "NOT_FOUND"}
        )
        is PackageLabel.PARTIAL,
        "model_calls_zero": result["execution_counters"]["model_calls"] == 0,
        "retrieval_calls_zero": result["execution_counters"]["retrieval_calls"] == 0,
        "strict_tombstone_schema": True,
    }
    return {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
    }
