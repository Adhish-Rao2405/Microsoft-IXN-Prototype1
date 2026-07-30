# Prototype 1 Input/Output Contract

## Prototype Name

Prototype 1 - Local Model-to-Action Feasibility

## Prototype Type

Feasibility prototype.

## Primary Purpose

To establish whether a local model can generate action-like outputs that can later be passed into deterministic validation and benchmark evaluation stages.

## Input Contract

| Input | Description | Required for |
|---|---|---|
| User command | A natural-language task instruction or planning request | Establishing model-to-action behaviour |
| Prompt template | The text structure used to guide the model toward an action-like response | Controlling model response shape |
| Local model interface | The local inference interface available at this stage | Running the feasibility test |
| Action representation | The early representation used to interpret the model response as action-like | Connecting output to later validation |

## Output Contract

| Output | Description | Downstream relevance |
|---|---|---|
| Raw model response | Direct output returned by the local model | Shows native model behaviour |
| Action-like response | Interpreted or extracted action-style content | Motivates formal schema design |
| Feasibility observation | Evidence that local model-to-action behaviour is possible | Justifies Prototype 2 |
| Downstream requirement | Need for validation, schema constraints and safety gates | Drives zero-trust architecture |

## Validation Status

Prototype 1 does not contain the final validation stack. It does not provide final schema validation, semantic validation, deterministic safety validation or execution eligibility. Any action-like output should therefore be interpreted as a planning proposal rather than as a validated command.

## Downstream Consumer

Prototype 2 consumes the feasibility conclusion and introduces deterministic validation. It turns the feasibility result into an architectural requirement: model output must be checked before it is considered execution-eligible.

Prototype 3 later evaluates local model outputs using a controlled benchmark. It uses the validation concepts developed after Prototype 1 to separate model response generation from parse success, schema validity, safety status and execution-related outcomes.

## Claim Boundary

Supported claim:

"Local model-to-action generation was feasible enough to justify building a deterministic validation architecture."

Unsupported claims:

- Output safety.
- Semantic correctness.
- Execution readiness.
- Production readiness.
- Local-vs-cloud superiority.
