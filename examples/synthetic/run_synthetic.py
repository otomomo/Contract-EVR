from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

# Make the documented direct-execution command work without installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from contract_evr.contracts import validate
from contract_evr.runtime import execute
from contract_evr.source_policy import SourcePolicy
from contract_evr.adapters import FixtureAdapter
from contract_evr.providers import FakeProvider


def run(input_path: Path, expected_path: Path, output_path: Path) -> dict[str, Any]:
    fixture = json.loads(input_path.read_text(encoding="utf-8"))
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    fixture_schema = json.loads(
        (input_path.parent / "input.schema.json").read_text(encoding="utf-8")
    )
    output_schema = json.loads(
        (input_path.parent / "output.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(fixture_schema).validate(fixture)
    result = execute(
        adapter=FixtureAdapter(fixture),
        provider=FakeProvider(fixture["provider_responses"]),
        source_policy=SourcePolicy(),
        candidate_ids_by_claim=fixture["candidate_ids_by_claim"],
        run_id="synthetic-demo-run",
    )
    for record in result["claim_judgements"] + result["package_aggregations"]:
        validate(record, "engine_record")
    Draft202012Validator(output_schema).validate(result)
    summary = {
        "status": result["status"],
        "mode": result["mode"],
        "project_id": result["project_id"],
        "counts": result["counts"],
        "claim_labels": {
            record["claim_id"]: record["label"]
            for record in result["claim_judgements"]
        },
        "package_labels": {
            record["requirement_id"]: record["package_label"]
            for record in result["package_aggregations"]
        },
        "execution_counters": result["execution_counters"],
    }
    if summary != expected:
        raise AssertionError({"expected": expected, "actual": summary})
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public synthetic Contract-EVR demo")
    root = Path(__file__).resolve().parent
    parser.add_argument("--input", type=Path, default=root / "input.json")
    parser.add_argument("--expected", type=Path, default=root / "expected_output.json")
    parser.add_argument("--output", type=Path, default=root / "output.json")
    args = parser.parse_args()
    summary = run(args.input, args.expected, args.output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
