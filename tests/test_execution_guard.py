from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.execution_guard import (
    TRANSITION_AUDIT,
    InvalidExecutionPathError,
    InvalidMessageTransitionError,
    require_bus_message,
    validate_transition,
)
from src.core.message import BusMessage


def test_require_bus_message_accepts_bus_message() -> None:
    message = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="status",
        device_hint="worker",
    )
    assert require_bus_message(message) is message


def test_require_bus_message_rejects_raw_dict() -> None:
    with pytest.raises(InvalidExecutionPathError):
        require_bus_message({"type": "task"})


def test_validate_transition_rejects_invalid_jump() -> None:
    with pytest.raises(InvalidMessageTransitionError):
        validate_transition("new", "running")


def test_validate_transition_accepts_valid_jump() -> None:
    assert validate_transition("running", "complete") is True


def test_invalid_transition_is_not_audited() -> None:
    n = len(TRANSITION_AUDIT)
    with pytest.raises(InvalidMessageTransitionError):
        validate_transition("new", "complete")
    assert len(TRANSITION_AUDIT) == n


def test_valid_transition_appends_audit_record() -> None:
    validate_transition(
        "new",
        "claimed",
        message_id="00000000-0000-4000-8000-000000000001",
        source="unit_test",
    )
    assert TRANSITION_AUDIT[-1]["from"] == "new"
    assert TRANSITION_AUDIT[-1]["to"] == "claimed"
    assert TRANSITION_AUDIT[-1]["message_id"] == "00000000-0000-4000-8000-000000000001"
    assert TRANSITION_AUDIT[-1]["source"] == "unit_test"
