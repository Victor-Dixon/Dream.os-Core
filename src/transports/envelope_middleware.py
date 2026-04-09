"""Pre-routing validation: reject invalid envelopes before I/O."""

from __future__ import annotations

from src.core.message import BusMessage


def assert_pre_routing_envelope(message: BusMessage) -> None:
    """Validate a message against the canonical envelope rules + JSON Schema."""
    BusMessage.validate_dict(message.to_dict())
