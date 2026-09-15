"""Provider protocols plus zero-external-call fake and replay implementations."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .canonical import sha256_value
from .errors import ProviderError


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    logical_call_id: str
    task: str
    payload: Mapping[str, Any]

    @property
    def request_hash(self) -> str:
        return sha256_value(
            {"logical_call_id": self.logical_call_id, "task": self.task, "payload": self.payload}
        )


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    request_hash: str
    payload: Mapping[str, Any]
    provider_name: str
    provider_digest: str
    external_calls: int = 0


class StructuredProvider(Protocol):
    name: str
    digest: str
    external_calls: int

    def call(self, request: ProviderRequest) -> ProviderResponse: ...


class FakeProvider:
    name = "fake"
    digest = "fake-provider-v1"
    external_calls = 0

    def __init__(self, responses_by_logical_call_id: Mapping[str, Mapping[str, Any]]) -> None:
        self._responses = dict(responses_by_logical_call_id)

    def call(self, request: ProviderRequest) -> ProviderResponse:
        if request.logical_call_id not in self._responses:
            raise ProviderError(f"missing fake response: {request.logical_call_id}")
        return ProviderResponse(
            request_hash=request.request_hash,
            payload=deepcopy(self._responses[request.logical_call_id]),
            provider_name=self.name,
            provider_digest=self.digest,
        )


class ReplayProvider:
    name = "replay"
    digest = "replay-provider-v1"
    external_calls = 0

    def __init__(self, responses_by_request_hash: Mapping[str, Mapping[str, Any]]) -> None:
        self._responses = dict(responses_by_request_hash)

    def call(self, request: ProviderRequest) -> ProviderResponse:
        if request.request_hash not in self._responses:
            raise ProviderError(f"replay cache miss: {request.request_hash}")
        return ProviderResponse(
            request_hash=request.request_hash,
            payload=deepcopy(self._responses[request.request_hash]),
            provider_name=self.name,
            provider_digest=self.digest,
        )


def validate_candidate_bound_response(
    request: ProviderRequest,
    response: ProviderResponse,
) -> None:
    if response.request_hash != request.request_hash:
        raise ProviderError("provider response request hash mismatch")
    allowed = set(request.payload.get("candidate_ids", ()))
    selected = set(response.payload.get("selected_evidence_unit_ids", ()))
    if not selected <= allowed:
        raise ProviderError(f"provider selected evidence outside candidates: {sorted(selected - allowed)}")
