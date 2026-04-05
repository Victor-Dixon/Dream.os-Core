from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from src.core.types import JsonDict, MessageStatus, TransportName


REQUIRED_FIELDS = (
    "id",
    "from",
    "to",
    "type",
    "body",
    "created_at",
    "status",
    "lease_owner",
    "lease_expires_at",
    "reply_to",
    "device_hint",
    "transport",
)


class MessageValidationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class BusMessage:
    from_agent: str
    to_agent: str
    msg_type: str
    body: str
    device_hint: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    status: MessageStatus = MessageStatus.NEW
    lease_owner: str | None = None
    lease_expires_at: str | None = None
    reply_to: str | None = None
    transport: TransportName = TransportName.FILESYSTEM
    meta: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.msg_type,
            "body": self.body,
            "created_at": self.created_at,
            "status": self.status.value,
            "lease_owner": self.lease_owner,
            "lease_expires_at": self.lease_expires_at,
            "reply_to": self.reply_to,
            "device_hint": self.device_hint,
            "transport": self.transport.value,
            "meta": self.meta,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def write_json(self, path: Path) -> None:
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def from_dict(cls, data: JsonDict) -> "BusMessage":
        cls.validate_dict(data)
        return cls(
            id=str(data["id"]),
            from_agent=str(data["from"]),
            to_agent=str(data["to"]),
            msg_type=str(data["type"]),
            body=str(data["body"]),
            created_at=str(data["created_at"]),
            status=MessageStatus(str(data["status"])),
            lease_owner=data["lease_owner"],
            lease_expires_at=data["lease_expires_at"],
            reply_to=data["reply_to"],
            device_hint=str(data["device_hint"]),
            transport=TransportName(str(data["transport"])),
            meta=dict(data.get("meta", {})),
        )

    @classmethod
    def from_json(cls, raw: str) -> "BusMessage":
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise MessageValidationError("message JSON must decode to object")
        return cls.from_dict(parsed)

    @staticmethod
    def validate_dict(data: JsonDict) -> None:
        missing = [key for key in REQUIRED_FIELDS if key not in data]
        if missing:
            raise MessageValidationError(f"missing required fields: {missing}")
        for key in ("id", "from", "to", "type", "body", "created_at", "status", "device_hint", "transport"):
            if not isinstance(data[key], str) or not data[key].strip():
                raise MessageValidationError(f"{key} must be a non-empty string")
        for key in ("lease_owner", "lease_expires_at", "reply_to"):
            if data[key] is not None and not isinstance(data[key], str):
                raise MessageValidationError(f"{key} must be null or string")
        if "meta" in data and not isinstance(data["meta"], dict):
            raise MessageValidationError("meta must be an object")
        try:
            uuid.UUID(data["id"])
        except ValueError as exc:
            raise MessageValidationError("id must be a UUID") from exc
        try:
            datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise MessageValidationError("created_at must be ISO-8601") from exc
        if data["status"] not in {s.value for s in MessageStatus}:
            raise MessageValidationError("invalid status")
        if data["transport"] not in {t.value for t in TransportName}:
            raise MessageValidationError("invalid transport")


def load_message(path: Path) -> BusMessage:
    return BusMessage.from_json(path.read_text(encoding="utf-8"))
