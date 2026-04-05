from __future__ import annotations

from pathlib import Path

from dreamos.core.task_adapter import TaskAdapter
from src.core.message import BusMessage, load_message
from src.core.types import COMPLETE_DIR, MessageStatus
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


class StubSwarm:
    def run(self, goal: str, repos: list[str]):
        return [{"goal": goal, "repos": repos, "ok": True}]


def test_message_to_swarm_execution_flow(tmp_path: Path) -> None:
    transport = FileTransport(tmp_path, ["cli", "worker"])
    adapter = TaskAdapter(StubSwarm())
    relay = DeviceRelay(node_id="worker", transport=transport, task_adapter=adapter)

    incoming = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="status",
        device_hint="worker",
        required_capabilities=["git"],
        routing_hints={"preferred_tags": ["desktop"]},
        meta={"goal": "status", "repos": ["/repo/a"]},
    )
    transport.send(incoming)

    processed = relay.poll_once()
    assert processed == 1

    complete_path = tmp_path / COMPLETE_DIR / f"worker__{incoming.id}.json"
    completed = load_message(complete_path)

    assert completed.status == MessageStatus.COMPLETE
    assert completed.result is not None
    assert completed.result.get("goal") == "status"
    assert completed.error is None
