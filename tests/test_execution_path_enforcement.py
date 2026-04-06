from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage, load_message
from src.core.types import COMPLETE_DIR, MessageStatus
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


def test_task_message_requires_task_adapter(tmp_path: Path) -> None:
    transport = FileTransport(tmp_path, ["cli", "worker"])
    relay = DeviceRelay(node_id="worker", transport=transport, task_adapter=None)

    incoming = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="status",
        device_hint="worker",
        meta={"goal": "status", "repos": [str(tmp_path)]},
    )
    transport.send(incoming)

    processed = relay.poll_once()
    assert processed == 1

    completed = load_message(tmp_path / COMPLETE_DIR / f"worker__{incoming.id}.json")
    assert completed.status == MessageStatus.FAILED
    assert completed.error is not None
    assert "TaskAdapter is required" in completed.error


def test_orchestrator_import_is_scoped_to_agent_engine() -> None:
    project_root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []

    for py_file in project_root.rglob("*.py"):
        rel = py_file.relative_to(project_root).as_posix()
        if rel in {"src/execution/agent_engine.py", "tests/test_execution_path_enforcement.py"}:
            continue
        content = py_file.read_text(encoding="utf-8")
        if "dreamos_agent.agent.orchestrator" in content:
            offenders.append(rel)

    assert offenders == []
