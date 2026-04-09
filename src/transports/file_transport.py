from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage, load_message
from src.core.types import CLAIMED_DIR, COMPLETE_DIR, INBOX_DIR, ensure_bus_layout
from src.transports.base import Transport
from src.transports.envelope_middleware import assert_pre_routing_envelope


class FileTransport(Transport):
    def __init__(self, bus_root: Path, nodes: list[str]) -> None:
        self.bus_root = bus_root
        ensure_bus_layout(self.bus_root, nodes)

    def send(self, message: BusMessage) -> str:
        assert_pre_routing_envelope(message)
        target = self.bus_root / INBOX_DIR / message.to_agent / f"{message.id}.json"
        message.write_json(target)
        return str(target)

    def receive(self, node_id: str, limit: int = 10) -> list[BusMessage]:
        inbox = self.bus_root / INBOX_DIR / node_id
        files = sorted(inbox.glob("*.json"))[:limit]
        return [load_message(path) for path in files]

    def claim(self, message_id: str, node_id: str) -> Path:
        source = self.bus_root / INBOX_DIR / node_id / f"{message_id}.json"
        claimed = self._claimed_path(message_id, node_id)
        source.rename(claimed)
        return claimed

    def update_claimed(self, message: BusMessage, node_id: str) -> None:
        message.write_json(self._claimed_path(message.id, node_id))

    def ack(self, message_id: str, node_id: str) -> None:
        claimed = self._claimed_path(message_id, node_id)
        complete = self.bus_root / COMPLETE_DIR / f"{node_id}__{message_id}.json"
        claimed.rename(complete)

    def _claimed_path(self, message_id: str, node_id: str) -> Path:
        return self.bus_root / CLAIMED_DIR / f"{node_id}__{message_id}.json"
