from __future__ import annotations

import pybullet as p

from src.utils.constants import PANDA_ARM_JOINTS, PANDA_EE_LINK_INDEX


def solve_ik(
    client_id: int,
    robot_id: int,
    target_xyz: tuple[float, float, float],
    target_rpy: tuple[float, float, float],
) -> list[float]:
    target_quat = p.getQuaternionFromEuler(target_rpy)
    full_solution = p.calculateInverseKinematics(
        bodyUniqueId=robot_id,
        endEffectorLinkIndex=PANDA_EE_LINK_INDEX,
        targetPosition=target_xyz,
        targetOrientation=target_quat,
        physicsClientId=client_id,
    )
    return [float(full_solution[i]) for i in range(len(PANDA_ARM_JOINTS))]
