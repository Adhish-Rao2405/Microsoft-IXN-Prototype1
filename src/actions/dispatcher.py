from __future__ import annotations

from src.actions.schema import (
    CloseGripperAction,
    DescribeSceneAction,
    MoveEEAction,
    OpenGripperAction,
    PickAction,
    PlaceAction,
    ResetAction,
    RobotAction,
)
from src.models.result import ExecutionResult
from src.sim.tasks import ManipulationController


class ActionDispatcher:
    def __init__(self, controller: ManipulationController) -> None:
        self._controller = controller

    def dispatch(self, action: RobotAction) -> ExecutionResult:
        if isinstance(action, DescribeSceneAction):
            scene = self._controller.describe_scene().to_dict()
            return ExecutionResult(
                success=True,
                action="describe_scene",
                message="Scene described.",
                data=scene,
            )

        if isinstance(action, MoveEEAction):
            params = action.parameters
            return self._controller.move_ee(
                target_xyz=params.target_xyz,
                target_rpy=params.target_rpy,
                speed=params.speed,
            )

        if isinstance(action, OpenGripperAction):
            return self._controller.open_gripper(width=action.parameters.width)

        if isinstance(action, CloseGripperAction):
            return self._controller.close_gripper(force=action.parameters.force)

        if isinstance(action, PickAction):
            return self._controller.pick(object_name=action.parameters.object)

        if isinstance(action, PlaceAction):
            return self._controller.place(target_xyz=action.parameters.target_xyz)

        if isinstance(action, ResetAction):
            return self._controller.reset()

        raise ValueError(f"Unsupported action type: {action}")
