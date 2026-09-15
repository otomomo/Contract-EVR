"""Project manifest loading, mode gating, and input preflight."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .audit import verify_file_refs
from .contracts import validate
from .errors import ContractValidationError


def load_manifest(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() in {".yaml", ".yml"}:
        value = yaml.safe_load(text)
    else:
        value = json.loads(text)
    if not isinstance(value, dict):
        raise ContractValidationError("project manifest must be an object")
    validate(value, "project_manifest")
    return value


def assert_mode_allowed(manifest: dict[str, Any], mode: str) -> None:
    if mode not in manifest["allowed_modes"]:
        raise ContractValidationError(f"mode not allowed by project manifest: {mode}")


def preflight(root: str | Path, manifest: dict[str, Any], mode: str) -> dict[str, Any]:
    assert_mode_allowed(manifest, mode)
    refs = list(manifest["inputs"].values())
    verified = verify_file_refs(root, refs)
    if mode != "live" and (
        manifest["budget"]["max_model_calls"] != 0
        or manifest["budget"]["max_retrieval_calls"] != 0
    ):
        raise ContractValidationError("non-live manifests must set model and retrieval calls to zero")
    return {
        "status": "passed",
        "project_id": manifest["project_id"],
        "mode": mode,
        "verified_input_count": len(verified),
        "model_calls_planned": 0,
        "retrieval_calls_planned": 0,
    }
