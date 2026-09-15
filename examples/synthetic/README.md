# Synthetic end-to-end example

This example was authored from scratch for the public release. It is not
copied, translated, anonymized, or derived from any project document,
expert opinion, evidence record, or experiment output.

The fixture contains one fictional review requirement with two jointly
required claims. One source unit is eligible evidence and one is explicitly
marked as review context. The fake provider selects only the eligible unit.
The runtime filters candidates, validates the structured response, and
deterministically aggregates both claim judgements into a package result.
`input.schema.json` and `output.schema.json` define and validate the complete
fixture and runtime-output shapes.

Run it from the repository root:

```bash
python examples/synthetic/run_synthetic.py
```
