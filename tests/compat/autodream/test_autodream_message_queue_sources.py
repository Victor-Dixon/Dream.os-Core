from pathlib import Path

import pytest

AUTO = Path.home() / "projects/AutoDream.Os"

pytestmark = pytest.mark.skipif(
    not AUTO.exists(),
    reason="AutoDream.Os absent; see _ops/reports/autodream_absorption_closure.md",
)


def test_autodream_message_sources_exist():
    expected = [
        AUTO / "src/application/queues/message_queue.py",
        AUTO / "src/domain/ports/message_bus.py",
    ]
    assert [path for path in expected if path.exists()]


def test_autodream_message_queue_has_lifecycle_language():
    text = (AUTO / "src/application/queues/message_queue.py").read_text(encoding="utf-8").lower()
    assert "pending" in text
    assert "processing" in text
    assert "completed" in text or "failed" in text


def test_autodream_message_bus_port_mentions_send_or_publish():
    text = (AUTO / "src/domain/ports/message_bus.py").read_text(encoding="utf-8").lower()
    assert "send" in text or "publish" in text
