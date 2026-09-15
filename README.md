# Contract-EVR

Contract-EVR is a knowledge-constrained evidence-verification runtime for
long-document review workflows under resource-constrained local LLM
deployment. The public-safe portion of this repository contains the generic
contracts, validation, evidence admissibility, deterministic aggregation,
budget, audit, and release components.

## Scope

The runtime separates four responsibilities:

1. controlled access to candidate evidence;
2. source-admissibility checks;
3. bounded local semantic verification; and
4. deterministic aggregation into inspectable review records.

The repository does not include raw documents, expert opinions, project
records, OCR/MinerU output, evidence snippets, model requests or responses,
experiment results, model weights, or paper-generation artifacts.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Repository layout

```text
contract_evr/             Generic data structures and validation utilities
contract_evr/schemas/     Public schema definitions
```

Project-specific adapters and all source-derived data must be supplied by a
private deployment outside this repository. Any example data used with the
runtime must be fully synthetic and independently authored.

## Privacy

Raw documents and project-derived data are intentionally excluded because of
data confidentiality. Do not commit files merely because they have a code,
JSON, CSV, Markdown, or text extension: inspect their contents and provenance
first. Keep credentials in the local environment or credential manager, never
in source files.

## Citation

Citation information will be added when the associated paper has an approved
public bibliographic record.
