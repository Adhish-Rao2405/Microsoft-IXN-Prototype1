from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class SceneObject:
    name: str
    body_id: int
    position: list[float]
    orientation_rpy: list[float]


@dataclass
class SceneState:
    ee_position: list[float]
    ee_rpy: list[float]
    arm_joint_positions: list[float]
    cube_position: list[float]
    cube_rpy: list[float]
    objects: dict[str, SceneObject]

    def to_dict(self) -> dict:
        return asdict(self)
