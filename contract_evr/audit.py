"""Protected artifact checks and immutable run materialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .canonical import canonical_json, sha256_file
from .errors import ProtectedArtifactError


def verify_file_refs(root: str | Path, refs: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    base = Path(root).resolve()
    verified: list[dict[str, str]] = []
    errors: list[str] = []
    for ref in refs:
        relative = str(ref["path"])
        path = (base / relative).resolve()
        try:
            path.relative_to(base)
        except ValueError:
            errors.append(f"outside_root:{relative}")
            continue
        if not path.is_file():
            errors.append(f"missing:{relative}")
            continue
        actual = sha256_file(path)
        expected = str(ref["sha256"])
        if actual != expected:
            errors.append(f"hash_mismatch:{relative}:{actual}")
            continue
        verified.append({"path": relative, "sha256": actual})
    if errors:
        raise ProtectedArtifactError("; ".join(errors))
    return verified


def verify_baseline_manifest(root: str | Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    groups = ("inputs", "historical_outputs", "protected_files")
    verified = []
    for group in groups:
        verified.extend(verify_file_refs(root, manifest.get(group, [])))
    return {"status": "passed", "verified_file_count": len(verified), "files": verified}


def materialize_immutable_json(path: str | Path, value: Any) -> str:
    target = Path(path)
    if target.exists():
        raise FileExistsError(f"immutable output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    target.write_text(text, encoding="utf-8")
    return sha256_file(target)


def materialize_immutable_jsonl(path: str | Path, values: Iterable[Any]) -> str:
    target = Path(path)
    if target.exists():
        raise FileExistsError(f"immutable output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [canonical_json(value) for value in values]
    target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return sha256_file(target)
