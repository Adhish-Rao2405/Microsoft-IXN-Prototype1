from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    foundry_local_base_url: str
    foundry_local_model: str
    foundry_local_api_key: str | None
    request_timeout_s: float
    temperature: float
    max_completion_tokens: int
    simulation_timestep: float

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        # Accept both FOUNDRY_LOCAL_BASE_URL and FOUNDY_LOCAL_BASE_URL.
        # If neither is set, default to local Foundry endpoint.
        base_url = os.environ.get("FOUNDRY_LOCAL_BASE_URL", "").strip()
        if not base_url:
            base_url = os.environ.get("FOUNDY_LOCAL_BASE_URL", "").strip()
        if not base_url:
            base_url = "http://127.0.0.1:8000"

        return cls(
            foundry_local_base_url=base_url.rstrip("/"),
            foundry_local_model=os.environ.get("FOUNDRY_LOCAL_MODEL", "gpt-4o-mini").strip(),
            foundry_local_api_key=os.environ.get("FOUNDRY_LOCAL_API_KEY", "").strip() or None,
            request_timeout_s=float(os.environ.get("REQUEST_TIMEOUT_S", "60")),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0")),
            max_completion_tokens=int(os.environ.get("MAX_COMPLETION_TOKENS", "600")),
            simulation_timestep=float(os.environ.get("SIM_TIMESTEP", str(1.0 / 240.0))),
        )
