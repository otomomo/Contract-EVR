"""Pre-call budget enforcement for provider requests."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import BudgetExceededError


@dataclass(slots=True)
class BudgetLedger:
    max_model_calls: int = 0
    max_retrieval_calls: int = 0
    max_input_tokens: int = 0
    max_output_tokens: int = 0
    model_calls: int = 0
    retrieval_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

    def reserve_model(self, *, input_tokens: int = 0, output_tokens: int = 0) -> None:
        if self.model_calls + 1 > self.max_model_calls:
            raise BudgetExceededError("model call budget exceeded")
        if self.input_tokens + input_tokens > self.max_input_tokens:
            raise BudgetExceededError("input token budget exceeded")
        if self.output_tokens + output_tokens > self.max_output_tokens:
            raise BudgetExceededError("output token budget exceeded")
        self.model_calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

    def reserve_retrieval(self) -> None:
        if self.retrieval_calls + 1 > self.max_retrieval_calls:
            raise BudgetExceededError("retrieval call budget exceeded")
        self.retrieval_calls += 1

    def snapshot(self) -> dict[str, int]:
        return {
            "model_calls": self.model_calls,
            "retrieval_calls": self.retrieval_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
        }
