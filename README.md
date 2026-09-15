# Contract-EVR

Contract-EVR: A Knowledge-Constrained Intelligent Information System for
Long-Document Review Verification Using Resource-Constrained Local LLMs

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

## Architecture / Workflow

An adapter supplies structured opinions, requirement packages, claims, and
candidate source units. The source policy filters candidate evidence before a
provider is called. A provider returns a bounded structured judgement, whose
selected evidence IDs are checked against the candidate set. Deterministic
aggregation then produces package-level results. The runtime can materialize
immutable JSON/JSONL records with hashes for later inspection.

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
configs/example_config.yaml
                          Safe configuration example
examples/synthetic/       Fully synthetic end-to-end demonstration
prompts/                  Clean generic prompt templates
```

## Quick Start

Run the zero-external-call synthetic demonstration from the repository root:

```bash
python examples/synthetic/run_synthetic.py
```

The command reads `examples/synthetic/input.json`, uses the included fake
provider, validates the structured records against the public schema, compares
the result with `expected_output.json`, and writes a local `output.json`.

## Input and Output

The synthetic input contains an opinion, one requirement package with claims,
candidate source-unit IDs, and deterministic fake-provider responses. The
output contains claim judgements, package aggregations, execution counters, and
a canonical result hash. Candidate IDs selected by a provider must be drawn
from the policy-approved candidate set.

## Models

The public demonstration does not call a model or access a network. Production
deployments may implement the `StructuredProvider` protocol with a local LLM,
while preserving the same bounded structured response contract.

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
