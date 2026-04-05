from __future__ import annotations

from dataclasses import dataclass, field

from src.core.message import BusMessage
from src.relay.claim_logic import claim_message, mark_complete, mark_running
from src.transports.file_transport import FileTransport


from typing import Callable


@dataclass
class DeviceRelay:
    node_id: str
    transport: FileTransport
    handlers: dict[str, Callable[[BusMessage], BusMessage | None]] = field(default_factory=dict)
    event_log: list[str] = field(default_factory=list)

    def register_handler(self, message_type: str, handler: Callable[[BusMessage], BusMessage | None]) -> None:
        self.handlers[message_type] = handler

    def poll_once(self) -> int:
        messages = self.transport.receive(self.node_id, limit=1)
        if not messages:
            return 0

        msg = messages[0]
        claimed = claim_message(msg, node_id=self.node_id)
        self.transport.claim(claimed.id, node_id=self.node_id)
        self.event_log.append(f"claimed:{claimed.id}")

        running = mark_running(claimed)
        response = self._handle(running)
        complete = mark_complete(running)
        self.transport.ack(complete.id, node_id=self.node_id)
        self.event_log.append(f"completed:{complete.id}")

        if response is not None:
            self.transport.send(response)
            self.event_log.append(f"response:{response.id}")
        return 1

    def _handle(self, message: BusMessage) -> BusMessage | None:
        handler = self.handlers.get(message.msg_type)
        if handler is None:
            return None
        return handler(message)
