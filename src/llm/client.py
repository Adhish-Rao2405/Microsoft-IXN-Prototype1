from __future__ import annotations

import logging
from typing import Any

import requests

from src.config import Settings
from src.llm.prompts import build_messages, response_json_schema

logger = logging.getLogger(__name__)


class FoundryLocalClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._active_model = settings.foundry_local_model
        logger.info(
            "FoundryLocalClient initialized: base_url=%s model=%s timeout=%s",
            self._settings.foundry_local_base_url,
            self._active_model,
            self._settings.request_timeout_s,
        )

    @property
    def active_model(self) -> str:
        return self._active_model

    def set_active_model(self, model_name: str) -> None:
        normalized = model_name.strip()
        if not normalized:
            raise ValueError("Model name cannot be empty.")
        self._active_model = normalized
        logger.info("Switched active Foundry model to: %s", self._active_model)

    def list_models(self) -> list[str]:
        url = f"{self._settings.foundry_local_base_url}/v1/models"
        logger.info("Foundry model list URL: %s", url)

        headers = {"Content-Type": "application/json"}
        if self._settings.foundry_local_api_key:
            headers["Authorization"] = f"Bearer {self._settings.foundry_local_api_key}"

        for attempt in range(1, 3):
            try:
                response = requests.get(url, headers=headers, timeout=self._settings.request_timeout_s)
                response.raise_for_status()
                break
            except requests.exceptions.ConnectionError as exc:
                if attempt < 2:
                    logger.warning("Model list connection failed on attempt %d: %s", attempt, exc)
                    continue
                raise ValueError(
                    f"Failed to connect to Foundry Local model list at {url} after 2 attempts. "
                    f"Ensure Foundry Local is running. Error: {exc}"
                ) from exc
            except requests.exceptions.Timeout as exc:
                if attempt < 2:
                    logger.warning("Model list request timed out on attempt %d: %s", attempt, exc)
                    continue
                raise ValueError(
                    f"Timed out while querying model list after {self._settings.request_timeout_s}s "
                    f"(2 attempts). Error: {exc}"
                ) from exc
            except requests.exceptions.RequestException as exc:
                raise ValueError(f"Model list request failed: {exc}") from exc

        try:
            payload = response.json()
            data = payload.get("data", [])
        except Exception as exc:
            raise ValueError(f"Invalid model list response from Foundry Local: {exc}") from exc

        models: list[str] = []
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                models.append(item["id"])

        if not models:
            raise ValueError("No models returned by Foundry Local. Start at least one model.")
        return models

    def generate_actions(self, user_command: str, scene_dict: dict[str, Any]) -> str:
        url = f"{self._settings.foundry_local_base_url}/v1/chat/completions"
        logger.info("LLM request URL: %s", url)

        headers = {"Content-Type": "application/json"}
        if self._settings.foundry_local_api_key:
            headers["Authorization"] = f"Bearer {self._settings.foundry_local_api_key}"

        payload = {
            "model": self._active_model,
            "messages": build_messages(user_command=user_command, scene_dict=scene_dict),
            "temperature": self._settings.temperature,
            "max_completion_tokens": self._settings.max_completion_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": response_json_schema(),
            },
        }

        # Attempt with retry on connection failure.
        for attempt in range(1, 3):
            try:
                logger.debug("LLM request attempt %d: timeout=%s", attempt, self._settings.request_timeout_s)
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self._settings.request_timeout_s,
                )
                response.raise_for_status()
                logger.info("LLM request succeeded on attempt %d", attempt)
                break

            except requests.exceptions.ConnectionError as exc:
                if attempt < 2:
                    logger.warning(
                        "LLM connection failed on attempt %d (will retry): %s",
                        attempt,
                        exc,
                    )
                    continue
                raise ValueError(
                    f"Failed to connect to Foundry Local at {url} after 2 attempts. "
                    f"Ensure Foundry Local is running and FOUNDRY_LOCAL_BASE_URL is correct. "
                    f"Error: {exc}"
                ) from exc

            except requests.exceptions.Timeout as exc:
                if attempt < 2:
                    logger.warning(
                        "LLM request timed out on attempt %d (will retry): %s",
                        attempt,
                        exc,
                    )
                    continue
                raise ValueError(
                    f"LLM request timed out after {self._settings.request_timeout_s}s "
                    f"(2 attempts). Check Foundry Local is responsive. Error: {exc}"
                ) from exc

            except requests.exceptions.RequestException as exc:
                raise ValueError(f"LLM request failed: {exc}") from exc

        try:
            data = response.json()
        except Exception as exc:
            raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected LLM response shape: {data}") from exc

        if isinstance(content, list):
            text_chunks = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_chunks.append(str(part["text"]))
            content = "".join(text_chunks)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM returned empty action content.")

        logger.debug("LLM response content length: %d", len(content))
        return content
