# Feature Specification: Franka Panda Cube Pickup via LLM Actions

**Feature Branch**: `001-panda-cube-pickup`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description from `specs/baseline_spec.md`

## Scope

Build a complete runnable Python project that demonstrates a local PyBullet GUI simulation where a Franka Panda robot picks up a cube from a table through a text CLI that routes natural-language commands to Foundry Local (OpenAI-compatible chat completions API). The model is constrained to strict JSON-only robot actions that are validated and safely executed.

## User Scenarios & Testing

### User Story 1 - Pick Up Cube from CLI (Priority: P1)

A user starts the app, types "pick up the cube", and observes the Panda robot pick and lift the default cube in the PyBullet GUI.

**Why this priority**: This is the primary product outcome and acceptance target.

**Independent Test**: Start app via `python -m src.app`, submit the command "pick up the cube", and verify at least one successful pick-and-lift behavior.

**Acceptance Scenarios**:

1. **Given** the simulation is initialized with plane, table, Panda, and one cube, **When** the user enters "pick up the cube", **Then** the system executes validated robot actions and the cube is picked and lifted.
2. **Given** the model returns malformed or unsafe action JSON, **When** validation runs, **Then** the action is rejected and no unsafe robot motion is executed.

---

### User Story 2 - Inspect Scene Through Action Interface (Priority: P2)

A user can request scene understanding behavior through the `describe_scene()` action path.

**Why this priority**: Scene introspection supports planning robustness and recoverability.

**Independent Test**: Issue a prompt that should lead to `describe_scene()` and verify structured scene details are returned.

**Acceptance Scenarios**:

1. **Given** a running simulation, **When** the model emits `describe_scene()`, **Then** the system returns current object and robot state needed for action planning.

---

### User Story 3 - Recover and Retry Safely (Priority: P3)

A user can recover from failed attempts using `reset()` and reissue commands without restarting the process.

**Why this priority**: Improves demo reliability and operator usability.

**Independent Test**: Cause a failed plan, run reset flow, then run pickup command again successfully.

**Acceptance Scenarios**:

1. **Given** a failed or partial manipulation attempt, **When** `reset()` is executed, **Then** the simulation returns to a known default state suitable for a new pickup attempt.

## Edge Cases

- LLM output is not valid JSON.
- LLM output is valid JSON but action name is unsupported.
- Action parameters are missing required fields.
- Action parameters are numerically valid but outside safety bounds.
- Inverse kinematics returns no feasible solution.
- Motion path causes likely collision with table or singular/unstable posture.
- Gripper close action fails to secure cube.
- Cube is already grasped or moved away from expected default location.
- Foundry Local endpoint is unreachable or times out.
- User submits empty input, unrelated text, or rapid repeated commands.

## Requirements

### Functional Requirements

- **FR-001**: System MUST launch PyBullet in GUI mode.
- **FR-002**: System MUST initialize a scene containing plane, table, Franka Panda robot, and one default cube object.
- **FR-003**: System MUST provide a text-based CLI loop for user commands.
- **FR-004**: System MUST integrate with Foundry Local via OpenAI-compatible chat completions endpoint.
- **FR-005**: System MUST enforce strict JSON-only LLM action outputs and reject any non-JSON content.
- **FR-006**: System MUST support the following actions: `describe_scene()`, `move_ee(target_xyz, target_rpy, speed)`, `open_gripper(width)`, `close_gripper(force)`, `pick(object)`, `place(target_xyz)`, `reset()`.
- **FR-007**: System MUST validate every action and its parameters before execution.
- **FR-008**: System MUST execute end-effector targeting using inverse kinematics.
- **FR-009**: System MUST execute motion using smooth joint interpolation.
- **FR-010**: System MUST apply safety clamps to motion and gripper commands before execution.
- **FR-011**: System MUST be packaged with `src/` layout, `requirements.txt`, and `README.md`.
- **FR-012**: System MUST provide default entrypoint `python -m src.app`.
- **FR-013**: System MUST satisfy acceptance behavior: user enters "pick up the cube" and robot picks and lifts the cube at least once.

### Non-Functional Requirements

- **NFR-001**: Project MUST be runnable locally on a standard Python environment with documented setup steps.
- **NFR-002**: Validation failures MUST fail safely (no unsafe motion execution).
- **NFR-003**: Logging/output MUST be understandable enough for a user to diagnose command/action failures.

### Key Entities

- **SceneState**: Runtime representation of robot state, cube pose, table/plane references, and simulation metadata.
- **RobotAction**: Validated command object with action name and typed parameters.
- **SafetyPolicy**: Boundaries and constraints for Cartesian targets, orientation, speed, gripper width/force, and optional workspace limits.
- **ExecutionResult**: Structured outcome of each action execution including success/failure, message, and optional telemetry.
- **LLMResponseEnvelope**: Parsed model response payload constrained to JSON action schema.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Running `python -m src.app` starts the CLI and PyBullet GUI without manual code edits.
- **SC-002**: In a default scene, entering "pick up the cube" leads to at least one successful pick-and-lift sequence.
- **SC-003**: 100% of unsupported or malformed action outputs are rejected before robot execution.
- **SC-004**: All required actions are callable through the validated action pipeline.

## Requirements Clarity Check

### Clear and Actionable

- Use of PyBullet GUI.
- Required scene composition (plane, table, Panda, one cube).
- Presence of CLI loop.
- Foundry Local integration path (OpenAI-compatible chat completions).
- Required supported action list.
- Need for action validation, IK, interpolation, and safety clamps.
- Packaging artifacts (`src/`, `requirements.txt`, `README.md`) and entrypoint.
- Top-level acceptance behavior for pickup.

### Ambiguities and Open Questions

- **A-001 Foundry Local configuration details**: Exact base URL, model name, auth requirements, and environment variable names are not specified.
- **A-002 Action JSON schema format**: Single-action vs multi-step plan, required top-level keys, and strict typing rules are not fully specified.
- **A-003 Safety clamp thresholds**: Workspace bounds, max speed, max joint delta, gripper width/force limits, and fail behavior thresholds are unspecified.
- **A-004 Coordinate frame conventions**: Whether `target_xyz`/`target_rpy` are world-frame, end-effector frame, or mixed is unspecified.
- **A-005 Object naming for `pick(object)`**: Canonical object IDs/names (e.g., "cube", "default_cube") are not standardized.
- **A-006 Success definition detail**: "Picks and lifts" lacks precise numeric threshold (lift height, hold duration, tolerance, and retries).
- **A-007 Reset semantics**: Whether `reset()` should restore full simulation, just object poses, or both is unspecified.
- **A-008 Collision policy**: Requirement mentions safety clamps but does not explicitly require collision checking strategy.
- **A-009 CLI interaction contract**: Exit command(s), timeout behavior, and handling multi-turn conversational context are unspecified.
- **A-010 Determinism and test repeatability**: Seed control and acceptable variance for physics/LLM behavior are not defined.

## Recommended Clarifications Before Planning

1. Confirm Foundry Local endpoint contract: base URL, model identifier, API key usage, timeout, retries.
2. Approve a strict JSON schema for actions (including examples and validation rules).
3. Define safety policy bounds and default constants.
4. Define precise pickup success metrics (minimum lift height and hold duration).
5. Define `reset()` behavior and expected post-reset object/robot poses.
6. Define canonical scene object IDs and frame conventions for all Cartesian targets.
