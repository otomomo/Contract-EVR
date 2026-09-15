# Generic Requirement Decomposition Prompt

Decompose a supplied review requirement into the smallest independently
verifiable claims without adding facts or changing its meaning.

Return structured claims with stable IDs, the required result, and the
parent-package relationship. Preserve whether claims are jointly required or
authorized alternatives. Do not copy unrelated document text into a claim.

Input placeholder:

```text
Requirement: {{requirement}}
Output schema: {{output_schema}}
```
