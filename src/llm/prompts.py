from __future__ import annotations

import json
from typing import Any


def system_prompt() -> str:
    return (
        "You are a robot action planner. "
        "Output strict JSON only with no markdown, no prose, no code fences. "
        "Use only these actions: describe_scene, move_ee, open_gripper, "
        "close_gripper, pick, place, reset. "
        "Always return an object with key 'actions' that is a non-empty list of action objects."
    )


def build_messages(user_command: str, scene_dict: dict[str, Any]) -> list[dict[str, str]]:
    user_payload = {
        "user_command": user_command,
        "scene": scene_dict,
        "required_output_format": {
            "actions": [
                {
                    "action": "<one_of_supported_actions>",
                    "parameters": "<object>"
                }
            ]
        },
    }
    return [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": json.dumps(user_payload)},
    ]


def response_json_schema() -> dict[str, Any]:
    action_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["action", "parameters"],
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "describe_scene",
                    "move_ee",
                    "open_gripper",
                    "close_gripper",
                    "pick",
                    "place",
                    "reset",
                ],
            },
            "parameters": {"type": "object"},
        },
    }

    return {
        "name": "robot_actions",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["actions"],
            "properties": {
                "actions": {
                    "type": "array",
                    "minItems": 1,
                    "items": action_schema,
                }
            },
        },
    }
