from __future__ import annotations

import json
import logging

from src.actions.dispatcher import ActionDispatcher
from src.actions.safety import SafetyPolicy
from src.actions.validator import ActionValidator
from src.cli.debug_commands import try_parse_debug_command
from src.cli.repl import run_cli
from src.config import Settings
from src.llm.client import FoundryLocalClient
from src.llm.parser import parse_json_actions
from src.models.result import ExecutionResult
from src.sim.robot import PandaRobot
from src.sim.tasks import ManipulationController
from src.sim.world import PyBulletWorld
from src.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def _format_results(results: list[ExecutionResult]) -> str:
    lines = []
    for result in results:
        status = "OK" if result.success else "ERROR"
        line = f"[{status}] {result.action}: {result.message}"
        if result.data:
            line += f" | data={json.dumps(result.data)}"
        lines.append(line)
    return "\n".join(lines)


def _format_model_list(models: list[str], active_model: str) -> str:
    lines = ["Available Foundry models:"]
    for index, model_name in enumerate(models, start=1):
        marker = "*" if model_name == active_model else " "
        lines.append(f"{index:>2}. [{marker}] {model_name}")
    lines.append("Use: model use <index|name>")
    return "\n".join(lines)


def main() -> None:
    configure_logging()
    settings = Settings.from_env()

    world = PyBulletWorld(timestep=settings.simulation_timestep)
    world.connect()
    world.setup_scene()

    robot = PandaRobot(client_id=world.client_id, robot_id=world.robot_id)
    robot.reset_home()
    world.step(steps=120, sleep_dt=0.0)

    controller = ManipulationController(world=world, robot=robot)
    dispatcher = ActionDispatcher(controller=controller)
    validator = ActionValidator()
    safety = SafetyPolicy()
    llm = FoundryLocalClient(settings=settings)
    model_cache: list[str] = []

    def process_command(user_command: str) -> str:
        scene_state = controller.describe_scene()
        scene_dict = scene_state.to_dict()
        normalized = user_command.strip()
        lower = normalized.lower()

        try:
            if lower in {"models", "model list", "/models"}:
                model_cache.clear()
                model_cache.extend(llm.list_models())
                return _format_model_list(model_cache, llm.active_model)

            if lower in {"model", "model current", "/model"}:
                return f"Current Foundry model: {llm.active_model}"

            if lower.startswith("model use "):
                selection = normalized[len("model use ") :].strip()
                if not selection:
                    return "[ERROR] Provide model index or name. Example: model use 1"

                chosen_model = selection
                if selection.isdigit():
                    if not model_cache:
                        model_cache.clear()
                        model_cache.extend(llm.list_models())
                    idx = int(selection)
                    if idx < 1 or idx > len(model_cache):
                        return f"[ERROR] Invalid model index {idx}. Run 'models' first."
                    chosen_model = model_cache[idx - 1]

                llm.set_active_model(chosen_model)
                return f"[OK] Active Foundry model set to: {llm.active_model}"

            # Try debug command matching first (no LLM needed).
            debug_actions = try_parse_debug_command(user_command)
            if debug_actions is not None:
                logger.info("Detected debug command: '%s'", user_command)
                validator.validate(debug_actions, scene_state)
                safe_actions = [safety.apply(action) for action in debug_actions]
                results: list[ExecutionResult] = []
                for action in safe_actions:
                    result = dispatcher.dispatch(action)
                    results.append(result)
                    if not result.success:
                        break
                return _format_results(results)

            # Fall through to LLM for natural-language planning.
            raw_output = llm.generate_actions(user_command=user_command, scene_dict=scene_dict)
            action_envelope = parse_json_actions(raw_output)
            validator.validate(action_envelope.actions, scene_state)

            safe_actions = [safety.apply(action) for action in action_envelope.actions]
            results: list[ExecutionResult] = []
            for action in safe_actions:
                result = dispatcher.dispatch(action)
                results.append(result)
                if not result.success:
                    break

            return _format_results(results)
        except Exception as exc:
            logger.exception("Command failed")
            return f"[ERROR] {exc}"

    try:
        run_cli(process_command=process_command)
    finally:
        world.shutdown()


if __name__ == "__main__":
    main()
