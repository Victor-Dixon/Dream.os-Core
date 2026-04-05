from __future__ import annotations

from dataclasses import dataclass, field

from src.core.message import BusMessage
from src.core.types import MessageStatus
from src.relay.claim_logic import claim_message, mark_complete, mark_failed, mark_running
from src.transports.file_transport import FileTransport

from dreamos.core.task_adapter import TaskAdapter

from typing import Callable


@dataclass
class DeviceRelay:
    node_id: str
    transport: FileTransport
    task_adapter: TaskAdapter | None = None
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
        handled = self._handle(running)
        is_task_execution = running.msg_type == "task" and self.task_adapter is not None
        if handled is None:
            final_message = mark_complete(running)
            response = None
        else:
            response = None if is_task_execution else handled
            if handled.status == MessageStatus.FAILED:
                final_message = handled
            elif handled.status == MessageStatus.COMPLETE:
                final_message = handled
            else:
                final_message = mark_complete(handled)

        self.transport.update_claimed(final_message, node_id=self.node_id)
        self.transport.ack(final_message.id, node_id=self.node_id)
        self.event_log.append(f"completed:{final_message.id}")

        if response is not None:
            self.transport.send(response)
            self.event_log.append(f"response:{response.id}")
        return 1

    def _handle(self, message: BusMessage) -> BusMessage | None:
        if self.task_adapter and self.task_adapter.can_handle(message.to_dict()):
            try:
                return self.task_adapter.execute_bus_message(message)
            except Exception as exc:
                return mark_failed(message, str(exc))
        handler = self.handlers.get(message.msg_type)
        if handler is None:
            return None
        return handler(message)
