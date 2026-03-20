from __future__ import annotations

from src.actions.schema import (
    CloseGripperAction,
    CloseGripperParameters,
    MoveEEAction,
    MoveEEParameters,
    OpenGripperAction,
    OpenGripperParameters,
    PlaceAction,
    PlaceParameters,
    RobotAction,
)
from src.utils.constants import (
    GRIPPER_FORCE_MAX,
    GRIPPER_FORCE_MIN,
    GRIPPER_WIDTH_MAX,
    GRIPPER_WIDTH_MIN,
    RPY_MAX,
    RPY_MIN,
    SPEED_MAX,
    SPEED_MIN,
    WORKSPACE_MAX,
    WORKSPACE_MIN,
)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


class SafetyPolicy:
    def apply(self, action: RobotAction) -> RobotAction:
        if isinstance(action, MoveEEAction):
            x, y, z = action.parameters.target_xyz
            rr, rp, ry = action.parameters.target_rpy
            speed = action.parameters.speed

            safe_xyz = (
                _clamp(x, WORKSPACE_MIN[0], WORKSPACE_MAX[0]),
                _clamp(y, WORKSPACE_MIN[1], WORKSPACE_MAX[1]),
                _clamp(z, WORKSPACE_MIN[2], WORKSPACE_MAX[2]),
            )
            safe_rpy = (
                _clamp(rr, RPY_MIN[0], RPY_MAX[0]),
                _clamp(rp, RPY_MIN[1], RPY_MAX[1]),
                _clamp(ry, RPY_MIN[2], RPY_MAX[2]),
            )
            safe_speed = _clamp(speed, SPEED_MIN, SPEED_MAX)
            return MoveEEAction(
                action="move_ee",
                parameters=MoveEEParameters(
                    target_xyz=safe_xyz,
                    target_rpy=safe_rpy,
                    speed=safe_speed,
                ),
            )

        if isinstance(action, OpenGripperAction):
            safe_width = _clamp(action.parameters.width, GRIPPER_WIDTH_MIN, GRIPPER_WIDTH_MAX)
            return OpenGripperAction(
                action="open_gripper",
                parameters=OpenGripperParameters(width=safe_width),
            )

        if isinstance(action, CloseGripperAction):
            safe_force = _clamp(action.parameters.force, GRIPPER_FORCE_MIN, GRIPPER_FORCE_MAX)
            return CloseGripperAction(
                action="close_gripper",
                parameters=CloseGripperParameters(force=safe_force),
            )

        if isinstance(action, PlaceAction):
            x, y, z = action.parameters.target_xyz
            safe_xyz = (
                _clamp(x, WORKSPACE_MIN[0], WORKSPACE_MAX[0]),
                _clamp(y, WORKSPACE_MIN[1], WORKSPACE_MAX[1]),
                _clamp(z, WORKSPACE_MIN[2], WORKSPACE_MAX[2]),
            )
            return PlaceAction(action="place", parameters=PlaceParameters(target_xyz=safe_xyz))

        return action
