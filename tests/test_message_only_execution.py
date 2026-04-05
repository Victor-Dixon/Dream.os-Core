from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dreamos.core.swarm import SwarmController
from dreamos.core.task_adapter import TaskAdapter
from src.core.execution_guard import InvalidExecutionPathError
from src.core.message import BusMessage
from src.core.types import MessageStatus


class StubSwarm:
    def execute_message(self, message: BusMessage):
        return [{"goal": message.body, "repos": message.meta.get("repos", []), "ok": True}]


def test_rejects_raw_dict_payload() -> None:
    adapter = TaskAdapter(StubSwarm())
    with pytest.raises(InvalidExecutionPathError):
        adapter.execute({"type": "task"})  # type: ignore[arg-type]


def test_accepts_bus_message_payload() -> None:
    adapter = TaskAdapter(StubSwarm())
    message = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="status",
        device_hint="worker",
        status=MessageStatus.RUNNING,
        meta={"repos": ["/repo/a"]},
    )
    result = adapter.execute(message)
    assert result.result is not None
    assert result.error is None


def test_no_public_direct_swarm_run_bypass() -> None:
    swarm = SwarmController(agents=[])
    with pytest.raises(InvalidExecutionPathError):
        swarm.run("status", ["/repo/a"])
