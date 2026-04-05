from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.core.message import BusMessage
from src.core.types import MessageStatus


def claim_message(message: BusMessage, node_id: str, lease_seconds: int = 120) -> BusMessage:
    expiry = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
    payload = message.to_dict()
    payload["status"] = MessageStatus.CLAIMED.value
    payload["lease_owner"] = node_id
    payload["lease_expires_at"] = expiry.isoformat(timespec="seconds")
    return BusMessage.from_dict(payload)


def mark_running(message: BusMessage) -> BusMessage:
    payload = message.to_dict()
    payload["status"] = MessageStatus.RUNNING.value
    return BusMessage.from_dict(payload)


def mark_complete(message: BusMessage) -> BusMessage:
    payload = message.to_dict()
    payload["status"] = MessageStatus.COMPLETE.value
    payload["lease_expires_at"] = None
    return BusMessage.from_dict(payload)
