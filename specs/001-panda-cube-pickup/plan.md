# Implementation Plan: Panda Cube Pickup

**Branch**: `001-panda-cube-pickup` | **Date**: 2026-03-20 | **Spec**: `specs/refined_spec.md`
**Input**: Feature specification from `specs/refined_spec.md`

## Summary

Deliver a local Python application that runs a PyBullet GUI scene (plane, table, Franka Panda, cube), accepts user commands in a CLI loop, uses Foundry Local chat completions to produce strict JSON robot actions, validates and safety-checks each action, and executes robot motion via IK and smooth interpolation until the cube is picked and lifted.

## Technical Context

**Language/Version**: Python 3.10+ (target 3.11)  
**Primary Dependencies**: `pybullet`, `numpy`, `openai`-compatible client, `pydantic` (or equivalent schema validator), `python-dotenv` (optional)  
**Storage**: In-memory runtime state; optional local logs on filesystem  
**Testing**: `pytest` with unit + integration tests  
**Target Platform**: Local Windows/Linux/macOS desktop with GUI support  
**Project Type**: Single-process CLI application with simulation loop  
**Performance Goals**: Interactive command latency suitable for manual use; smooth visual robot motion  
**Constraints**: Strict JSON-only model outputs; fail-safe validation; no cloud dependency beyond local Foundry endpoint  
**Scale/Scope**: Single robot, single cube scenario, local single-user demo

## Constitution Check

- No constitution violations identified for this feature scope.
- Plan preserves simple single-project structure and explicit safety gate before actuator commands.

## System Architecture

### Architectural Style

Layered runtime with explicit orchestration:

1. Presentation Layer: CLI input/output loop.
2. Planning Layer: Prompt builder + LLM client for action generation.
3. Validation & Safety Layer: JSON parsing, schema checks, semantic checks, clamps, deny rules.
4. Execution Layer: Action dispatcher + high-level skills (`pick`, `place`) + low-level motion primitives.
5. Simulation Layer: PyBullet world setup, robot control, scene queries, stepping.

### Core Runtime Components

- `App Orchestrator`: Owns lifecycle, initializes modules, runs command loop.
- `LLM Planner`: Sends user + scene context to Foundry Local and requests strict JSON action output.
- `Action Validator`: Enforces schema and supported action contract.
- `Safety Guard`: Applies bounds and rejects unsafe intents before execution.
- `Action Executor`: Maps validated actions to simulator operations.
- `Simulation Controller`: Manages world initialization, robot state, IK, interpolation, and object manipulation.

## Module Breakdown

Proposed source layout:

```text
src/
├── app.py                      # Entrypoint and main loop
├── config.py                   # Environment/config loading
├── cli/
│   └── repl.py                 # Text command loop and UX messaging
├── llm/
│   ├── client.py               # Foundry Local OpenAI-compatible API client
│   ├── prompts.py              # System/user prompt construction
│   └── parser.py               # Strict JSON extraction/parsing utilities
├── actions/
│   ├── schema.py               # Action schemas and enums
│   ├── validator.py            # Structural + semantic validation
│   ├── safety.py               # Clamp policies and safety checks
│   └── dispatcher.py           # Route action -> simulation method
├── sim/
│   ├── world.py                # PyBullet connection and scene setup
│   ├── robot.py                # Panda model loading and joint helpers
│   ├── kinematics.py           # IK helper and pose/joint conversions
│   ├── motion.py               # Smooth interpolation and stepping
│   ├── gripper.py              # Gripper open/close logic
│   └── tasks.py                # High-level pick/place routines
├── models/
│   ├── state.py                # SceneState and execution state models
│   └── result.py               # ExecutionResult/error models
└── utils/
    ├── logging.py              # Structured logging helpers
    └── constants.py            # Joint limits, workspace bounds, defaults

tests/
├── unit/
│   ├── test_action_validator.py
│   ├── test_safety_policy.py
│   └── test_parser.py
├── integration/
│   ├── test_cli_to_action_pipeline.py
│   └── test_pickup_succeeds.py
└── fixtures/
    └── sample_actions.json
```

## Data Flow: LLM -> Actions -> Robot

### End-to-End Sequence

1. User enters command in CLI (example: "pick up the cube").
2. App requests current scene summary from simulation (`describe_scene` data model).
3. LLM Planner builds prompt with allowed actions and strict JSON schema instructions.
4. Foundry Local returns response.
5. Parser extracts and parses JSON only.
6. Validator checks:
- supported action name
- required fields and types
- parameter ranges and enum values
7. Safety Guard applies workspace and actuator clamps; rejects unsafe actions.
8. Dispatcher routes action to execution primitive/high-level task.
9. Simulation Controller performs IK + joint interpolation + gripper commands.
10. Execution result is returned to CLI and logged.
11. Loop continues for next user command.

### Error and Recovery Flow

- Any parse/validation/safety failure returns explicit non-execution error to CLI.
- User can issue retry or `reset()` to restore baseline scene.
- Foundry endpoint failures surface as recoverable planner errors (no motion executed).

## Safety Validation Layer

### Safety Objectives

- Prevent out-of-bounds Cartesian targets.
- Prevent excessive speed/step changes.
- Prevent invalid gripper width/force commands.
- Prevent unsupported or malformed action execution.

### Validation Stages

1. **Syntax Gate**: Response must be valid JSON object/array per expected contract.
2. **Schema Gate**: Must conform to defined action schema.
3. **Semantic Gate**: Object existence checks, frame requirements, and command prerequisites.
4. **Safety Gate**: Clamp or reject based on workspace/joint/gripper limits.
5. **Execution Gate**: Only fully validated action reaches robot dispatcher.

### Initial Policy Defaults (to be confirmed)

- Workspace bounds: axis-aligned XYZ limits above table and within Panda reach.
- Speed bounds: min/max scalar for `move_ee`.
- Orientation bounds: normalized roll/pitch/yaw ranges.
- Gripper bounds: width and force min/max.
- Motion segmentation: maximum joint delta per interpolation step.

## PyBullet Simulation Structure

### Scene Initialization

- Connect in GUI mode.
- Load plane URDF.
- Load table URDF at fixed pose.
- Load Franka Panda URDF with known base pose.
- Spawn one cube at default pickup pose.
- Set gravity, simulation timestep, and camera defaults.

### Robot Control Model

- Maintain mapping of Panda arm and gripper joint indices.
- Use IK solver for end-effector targets.
- Convert IK target joints into smooth interpolated trajectory.
- Step simulation incrementally while applying joint commands.
- Use gripper helper for open/close primitives and grasp checks.

### High-Level Task Composition

- `pick(object)` decomposes into: pre-grasp approach -> open gripper -> descend -> close -> lift.
- `place(target_xyz)` decomposes into: approach -> descend -> open -> retreat.
- `reset()` restores robot and cube to default initial conditions.

## Milestones

1. Foundation
- Project skeleton, config, logging, and app lifecycle.
- PyBullet world loads correctly in GUI with required entities.

2. Motion Core
- IK + interpolation + gripper primitives operational.
- Deterministic `move_ee`, `open_gripper`, `close_gripper`, `reset` primitives.

3. LLM Action Pipeline
- Foundry Local client, prompts, strict JSON parsing.
- Validation + safety guards integrated before execution.

4. Composite Behaviors
- `pick` and `place` action implementations using primitives.
- `describe_scene` reporting and robust CLI messaging.

5. Verification & Documentation
- Unit and integration tests for parser/validator/safety/pickup.
- README with setup, Foundry configuration, and run instructions.

## Risks and Mitigations

- IK instability near singularities: add fallback waypoints and conservative bounds.
- Non-deterministic LLM outputs: enforce schema, add constrained prompting, reject on mismatch.
- Physics grasp unreliability: tune approach offsets, grip force, and settle timing.
- Endpoint downtime/timeouts: implement retry with timeout and clear user error messaging.

## Open Items Requiring Final Decisions

- Exact Foundry Local endpoint/model/auth environment variables.
- Final action JSON schema shape (single-action vs action-list).
- Numeric safety clamp constants.
- Precise pickup success metric (minimum lift height and hold duration).
- Frame convention for Cartesian targets.
