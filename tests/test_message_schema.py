from __future__ import annotations

import json

import pytest

from src.core.message import BusMessage, MessageValidationError
from src.core.types import MessageStatus


def test_message_round_trip() -> None:
    msg = BusMessage(
        from_agent="desktop.supervisor",
        to_agent="laptop.codex-1",
        msg_type="task",
        body="run tests",
        device_hint="laptop",
    )
    restored = BusMessage.from_json(msg.to_json())
    assert restored.to_dict() == msg.to_dict()


def test_invalid_message_missing_field() -> None:
    payload = BusMessage(
        from_agent="a",
        to_agent="b",
        msg_type="task",
        body="x",
        device_hint="desktop",
    ).to_dict()
    payload.pop("status")
    with pytest.raises(MessageValidationError):
        BusMessage.from_dict(payload)


def test_status_enum_values_stable_ssot() -> None:
    assert [s.value for s in MessageStatus] == ["new", "claimed", "running", "complete", "failed", "expired"]
    parsed = json.loads(BusMessage(from_agent="a", to_agent="b", msg_type="t", body="x", device_hint="desktop").to_json())
    assert parsed["status"] == "new"


def test_envelope_schema_rejects_extra_top_level_properties() -> None:
    payload = BusMessage(
        from_agent="a",
        to_agent="b",
        msg_type="task",
        body="x",
        device_hint="b",
    ).to_dict()
    payload["unexpected_field"] = True
    with pytest.raises(MessageValidationError, match="envelope schema"):
        BusMessage.validate_dict(payload)
