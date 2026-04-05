from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, TypeAlias


JsonDict: TypeAlias = Dict[str, Any]


class MessageStatus(str, Enum):
    NEW = "new"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    EXPIRED = "expired"


class TransportName(str, Enum):
    FILESYSTEM = "filesystem"
    GIT = "git"
    MANUAL_CLIPBOARD = "manual_clipboard"


INBOX_DIR = "inbox"
OUTBOX_DIR = "outbox"
CLAIMED_DIR = "claimed"
COMPLETE_DIR = "complete"
FAILED_DIR = "failed"
LOGS_DIR = "logs"


BUS_DIRS = (INBOX_DIR, OUTBOX_DIR, CLAIMED_DIR, COMPLETE_DIR, FAILED_DIR, LOGS_DIR)


def ensure_bus_layout(root: Path, nodes: list[str]) -> None:
    for dirname in BUS_DIRS:
        (root / dirname).mkdir(parents=True, exist_ok=True)
    for node in nodes:
        (root / INBOX_DIR / node).mkdir(parents=True, exist_ok=True)
