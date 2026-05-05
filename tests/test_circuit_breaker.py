from __future__ import annotations

import pytest

from dreamos.core.resilience import CircuitBreaker, CircuitBreakerOpen, CircuitState


def test_closed_opens_after_failure_threshold() -> None:
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=10)

    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED

    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN


def test_open_blocks_before_recovery_timeout() -> None:
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout_seconds=10, clock=lambda: 100.0)

    breaker.record_failure()

    with pytest.raises(CircuitBreakerOpen):
        breaker.before_call()


def test_open_moves_to_half_open_after_timeout() -> None:
    now = 100.0
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=5,
        clock=lambda: now,
    )

    breaker.record_failure()
    now = 106.0

    breaker.before_call()

    assert breaker.state == CircuitState.HALF_OPEN


def test_half_open_success_closes() -> None:
    now = 100.0
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=5,
        success_threshold=1,
        clock=lambda: now,
    )

    breaker.record_failure()
    now = 106.0
    breaker.before_call()
    breaker.record_success()

    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


def test_half_open_failure_reopens() -> None:
    now = 100.0
    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=5,
        clock=lambda: now,
    )

    breaker.record_failure()
    now = 106.0
    breaker.before_call()
    breaker.record_failure()

    assert breaker.state == CircuitState.OPEN
