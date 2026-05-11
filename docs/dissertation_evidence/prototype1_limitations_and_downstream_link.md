# Prototype 1 Limitations and Downstream Link

## Why This Document Exists

This document records the claim boundary for Prototype 1 and prevents the feasibility result from being overstated in the dissertation. Prototype 1 is useful because it establishes a feasibility premise, but it is not a complete safety, evaluation or deployment result.

## Limitation Summary Table

| Area | Prototype 1 Status |
|---|---|
| Local model-to-action feasibility | Addressed |
| Deterministic schema validation | Not yet addressed |
| Deterministic safety gating | Not yet addressed |
| Benchmark-level evaluation | Not yet addressed |
| Local-vs-cloud comparison | Not yet addressed |
| Quantisation/model-family evidence | Not yet addressed |
| Live resource profiling | Not yet addressed |
| Execution-grounded safety evidence | Not yet addressed |
| Production robot deployment | Not addressed |

## Why the Limitations Matter

These limitations are not a failure of Prototype 1. They define its role in the wider research sequence. The prototype answers an early feasibility question: whether local model outputs can be connected to an action-like task-planning workflow. That answer is necessary before later prototypes can test validation, safety, benchmarking, model comparison or resource behaviour.

The limitations also prevent unsupported dissertation claims. Prototype 1 should be cited as evidence for feasibility, not as evidence for safety, correctness, deployment readiness or comparative performance.

## Transition to Prototype 2

Prototype 1 shows that local model outputs can be action-like. This creates a safety and validity problem because an action-like response may appear useful while still being malformed, ambiguous, semantically wrong or unsafe.

Prototype 2 responds by adding deterministic validation, schema constraints and reject-before-execution logic. It changes the system interpretation of model output: generated content becomes a proposal that must pass deterministic checks before it can be considered for execution.

## Transition to Prototype 3

Prototype 1 does not evaluate behaviour across a benchmark. It does not establish how often a model responds, parses correctly, emits valid JSON, satisfies a schema or passes safety checks.

Prototype 3 later introduces the 30-command benchmark and separates request success, parse success, JSON validity, schema validity and safety outcomes. This makes the model behaviour measurable rather than only feasible.

## Dissertation Wording

"Prototype 1 established local model-to-action feasibility. It showed that local model outputs could be connected to an action-like task-planning workflow, but it did not claim safety, semantic correctness or execution eligibility. This limitation was intentional: the purpose of Prototype 1 was to justify the later development of deterministic validation in Prototype 2 and structured benchmark evaluation in Prototype 3."
