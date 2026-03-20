from __future__ import annotations

import math

from src.sim.robot import PandaRobot
from src.sim.world import PyBulletWorld
from src.utils.constants import MAX_JOINT_STEP


def interpolate_joint_targets(current: list[float], target: list[float]) -> list[list[float]]:
    if len(current) != len(target):
        raise ValueError("Current and target joint vectors must have same length.")

    max_delta = max(abs(t - c) for c, t in zip(current, target))
    steps = max(1, int(math.ceil(max_delta / MAX_JOINT_STEP)))

    result: list[list[float]] = []
    for i in range(1, steps + 1):
        alpha = i / steps
        result.append([c + (t - c) * alpha for c, t in zip(current, target)])
    return result


def execute_joint_trajectory(
    world: PyBulletWorld,
    robot: PandaRobot,
    trajectory: list[list[float]],
    speed: float,
) -> None:
    if speed <= 0:
        raise ValueError("Speed must be positive.")

    sleep_dt = max(0.0, 0.01 / speed)
    for point in trajectory:
        robot.set_arm_joint_targets(point)
        world.step(steps=2, sleep_dt=sleep_dt)

    world.step(steps=20, sleep_dt=sleep_dt)
