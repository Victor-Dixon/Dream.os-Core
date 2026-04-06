from __future__ import annotations

from pathlib import Path

from dreamos.core.swarm import SwarmController
from dreamos.core.task_adapter import TaskAdapter
from src.core.message import BusMessage, load_message
from src.core.types import COMPLETE_DIR, MessageStatus
from src.execution.agent_engine import AgentEngine
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


class FakeOrchestrator:
    initialized = False
    last_query = ""

    def __init__(self, workspace: str, model: str, verbose: bool):
        self.workspace = workspace
        self.model = model
        self.verbose = verbose

    def initialize(self):
        FakeOrchestrator.initialized = True
        return self

    def answer(self, query: str) -> str:
        FakeOrchestrator.last_query = query
        return f"executed:{query}"


def test_full_execution_flow_with_agent_engine(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(AgentEngine, "_load_orchestrator_class", lambda self: FakeOrchestrator)

    transport = FileTransport(tmp_path, ["cli", "worker"])
    engine = AgentEngine(verbose=False)
    swarm = SwarmController(agents=[], agent_engine=engine)
    adapter = TaskAdapter(swarm)
    relay = DeviceRelay(node_id="worker", transport=transport, task_adapter=adapter)

    incoming = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="status",
        device_hint="worker",
        meta={"goal": "scan architecture", "repos": [str(tmp_path)]},
    )
    transport.send(incoming)

    processed = relay.poll_once()
    assert processed == 1

    completed_path = tmp_path / COMPLETE_DIR / f"worker__{incoming.id}.json"
    completed = load_message(completed_path)

    assert FakeOrchestrator.initialized is True
    assert FakeOrchestrator.last_query == "scan architecture"
    assert completed.status == MessageStatus.COMPLETE
    assert completed.result is not None
    assert completed.result["results"][0]["engine"] == "dreamos_agent.orchestrator"
