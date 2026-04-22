from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryStore:
    """Simple in-memory context shared across runtime steps."""

    values: dict[str, Any] = field(default_factory=dict)

    def put(self, key: str, value: Any) -> None:
        self.values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def snapshot(self) -> dict[str, Any]:
        return dict(self.values)
