from __future__ import annotations

from src.sim.robot import PandaRobot
from src.sim.world import PyBulletWorld
from src.utils.constants import FINGER_CLOSED_WIDTH


def open_gripper(world: PyBulletWorld, robot: PandaRobot, width: float) -> None:
    robot.set_gripper_width(width=width, force=30.0, settle_steps=60)
    world.step(steps=40, sleep_dt=0.0)


def close_gripper(world: PyBulletWorld, robot: PandaRobot, force: float) -> None:
    robot.set_gripper_width(width=FINGER_CLOSED_WIDTH, force=force, settle_steps=80)
    world.step(steps=50, sleep_dt=0.0)
