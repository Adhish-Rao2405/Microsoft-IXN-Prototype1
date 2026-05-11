# Prototype 1 - Local Model-to-Action Feasibility

## Purpose

Prototype 1 is the first feasibility layer of the UCL Microsoft IXN Foundry Local dissertation project. It tests whether a local model can be connected to a task-planning workflow and produce action-like outputs that can be interpreted as early planning proposals.

Prototype 1 is deliberately limited in scope. It does not attempt to prove safety, semantic correctness, execution validity, cloud comparison, quantisation behaviour or resource efficiency. Its role is to establish whether local model-to-action generation is feasible enough to motivate later deterministic validation and benchmark evaluation.

## Research Question

Can local LLM/SLM inference produce action-like task-planning outputs that justify building a deterministic validation pipeline?

## Role in the Prototype Sequence

| Prototype | Role |
|---|---|
| Prototype 1 | Establishes local model-to-action feasibility |
| Prototype 2 / 2.1 | Adds deterministic schema validation, safety gating and reject-before-execution logic |
| Prototype 3 | Evaluates local model behaviour using a fixed benchmark |
| Prototype 4 | Adds execution-grounded safety and safety-latency evidence |
| Prototype 5 | Consolidates final evidence and closes the Microsoft IXN brief |

## Engineering Significance

Prototype 1 provides the minimum viable link between local inference and task-planning behaviour. It establishes whether a local model can generate outputs that resemble action plans rather than only free-form text. This is an engineering prerequisite for the rest of the system because a validation pipeline is only meaningful if there is a model-generated planning proposal to validate.

The prototype therefore provides the engineering reason to build Prototype 2. Once local outputs can be action-like, the next system requirement is to prevent those outputs from being treated as executable by default.

## Academic Significance

Prototype 1 motivates the zero-trust framing used later in the dissertation. If local models can generate action-like outputs, those outputs must be treated as untrusted proposals rather than as authoritative commands. The local model is treated as a proposal generator, not an execution authority.

The research problem is therefore not generation alone. The next research problem is safe validation, rejection and evidence collection around model-generated proposals.

## Inputs

- User task command.
- Local model prompt or planning prompt.
- Local model / Foundry-compatible model interface.
- Initial action representation or action-like output format.

## Outputs

- Initial model-generated action-like responses.
- Feasibility evidence.
- Early observations about structure and limitations.
- Basis for deterministic validation in Prototype 2.

## What Prototype 1 Does Not Claim

- Safe output.
- Semantic correctness.
- Schema validity under the final action schema.
- Execution eligibility.
- Local superiority over cloud.
- Production readiness.
- Resource benchmarking.
- Quantisation/model-size trade-off evaluation.

## Limitations

1. Prototype 1 is a feasibility prototype only.
2. It does not include the final deterministic safety gate.
3. It does not provide benchmark-level evaluation.
4. It does not compare local and cloud inference.
5. It does not include live CPU/GPU/NPU profiling.
6. It does not support statistical generalisation.
7. It does not establish production robot control.

## Downstream Link

Prototype 2 builds directly on Prototype 1 by introducing deterministic validation. Prototype 1 shows that local model outputs can be connected to an action-like workflow; Prototype 2 then asks how those outputs should be constrained before they can influence execution.

Prototype 3 later introduces benchmark evaluation. It moves from a feasibility question to a repeatable measurement question by evaluating model behaviour across a controlled command set.

Prototype 1 asks whether local model-to-action generation is possible. Prototype 2 asks how such outputs can be constrained before execution. Prototype 3 asks how reliably the local model behaves under a controlled benchmark.
