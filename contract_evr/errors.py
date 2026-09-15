"""Typed failures used across Contract-EVR boundaries."""


class ContractEvrError(Exception):
    """Base error for expected engine failures."""


class ContractValidationError(ContractEvrError):
    """A versioned data contract was violated."""


class ProtectedArtifactError(ContractEvrError):
    """A protected historical artifact is missing or changed."""


class SourcePolicyError(ContractEvrError):
    """Evidence attempted to cross a source-qualification boundary."""


class ProviderError(ContractEvrError):
    """A provider failed or returned an invalid envelope."""


class BudgetExceededError(ContractEvrError):
    """A request would exceed the predeclared run budget."""
