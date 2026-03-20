from __future__ import annotations

import time
from typing import Any

import pybullet as p
import pybullet_data

from src.models.state import SceneObject, SceneState


class PyBulletWorld:
    def __init__(self, timestep: float) -> None:
        self.timestep = timestep
        self.client_id: int | None = None
        self.plane_id: int | None = None
        self.table_id: int | None = None
        self.robot_id: int | None = None
        self.cube_id: int | None = None
        self._cube_constraint_id: int | None = None

        self._cube_start_position = [0.62, 0.0, 0.02]
        self._cube_start_orientation = p.getQuaternionFromEuler([0.0, 0.0, 0.0])

    def connect(self) -> None:
        if self.client_id is not None:
            return
        self.client_id = p.connect(p.GUI)
        if self.client_id < 0:
            raise RuntimeError("Failed to connect to PyBullet GUI.")

        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.client_id)
        p.setGravity(0, 0, -9.81, physicsClientId=self.client_id)
        p.setTimeStep(self.timestep, physicsClientId=self.client_id)
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0, physicsClientId=self.client_id)

    def setup_scene(self) -> None:
        self._require_connected()
        self.plane_id = p.loadURDF("plane.urdf", physicsClientId=self.client_id)
        self.table_id = p.loadURDF(
            "table/table.urdf",
            [0.5, 0.0, -0.65],
            useFixedBase=True,
            physicsClientId=self.client_id,
        )
        self.robot_id = p.loadURDF(
            "franka_panda/panda.urdf",
            [0.0, 0.0, 0.0],
            useFixedBase=True,
            physicsClientId=self.client_id,
        )
        self.cube_id = p.loadURDF(
            "cube_small.urdf",
            self._cube_start_position,
            self._cube_start_orientation,
            globalScaling=1.15,
            physicsClientId=self.client_id,
        )

        for _ in range(60):
            self.step(1, sleep_dt=0.0)

    def step(self, steps: int = 1, sleep_dt: float = 0.0) -> None:
        self._require_connected()
        for _ in range(steps):
            p.stepSimulation(physicsClientId=self.client_id)
            if sleep_dt > 0:
                time.sleep(sleep_dt)

    def describe_scene(
        self,
        ee_position: list[float],
        ee_rpy: list[float],
        arm_joint_positions: list[float],
    ) -> SceneState:
        self._require_scene_loaded()
        cube_pos, cube_orn = p.getBasePositionAndOrientation(
            self.cube_id,
            physicsClientId=self.client_id,
        )
        cube_rpy = p.getEulerFromQuaternion(cube_orn)

        objects = {
            "cube": SceneObject(
                name="cube",
                body_id=self.cube_id,
                position=list(cube_pos),
                orientation_rpy=list(cube_rpy),
            ),
            "table": SceneObject(
                name="table",
                body_id=self.table_id,
                position=[0.5, 0.0, -0.65],
                orientation_rpy=[0.0, 0.0, 0.0],
            ),
            "panda": SceneObject(
                name="panda",
                body_id=self.robot_id,
                position=[0.0, 0.0, 0.0],
                orientation_rpy=[0.0, 0.0, 0.0],
            ),
        }

        return SceneState(
            ee_position=ee_position,
            ee_rpy=ee_rpy,
            arm_joint_positions=arm_joint_positions,
            cube_position=list(cube_pos),
            cube_rpy=list(cube_rpy),
            objects=objects,
        )

    def attach_cube_to_ee(self, ee_link_index: int) -> bool:
        self._require_scene_loaded()
        if self._cube_constraint_id is not None:
            return True

        closest = p.getClosestPoints(
            bodyA=self.robot_id,
            bodyB=self.cube_id,
            distance=0.055,
            linkIndexA=ee_link_index,
            physicsClientId=self.client_id,
        )
        if not closest:
            return False

        link_state = p.getLinkState(
            self.robot_id,
            ee_link_index,
            computeForwardKinematics=True,
            physicsClientId=self.client_id,
        )
        ee_pos = link_state[4]
        ee_orn = link_state[5]

        cube_pos, cube_orn = p.getBasePositionAndOrientation(self.cube_id, physicsClientId=self.client_id)
        inv_ee_pos, inv_ee_orn = p.invertTransform(ee_pos, ee_orn)
        child_pos, child_orn = p.multiplyTransforms(inv_ee_pos, inv_ee_orn, cube_pos, cube_orn)

        self._cube_constraint_id = p.createConstraint(
            parentBodyUniqueId=self.robot_id,
            parentLinkIndex=ee_link_index,
            childBodyUniqueId=self.cube_id,
            childLinkIndex=-1,
            jointType=p.JOINT_FIXED,
            jointAxis=[0, 0, 0],
            parentFramePosition=[0, 0, 0],
            childFramePosition=list(child_pos),
            parentFrameOrientation=[0, 0, 0, 1],
            childFrameOrientation=list(child_orn),
            physicsClientId=self.client_id,
        )
        return True

    def get_cube_pose(self) -> tuple[list[float], list[float]]:
        self._require_scene_loaded()
        cube_pos, cube_orn = p.getBasePositionAndOrientation(self.cube_id, physicsClientId=self.client_id)
        cube_rpy = p.getEulerFromQuaternion(cube_orn)
        return list(cube_pos), list(cube_rpy)

    def get_cube_height(self) -> float:
        cube_pos, _ = self.get_cube_pose()
        return float(cube_pos[2])

    def has_grasp_contact(self, ee_link_index: int) -> bool:
        self._require_scene_loaded()
        contacts = p.getContactPoints(
            bodyA=self.robot_id,
            bodyB=self.cube_id,
            linkIndexA=ee_link_index,
            physicsClientId=self.client_id,
        )
        return bool(contacts)

    def detach_cube(self) -> None:
        self._require_connected()
        if self._cube_constraint_id is not None:
            p.removeConstraint(self._cube_constraint_id, physicsClientId=self.client_id)
            self._cube_constraint_id = None

    def reset_cube_pose(self) -> None:
        self._require_scene_loaded()
        self.detach_cube()
        p.resetBasePositionAndOrientation(
            self.cube_id,
            self._cube_start_position,
            self._cube_start_orientation,
            physicsClientId=self.client_id,
        )

    def is_cube_attached(self) -> bool:
        return self._cube_constraint_id is not None

    def shutdown(self) -> None:
        if self.client_id is not None:
            self.detach_cube()
            p.disconnect(physicsClientId=self.client_id)
            self.client_id = None

    def _require_connected(self) -> None:
        if self.client_id is None:
            raise RuntimeError("PyBullet is not connected.")

    def _require_scene_loaded(self) -> None:
        self._require_connected()
        if self.robot_id is None or self.cube_id is None or self.table_id is None:
            raise RuntimeError("Scene not initialized.")

    def debug_snapshot(self) -> dict[str, Any]:
        self._require_scene_loaded()
        cube_pos, cube_orn = p.getBasePositionAndOrientation(self.cube_id, physicsClientId=self.client_id)
        return {
            "cube_position": list(cube_pos),
            "cube_rpy": list(p.getEulerFromQuaternion(cube_orn)),
            "cube_attached": self.is_cube_attached(),
        }
