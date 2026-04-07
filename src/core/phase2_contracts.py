from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True, slots=True)
class InboundMessage:
    source: str
    text: str
    channel: str = "ocr"
    priority: int = 100
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CommandMessage:
    command: str
    args: dict[str, Any]
    source_message_id: str
    priority: int = 100


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: str
    status: str
    detail: str
    retries: int = 0
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PipelineError(Exception):
    stage: str
    reason: str
    transient: bool = False
    message_id: str | None = None

    def __str__(self) -> str:
        msg = f"[{self.stage}] {self.reason}"
        if self.message_id:
            msg = f"{msg} (message={self.message_id})"
        return msg
