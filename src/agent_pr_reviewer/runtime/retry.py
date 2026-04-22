from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryableToolError(RuntimeError):
    """Raised when a tool failure should be retried."""


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    backoff_seconds: float = 0.2

    def run(self, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                return operation()
            except RetryableToolError as error:
                last_error = error
                if attempt == self.attempts:
                    break
                time.sleep(self.backoff_seconds * attempt)
        if last_error is None:
            raise RuntimeError("retry policy failed without capturing an error")
        raise last_error
