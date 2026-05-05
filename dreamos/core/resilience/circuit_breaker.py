from __future__ import annotations

import time
from enum import Enum
from typing import Callable


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(RuntimeError):
    """Raised when an operation is blocked by an open circuit breaker."""


class CircuitBreaker:
    """Small deterministic circuit breaker for runtime resilience gates."""

    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 30.0,
        success_threshold: int = 1,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if recovery_timeout_seconds < 0:
            raise ValueError("recovery_timeout_seconds must be >= 0")
        if success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")

        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.success_threshold = success_threshold
        self.clock = clock or time.monotonic

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at: float | None = None

    def before_call(self) -> None:
        """Raise if calls are currently blocked; transition to half-open when ready."""
        if self.state != CircuitState.OPEN:
            return

        if self.opened_at is None:
            raise CircuitBreakerOpen("circuit is open")

        elapsed = self.clock() - self.opened_at
        if elapsed < self.recovery_timeout_seconds:
            raise CircuitBreakerOpen("circuit is open")

        self.state = CircuitState.HALF_OPEN
        self.success_count = 0

    def record_success(self) -> None:
        """Record a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close()
            return

        if self.state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count += 1

    def record_failure(self) -> None:
        """Record a failed operation and open/reopen when thresholds require it."""
        if self.state == CircuitState.HALF_OPEN:
            self._open()
            return

        if self.state == CircuitState.OPEN:
            self.opened_at = self.clock()
            return

        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self._open()

    def call(self, operation: Callable[[], object]) -> object:
        """Run an operation through the breaker and record success/failure."""
        self.before_call()
        try:
            result = operation()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result

    def _open(self) -> None:
        self.state = CircuitState.OPEN
        self.opened_at = self.clock()
        self.success_count = 0

    def _close(self) -> None:
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.opened_at = None
