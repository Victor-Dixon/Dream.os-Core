from __future__ import annotations

from typing import Any

from src.core.message import BusMessage


TRANSITION_AUDIT: list[dict[str, Any]] = []


def clear_transition_audit() -> None:
    TRANSITION_AUDIT.clear()


class InvalidExecutionPathError(ValueError):
    """Raised when execution bypasses the message-bus boundary."""


class InvalidMessageTransitionError(ValueError):
    """Raised when an invalid lifecycle transition is attempted."""



class InvalidPromptError(ValueError):
    """Raised when an LLM prompt violates guard policy."""

BLOCKED_PROMPT_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "bypass safety",
    "system prompt",
    "developer message",
)

MAX_PROMPT_CHARS = 12000


def validate_prompt(prompt: str, *, max_chars: int = MAX_PROMPT_CHARS) -> str:
    if not isinstance(prompt, str):
        raise InvalidPromptError("Prompt must be a string.")

    normalized = prompt.strip()
    if not normalized:
        raise InvalidPromptError("Prompt must not be empty.")

    if len(normalized) > max_chars:
        raise InvalidPromptError("Prompt exceeds maximum allowed length.")

    lowered = normalized.lower()
    for marker in BLOCKED_PROMPT_MARKERS:
        if marker in lowered:
            raise InvalidPromptError(f"Prompt rejected by blocked marker: {marker}")

    return normalized


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


def validate_transition(
    current_state: str,
    next_state: str,
    *,
    message_id: str | None = None,
    source: str | None = None,
) -> bool:
    allowed = ALLOWED_TRANSITIONS.get(current_state, set())
    if next_state not in allowed:
        raise InvalidMessageTransitionError(
            f"Invalid message transition: {current_state} -> {next_state}"
        )
    TRANSITION_AUDIT.append(
        {
            "from": current_state,
            "to": next_state,
            "message_id": message_id,
            "source": source,
        }
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
