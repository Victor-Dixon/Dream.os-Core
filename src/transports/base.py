from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.message import BusMessage


class Transport(ABC):
    @abstractmethod
    def send(self, message: BusMessage) -> str:
        """Persist a message and return its storage id/path."""

    @abstractmethod
    def receive(self, node_id: str, limit: int = 10) -> list[BusMessage]:
        """Return pending messages for a node without deleting them."""

    @abstractmethod
    def ack(self, message_id: str, node_id: str) -> None:
        """Mark a message completed for a node."""
