from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionResult:
    success: bool
    action: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
