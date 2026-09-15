"""Project-independent deterministic identifier helpers."""

from __future__ import annotations

import re

from .canonical import sha256_value

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def normalize_namespace(value: str) -> str:
    normalized = _SAFE.sub("-", value.strip()).strip("-._")
    if not normalized:
        raise ValueError("namespace cannot be empty")
    return normalized


def stable_id(namespace: str, record_type: str, source_identity: object, length: int = 16) -> str:
    if length < 12 or length > 64:
        raise ValueError("length must be between 12 and 64")
    prefix = normalize_namespace(namespace)
    kind = normalize_namespace(record_type).upper()
    digest = sha256_value({"namespace": prefix, "record_type": kind, "source_identity": source_identity})
    return f"{prefix}_{kind}_{digest[:length]}"
