from __future__ import annotations

import json

from pydantic import ValidationError

from src.actions.schema import ActionEnvelope


def parse_json_actions(raw_content: str) -> ActionEnvelope:
    text = raw_content.strip()
    if not text:
        raise ValueError("LLM output was empty.")

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM output is not valid JSON: {exc}") from exc

    if isinstance(parsed, dict) and "action" in parsed:
        parsed = {"actions": [parsed]}

    if not isinstance(parsed, dict) or "actions" not in parsed:
        raise ValueError("JSON must be an object containing an 'actions' field.")

    try:
        return ActionEnvelope.model_validate(parsed)
    except ValidationError as exc:
        raise ValueError(f"JSON does not match strict action schema: {exc}") from exc
