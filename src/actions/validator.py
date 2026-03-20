from __future__ import annotations

from src.actions.schema import PickAction, PlaceAction, RobotAction
from src.models.state import SceneState


class ActionValidator:
    def validate(self, actions: list[RobotAction], scene_state: SceneState) -> None:
        if not actions:
            raise ValueError("Action list cannot be empty.")

        for action in actions:
            if isinstance(action, PickAction):
                if action.parameters.object not in scene_state.objects:
                    raise ValueError(
                        f"Unknown object '{action.parameters.object}'. "
                        f"Known objects: {', '.join(sorted(scene_state.objects.keys()))}"
                    )

            if isinstance(action, PlaceAction):
                if len(action.parameters.target_xyz) != 3:
                    raise ValueError("place.target_xyz must have 3 values.")
