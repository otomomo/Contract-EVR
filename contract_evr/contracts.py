"""Versioned JSON Schema loading and strict validation."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .errors import ContractValidationError

SCHEMA_DIR = Path(__file__).with_name("schemas")


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{name}.schema.json"
    if not path.is_file():
        raise ContractValidationError(f"unknown schema: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate(value: Any, schema_name: str) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.path))
    if errors:
        details = []
        for error in errors[:10]:
            location = ".".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{location}: {error.message}")
        raise ContractValidationError("; ".join(details))


def read_and_validate(path: str | Path, schema_name: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(value, schema_name)
    return value
