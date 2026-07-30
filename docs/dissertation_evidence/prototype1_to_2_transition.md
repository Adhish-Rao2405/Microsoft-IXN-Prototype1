# Transition from Prototype 1 to Prototype 2

## Summary

Prototype 1 established that local model-to-action generation was feasible. However, feasibility introduced a new problem: action-like outputs from a model cannot be trusted as executable actions.

## Problem Exposed by Prototype 1

A local model may produce an action-like response that appears useful but may still be:

- Syntactically malformed.
- Outside an expected schema.
- Semantically misaligned.
- Unsafe.
- Ambiguous.
- Unsuitable for execution.

## Design Consequence

The system needs deterministic validation between model output and execution eligibility. The model should generate proposals, but a deterministic layer should decide whether those proposals satisfy the required structure, meaning and safety constraints.

## Prototype 2 Response

Prototype 2 introduces:

- Formal schema validation.
- Safety gating.
- Reject-before-execution logic.
- Deterministic separation between model output and execution eligibility.

## Dissertation Interpretation

Prototype 1 and Prototype 2 should be presented together as the foundation phase, but not merged into one prototype.

"Prototype 1 and Prototype 2 form the foundation phase of the system. Prototype 1 establishes feasibility of local model-to-action generation, while Prototype 2 addresses the safety problem created by that feasibility by introducing deterministic validation and reject-before-execution logic."

## Why They Should Remain Separate

They answer different engineering questions. Prototype 1 asks whether local model-to-action generation is possible. Prototype 2 asks how that output can be constrained before execution.

Keeping them separate makes the dissertation sequence clearer: first establish that local generation is possible, then introduce the zero-trust architecture required to make generated proposals governable.

## Link to Prototype 3

Prototype 3 then evaluates model behaviour against a fixed benchmark using the validation concepts introduced by Prototype 2. This moves the work from feasibility and architecture into repeatable evaluation.
