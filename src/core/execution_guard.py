from __future__ import annotations

from typing import Any

from src.core.message import BusMessage


class InvalidExecutionPathError(ValueError):
    """Raised when execution bypasses the message-bus boundary."""


class InvalidMessageTransitionError(ValueError):
    """Raised when an invalid lifecycle transition is attempted."""


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "new": {"claimed"},
    "claimed": {"running", "expired"},
    "running": {"complete", "failed", "expired"},
    "complete": set(),
    "failed": set(),
    "expired": set(),
}


def require_bus_message(payload: Any) -> BusMessage:
    if not isinstance(payload, BusMessage):
        raise InvalidExecutionPathError(
            "Execution rejected: payload must be a validated BusMessage."
        )
    return payload


def validate_transition(current_state: str, next_state: str) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(current_state, set())
    if next_state not in allowed:
        raise InvalidMessageTransitionError(
            f"Invalid message transition: {current_state} -> {next_state}"
        )
    return True


def assert_execution_entrypoint(
    source: str,
    payload: Any | None = None,
    *,
    internal_only: bool = False,
    internal_call: bool = False,
) -> None:
    if internal_only and not internal_call:
        raise InvalidExecutionPathError(
            f"Execution rejected: {source} is internal-only. "
            "Submit a BusMessage through TaskAdapter.execute()."
        )
    if payload is not None:
        require_bus_message(payload)
