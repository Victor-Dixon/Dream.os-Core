from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage, load_message
from src.core.types import CLAIMED_DIR, COMPLETE_DIR, INBOX_DIR, ensure_bus_layout
from src.transports.base import Transport


class FileTransport(Transport):
    def __init__(self, bus_root: Path, nodes: list[str]) -> None:
        self.bus_root = bus_root
        ensure_bus_layout(self.bus_root, nodes)

    def send(self, message: BusMessage) -> str:
        target = self.bus_root / INBOX_DIR / message.to_agent / f"{message.id}.json"
        message.write_json(target)
        return str(target)

    def receive(self, node_id: str, limit: int = 10) -> list[BusMessage]:
        inbox = self.bus_root / INBOX_DIR / node_id
        files = sorted(inbox.glob("*.json"))[:limit]
        return [load_message(path) for path in files]

    def claim(self, message_id: str, node_id: str) -> Path:
        source = self.bus_root / INBOX_DIR / node_id / f"{message_id}.json"
        claimed = self.bus_root / CLAIMED_DIR / f"{node_id}__{message_id}.json"
        source.rename(claimed)
        return claimed

    def ack(self, message_id: str, node_id: str) -> None:
        claimed = self.bus_root / CLAIMED_DIR / f"{node_id}__{message_id}.json"
        complete = self.bus_root / COMPLETE_DIR / f"{node_id}__{message_id}.json"
        claimed.rename(complete)
