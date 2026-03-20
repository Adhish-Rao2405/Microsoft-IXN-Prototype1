from __future__ import annotations

import pybullet as p

from src.utils.constants import (
    FINGER_OPEN_WIDTH,
    PANDA_ARM_JOINTS,
    PANDA_EE_LINK_INDEX,
    PANDA_FINGER_JOINTS,
    PANDA_HOME_JOINTS,
)


class PandaRobot:
    def __init__(self, client_id: int, robot_id: int) -> None:
        self.client_id = client_id
        self.robot_id = robot_id
        self.arm_joints = tuple(PANDA_ARM_JOINTS)
        self.finger_joints = tuple(PANDA_FINGER_JOINTS)
        self.ee_link_index = PANDA_EE_LINK_INDEX

    def reset_home(self) -> None:
        for idx, target in zip(self.arm_joints, PANDA_HOME_JOINTS):
            p.resetJointState(self.robot_id, idx, target, physicsClientId=self.client_id)
        self.set_gripper_width(FINGER_OPEN_WIDTH, force=30.0, settle_steps=80)

    def get_arm_joint_positions(self) -> list[float]:
        positions = []
        for idx in self.arm_joints:
            positions.append(p.getJointState(self.robot_id, idx, physicsClientId=self.client_id)[0])
        return positions

    def get_end_effector_pose(self) -> tuple[list[float], list[float]]:
        link_state = p.getLinkState(
            self.robot_id,
            self.ee_link_index,
            computeForwardKinematics=True,
            physicsClientId=self.client_id,
        )
        pos = list(link_state[4])
        rpy = list(p.getEulerFromQuaternion(link_state[5]))
        return pos, rpy

    def set_arm_joint_targets(self, targets: list[float], force: float = 120.0) -> None:
        p.setJointMotorControlArray(
            bodyUniqueId=self.robot_id,
            jointIndices=list(self.arm_joints),
            controlMode=p.POSITION_CONTROL,
            targetPositions=list(targets),
            forces=[force] * len(self.arm_joints),
            physicsClientId=self.client_id,
        )

    def set_gripper_width(self, width: float, force: float, settle_steps: int = 60) -> None:
        target = max(0.0, min(0.08, width)) / 2.0
        for _ in range(settle_steps):
            p.setJointMotorControlArray(
                bodyUniqueId=self.robot_id,
                jointIndices=list(self.finger_joints),
                controlMode=p.POSITION_CONTROL,
                targetPositions=[target, target],
                forces=[force, force],
                physicsClientId=self.client_id,
            )

    def get_gripper_joint_positions(self) -> list[float]:
        return [
            p.getJointState(self.robot_id, idx, physicsClientId=self.client_id)[0]
            for idx in self.finger_joints
        ]
