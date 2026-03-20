# Tasks: Panda Cube Pickup

**Input**: Design docs from `specs/001-panda-cube-pickup/`  
**Prerequisites**: `plan.md`, `../refined_spec.md`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: US1, US2, US3, or Foundation
- Every task includes a concrete file/module target and a testable completion check.

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 [Foundation] Create package skeleton and module folders in `src/__init__.py`, `src/cli/__init__.py`, `src/llm/__init__.py`, `src/actions/__init__.py`, `src/sim/__init__.py`, `src/models/__init__.py`, `src/utils/__init__.py`.
  - Testable check: `python -c "import src, src.cli, src.llm, src.actions, src.sim, src.models, src.utils"` succeeds.

- [ ] T002 [P] [Foundation] Add dependencies in `requirements.txt` (`pybullet`, `numpy`, `openai`, `pydantic`, `pytest`, `python-dotenv`).
  - Testable check: `pip install -r requirements.txt` completes in a clean venv.

- [ ] T003 [P] [Foundation] Add environment/config template and loader contract in `README.md` and `src/config.py`.
  - Testable check: unit test for missing/invalid config passes in `tests/unit/test_config.py`.

- [ ] T004 [P] [Foundation] Add logging bootstrap in `src/utils/logging.py`.
  - Testable check: unit test verifies logger creation and level settings in `tests/unit/test_logging.py`.

- [ ] T005 [Foundation] Create main entrypoint shell in `src/app.py` wired to config + CLI bootstrap.
  - Testable check: `python -m src.app --help` (or startup path) exits cleanly without traceback.

## Phase 2: Foundational Runtime (Blocks User Stories)

- [ ] T006 [P] [Foundation] Define constants for workspace, speed, gripper, interpolation limits in `src/utils/constants.py`.
  - Testable check: unit test asserts expected bounds shape/types in `tests/unit/test_constants.py`.

- [ ] T007 [P] [Foundation] Define runtime models `SceneState` and related state objects in `src/models/state.py`.
  - Testable check: unit test validates model construction/serialization in `tests/unit/test_state_models.py`.

- [ ] T008 [P] [Foundation] Define `ExecutionResult` and error result models in `src/models/result.py`.
  - Testable check: unit test verifies success/error payload invariants in `tests/unit/test_result_models.py`.

- [ ] T009 [Foundation] Implement PyBullet connection and world bootstrapping (plane/table/Panda/cube) in `src/sim/world.py`.
  - Testable check: integration test confirms object IDs exist after init in `tests/integration/test_world_bootstrap.py`.

- [ ] T010 [Foundation] Implement Panda joint index mapping and reset helpers in `src/sim/robot.py`.
  - Testable check: integration test confirms controlled joint list is non-empty in `tests/integration/test_robot_model.py`.

- [ ] T011 [Foundation] Implement IK utility for EE target to joint goals in `src/sim/kinematics.py`.
  - Testable check: integration test validates IK returns finite joint targets for reachable pose in `tests/integration/test_ik.py`.

- [ ] T012 [Foundation] Implement smooth joint interpolation executor in `src/sim/motion.py`.
  - Testable check: unit test validates interpolation step limits and monotonic convergence in `tests/unit/test_motion_interp.py`.

- [ ] T013 [Foundation] Implement gripper primitives (open/close) in `src/sim/gripper.py`.
  - Testable check: integration test verifies commanded width/force boundaries in `tests/integration/test_gripper.py`.

- [ ] T014 [Foundation] Implement high-level manipulation skeleton (`pick`, `place`, `reset`) in `src/sim/tasks.py`.
  - Testable check: integration test confirms reset restores default cube pose in `tests/integration/test_reset_behavior.py`.

- [ ] T015 [Foundation] Define action schemas/enums for all required actions in `src/actions/schema.py`.
  - Testable check: unit test validates all required action names are present in `tests/unit/test_action_schema.py`.

- [ ] T016 [Foundation] Implement strict JSON parser/extractor in `src/llm/parser.py`.
  - Testable check: parser unit tests pass for valid JSON and reject non-JSON text in `tests/unit/test_parser.py`.

- [ ] T017 [Foundation] Implement structural + semantic validation in `src/actions/validator.py`.
  - Testable check: unit tests cover missing fields, wrong types, unknown action in `tests/unit/test_action_validator.py`.

- [ ] T018 [Foundation] Implement safety policy clamps/rejections in `src/actions/safety.py`.
  - Testable check: unit tests verify out-of-bounds targets are clamped/rejected in `tests/unit/test_safety_policy.py`.

- [ ] T019 [Foundation] Implement action dispatch layer to sim operations in `src/actions/dispatcher.py`.
  - Testable check: unit test with mocks confirms each action routes to correct function in `tests/unit/test_dispatcher.py`.

- [ ] T020 [Foundation] Implement Foundry Local client wrapper in `src/llm/client.py`.
  - Testable check: unit test with mocked HTTP/client verifies request payload and timeout handling in `tests/unit/test_llm_client.py`.

- [ ] T021 [Foundation] Implement prompt builder with allowed-action contract in `src/llm/prompts.py`.
  - Testable check: unit test confirms prompt includes all required actions and JSON-only constraint in `tests/unit/test_prompts.py`.

- [ ] T022 [Foundation] Implement CLI REPL loop skeleton and command handling in `src/cli/repl.py`.
  - Testable check: integration test drives one command and one quit path in `tests/integration/test_cli_loop.py`.

**Checkpoint**: Foundation complete. User stories can be built/tested independently.

## Phase 3: User Story 1 - Pick Up Cube from CLI (P1)

**Goal**: User types "pick up the cube" and robot successfully picks/lifts at least once.

**Independent test**: Run app and verify pickup pipeline executes end-to-end.

- [ ] T023 [US1] Wire app orchestration loop in `src/app.py` (scene snapshot -> prompt -> LLM -> parse -> validate -> safety -> dispatch).
  - Testable check: integration test validates full pipeline with mocked LLM in `tests/integration/test_cli_to_action_pipeline.py`.

- [ ] T024 [P] [US1] Implement `describe_scene()` payload from simulation state in `src/sim/world.py`.
  - Testable check: integration test asserts cube/table/robot metadata in `tests/integration/test_describe_scene.py`.

- [ ] T025 [US1] Complete `move_ee` execution path using IK + interpolation in `src/actions/dispatcher.py` and `src/sim/motion.py`.
  - Testable check: integration test confirms EE reaches near-target tolerance in `tests/integration/test_move_ee.py`.

- [ ] T026 [US1] Complete `pick(object)` decomposition and grasp-lift sequence in `src/sim/tasks.py`.
  - Testable check: integration test verifies cube Z increases above lift threshold in `tests/integration/test_pick_sequence.py`.

- [ ] T027 [US1] Connect `open_gripper` and `close_gripper` action parameters to runtime commands in `src/actions/dispatcher.py`.
  - Testable check: integration test confirms action params alter gripper command inputs in `tests/integration/test_gripper_actions.py`.

- [ ] T028 [US1] Add acceptance integration test for exact command flow in `tests/integration/test_pickup_succeeds.py`.
  - Testable check: test passes when command is "pick up the cube" and lift criterion met at least once.

## Phase 4: User Story 2 - Describe/Place Actions (P2)

**Goal**: Scene introspection and place behavior work through the same validated action pipeline.

**Independent test**: Execute `describe_scene()` and `place(target_xyz)` from validated action inputs.

- [ ] T029 [US2] Implement robust object lookup/name normalization for `pick(object)` and reporting in `src/sim/world.py`.
  - Testable check: unit test verifies aliases like "cube" resolve deterministically in `tests/unit/test_object_resolution.py`.

- [ ] T030 [US2] Implement `place(target_xyz)` high-level routine with approach/release/retreat in `src/sim/tasks.py`.
  - Testable check: integration test validates cube final pose near target in `tests/integration/test_place_sequence.py`.

- [ ] T031 [US2] Ensure action schema and validator support place/describe specifics in `src/actions/schema.py` and `src/actions/validator.py`.
  - Testable check: unit tests for place target validation and describe no-arg behavior in `tests/unit/test_place_describe_validation.py`.

- [ ] T032 [US2] Add integration test for describe + place pipeline in `tests/integration/test_describe_and_place_pipeline.py`.
  - Testable check: both actions execute via dispatcher with no schema/safety failures.

## Phase 5: User Story 3 - Reset and Safe Recovery (P3)

**Goal**: Failed actions do not execute unsafely, and `reset()` restores default state for retry.

**Independent test**: Trigger invalid/unsafe actions, verify fail-safe behavior, then reset and retry.

- [ ] T033 [US3] Implement `reset()` behavior for robot joints and cube pose in `src/sim/tasks.py` and `src/sim/world.py`.
  - Testable check: integration test asserts state equals baseline after reset in `tests/integration/test_reset_behavior.py`.

- [ ] T034 [US3] Implement non-execution fail path + user-visible errors for parse/validation/safety failures in `src/app.py` and `src/cli/repl.py`.
  - Testable check: integration test verifies invalid action returns error and sends no movement commands in `tests/integration/test_fail_safe_non_execution.py`.

- [ ] T035 [US3] Add safety regression tests for boundary clamping and hard rejection in `tests/unit/test_safety_regression.py`.
  - Testable check: out-of-range commands consistently fail or clamp per policy.

- [ ] T036 [US3] Add recovery integration test: invalid command -> reset -> successful pickup in `tests/integration/test_recovery_after_failure.py`.
  - Testable check: full scenario passes in one process without restart.

## Phase 6: Documentation and Final Verification

- [ ] T037 [P] [Foundation] Document setup, Foundry Local config, and run commands in `README.md`.
  - Testable check: fresh-environment runbook is executable end-to-end by following README steps.

- [ ] T038 [P] [Foundation] Add troubleshooting section for JSON parse/safety/endpoint failures in `README.md`.
  - Testable check: each known failure mode has an actionable remediation step.

- [ ] T039 [Foundation] Add test fixture action payloads in `tests/fixtures/sample_actions.json`.
  - Testable check: parser/validator tests consume fixture cases successfully.

- [ ] T040 [Foundation] Add final smoke integration test for startup and one CLI iteration in `tests/integration/test_app_smoke.py`.
  - Testable check: app starts, processes one mocked command, and exits cleanly.

## Dependency Notes

- T001-T005 must complete before T009+.
- T009-T022 are blocking foundation tasks for user stories.
- US1 tasks (T023-T028) should complete before claiming MVP acceptance.
- US2 and US3 can proceed after foundation; they may run in parallel with separate owners.
- Documentation tasks (T037-T038) can run in parallel near the end but should be finalized after integration tests stabilize.

## MVP Slice

- Complete: T001-T028.
- MVP pass condition: `tests/integration/test_pickup_succeeds.py` passes and acceptance criterion is met.
