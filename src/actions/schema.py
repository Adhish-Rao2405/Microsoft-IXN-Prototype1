from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DescribeSceneAction(StrictModel):
    action: Literal["describe_scene"]
    parameters: dict = Field(default_factory=dict)


class MoveEEParameters(StrictModel):
    target_xyz: tuple[float, float, float]
    target_rpy: tuple[float, float, float]
    speed: float


class MoveEEAction(StrictModel):
    action: Literal["move_ee"]
    parameters: MoveEEParameters


class OpenGripperParameters(StrictModel):
    width: float


class OpenGripperAction(StrictModel):
    action: Literal["open_gripper"]
    parameters: OpenGripperParameters


class CloseGripperParameters(StrictModel):
    force: float


class CloseGripperAction(StrictModel):
    action: Literal["close_gripper"]
    parameters: CloseGripperParameters


class PickParameters(StrictModel):
    object: str


class PickAction(StrictModel):
    action: Literal["pick"]
    parameters: PickParameters


class PlaceParameters(StrictModel):
    target_xyz: tuple[float, float, float]


class PlaceAction(StrictModel):
    action: Literal["place"]
    parameters: PlaceParameters


class ResetAction(StrictModel):
    action: Literal["reset"]
    parameters: dict = Field(default_factory=dict)


RobotAction = Annotated[
    Union[
        DescribeSceneAction,
        MoveEEAction,
        OpenGripperAction,
        CloseGripperAction,
        PickAction,
        PlaceAction,
        ResetAction,
    ],
    Field(discriminator="action"),
]


class ActionEnvelope(StrictModel):
    actions: list[RobotAction]
