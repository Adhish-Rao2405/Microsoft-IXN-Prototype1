from __future__ import annotations

from src.actions.schema import (
    CloseGripperAction,
    CloseGripperParameters,
    DescribeSceneAction,
    OpenGripperAction,
    OpenGripperParameters,
    PickAction,
    PickParameters,
    ResetAction,
    RobotAction,
)
from src.utils.constants import FINGER_OPEN_WIDTH, GRIPPER_FORCE_MAX


def try_parse_debug_command(user_input: str) -> list[RobotAction] | None:
    """
    Try to match user input against known debug commands.
    If matched, return a list of actions to execute.
    If not matched, return None (fall through to LLM).
    """
    lower_input = user_input.lower().strip()

    # "pick up cube" or "pick cube"
    if "pick" in lower_input and "cube" in lower_input:
        return [PickAction(action="pick", parameters=PickParameters(object="cube"))]

    # "reset"
    if lower_input == "reset":
        return [ResetAction(action="reset")]

    # "describe scene" or "describe"
    if "describe" in lower_input and "scene" in lower_input:
        return [DescribeSceneAction(action="describe_scene")]
    if lower_input == "describe":
        return [DescribeSceneAction(action="describe_scene")]

    # "open gripper"
    if "open" in lower_input and "gripper" in lower_input:
        return [
            OpenGripperAction(
                action="open_gripper",
                parameters=OpenGripperParameters(width=FINGER_OPEN_WIDTH),
            )
        ]

    # "close gripper"
    if "close" in lower_input and "gripper" in lower_input:
        return [
            CloseGripperAction(
                action="close_gripper",
                parameters=CloseGripperParameters(force=GRIPPER_FORCE_MAX * 0.8),
            )
        ]

    return None
