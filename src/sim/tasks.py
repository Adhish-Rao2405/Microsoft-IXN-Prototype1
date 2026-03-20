from __future__ import annotations

import logging

from src.models.result import ExecutionResult
from src.models.state import SceneState
from src.sim.gripper import close_gripper, open_gripper
from src.sim.kinematics import solve_ik
from src.sim.motion import execute_joint_trajectory, interpolate_joint_targets
from src.sim.robot import PandaRobot
from src.sim.world import PyBulletWorld
from src.utils.constants import (
    DEFAULT_EE_RPY,
    FINGER_OPEN_WIDTH,
    PICK_APPROACH_Z_OFFSET,
    PICK_CLOSE_FORCE,
    PICK_GRASP_Z_OFFSET,
    PICK_LIFT_Z_OFFSET,
    PICK_POST_CLOSE_SETTLE_STEPS,
    PICK_REGRASP_DELTA_Z,
    PICK_SUCCESS_MIN_HEIGHT_GAIN,
    PLACE_APPROACH_Z_OFFSET,
)


class ManipulationController:
    def __init__(self, world: PyBulletWorld, robot: PandaRobot) -> None:
        self.world = world
        self.robot = robot

    def describe_scene(self) -> SceneState:
        ee_position, ee_rpy = self.robot.get_end_effector_pose()
        arm_joints = self.robot.get_arm_joint_positions()
        return self.world.describe_scene(ee_position=ee_position, ee_rpy=ee_rpy, arm_joint_positions=arm_joints)

    def move_ee(
        self,
        target_xyz: tuple[float, float, float],
        target_rpy: tuple[float, float, float],
        speed: float,
    ) -> ExecutionResult:
        current = self.robot.get_arm_joint_positions()
        goal = solve_ik(
            client_id=self.world.client_id,
            robot_id=self.world.robot_id,
            target_xyz=target_xyz,
            target_rpy=target_rpy,
        )
        trajectory = interpolate_joint_targets(current=current, target=goal)
        execute_joint_trajectory(world=self.world, robot=self.robot, trajectory=trajectory, speed=speed)

        return ExecutionResult(
            success=True,
            action="move_ee",
            message="End-effector motion completed.",
            data={"target_xyz": list(target_xyz), "target_rpy": list(target_rpy), "speed": speed},
        )

    def open_gripper(self, width: float) -> ExecutionResult:
        self.world.detach_cube()
        open_gripper(world=self.world, robot=self.robot, width=width)
        return ExecutionResult(
            success=True,
            action="open_gripper",
            message="Gripper opened.",
            data={"width": width},
        )

    def close_gripper(self, force: float) -> ExecutionResult:
        close_gripper(world=self.world, robot=self.robot, force=force)
        return ExecutionResult(
            success=True,
            action="close_gripper",
            message="Gripper closed.",
            data={"force": force},
        )

    def pick(self, object_name: str) -> ExecutionResult:
        logger = logging.getLogger(__name__)
        scene = self.describe_scene()
        if object_name != "cube":
            return ExecutionResult(False, "pick", f"Only 'cube' is supported for pick, got '{object_name}'.")

        cube_position, _ = self.world.get_cube_pose()
        cube_x, cube_y, cube_z = cube_position
        cube_height_before = self.world.get_cube_height()

        # Keep tool orientation vertical/downward while approaching and grasping.
        approach_xyz = (cube_x, cube_y, cube_z + PICK_APPROACH_Z_OFFSET)
        grasp_xyz = (cube_x, cube_y, cube_z + PICK_GRASP_Z_OFFSET)
        lift_xyz = (cube_x, cube_y, cube_z + PICK_LIFT_Z_OFFSET)

        logger.info("pick(): cube_pos=%s", [round(v, 4) for v in cube_position])
        logger.info("pick(): target_approach=%s target_grasp=%s target_lift=%s", approach_xyz, grasp_xyz, lift_xyz)

        self.move_ee(approach_xyz, DEFAULT_EE_RPY, speed=0.25)
        self.open_gripper(FINGER_OPEN_WIDTH)
        self.move_ee(grasp_xyz, DEFAULT_EE_RPY, speed=0.18)
        self.close_gripper(force=PICK_CLOSE_FORCE)

        # Allow contacts and gripper closure to settle before evaluating grasp.
        self.world.step(steps=PICK_POST_CLOSE_SETTLE_STEPS, sleep_dt=0.0)
        gripper_positions = self.robot.get_gripper_joint_positions()
        logger.info("pick(): gripper_joints=%s", [round(v, 5) for v in gripper_positions])

        contact_exists = self.world.has_grasp_contact(self.robot.ee_link_index)
        attached = False
        if contact_exists:
            attached = self.world.attach_cube_to_ee(self.robot.ee_link_index)
        if not contact_exists and not attached:
            retry_grasp_xyz = (cube_x, cube_y, cube_z + max(0.0, PICK_GRASP_Z_OFFSET - PICK_REGRASP_DELTA_Z))
            logger.info("pick(): retry_grasp=%s", retry_grasp_xyz)
            self.move_ee(retry_grasp_xyz, DEFAULT_EE_RPY, speed=0.12)
            self.close_gripper(force=PICK_CLOSE_FORCE)
            self.world.step(steps=PICK_POST_CLOSE_SETTLE_STEPS, sleep_dt=0.0)
            contact_exists = self.world.has_grasp_contact(self.robot.ee_link_index)
            if contact_exists:
                attached = self.world.attach_cube_to_ee(self.robot.ee_link_index)
        logger.info("pick(): contact_exists=%s attached=%s", contact_exists, attached)

        # Lift vertically from the grasp pose.
        self.move_ee(lift_xyz, DEFAULT_EE_RPY, speed=0.22)
        self.world.step(steps=100, sleep_dt=0.0)

        cube_height_after = self.world.get_cube_height()
        height_gain = cube_height_after - cube_height_before
        success = (
            height_gain > PICK_SUCCESS_MIN_HEIGHT_GAIN
            or self.world.is_cube_attached()
            or self.world.has_grasp_contact(self.robot.ee_link_index)
        )
        logger.info(
            "pick(): cube_height_before=%.4f cube_height_after=%.4f height_gain=%.4f success=%s",
            cube_height_before,
            cube_height_after,
            height_gain,
            success,
        )

        if not success:
            return ExecutionResult(
                False,
                "pick",
                "Grasp failed: no stable contact or lift detected.",
                data={
                    "cube_height_before": cube_height_before,
                    "cube_height_after": cube_height_after,
                    "height_gain": height_gain,
                    "gripper_joints": gripper_positions,
                    "contact_exists": contact_exists,
                },
            )

        return ExecutionResult(
            success=True,
            action="pick",
            message="Cube picked and lifted.",
            data={
                "object": object_name,
                "lift_xyz": list(lift_xyz),
                "cube_height_before": cube_height_before,
                "cube_height_after": cube_height_after,
                "height_gain": height_gain,
            },
        )

    def place(self, target_xyz: tuple[float, float, float]) -> ExecutionResult:
        tx, ty, tz = target_xyz
        approach = (tx, ty, tz + PLACE_APPROACH_Z_OFFSET)

        self.move_ee(approach, DEFAULT_EE_RPY, speed=0.25)
        self.move_ee((tx, ty, tz), DEFAULT_EE_RPY, speed=0.18)
        self.open_gripper(FINGER_OPEN_WIDTH)
        self.move_ee(approach, DEFAULT_EE_RPY, speed=0.25)

        return ExecutionResult(
            success=True,
            action="place",
            message="Place routine completed.",
            data={"target_xyz": list(target_xyz)},
        )

    def reset(self) -> ExecutionResult:
        self.world.reset_cube_pose()
        self.robot.reset_home()
        self.world.step(steps=80, sleep_dt=0.0)
        return ExecutionResult(success=True, action="reset", message="World reset completed.")
