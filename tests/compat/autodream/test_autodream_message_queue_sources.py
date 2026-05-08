from pathlib import Path

AUTO = Path.home() / "projects/AutoDream.Os"

SOURCES = [
    AUTO / "src/core/message_queue.py",
    AUTO / "src/core/message_queue_persistence.py",
    AUTO / "src/domain/ports/message_bus.py",
]

def test_autodream_message_sources_exist():
    for source in SOURCES:
        assert source.exists(), source

def test_autodream_message_queue_has_lifecycle_language():
    text = (AUTO / "src/core/message_queue.py").read_text(encoding="utf-8").lower()
    assert "pending" in text
    assert "processing" in text or "processed" in text
    assert "failed" in text

def test_autodream_message_bus_port_mentions_send_or_publish():
    text = (AUTO / "src/domain/ports/message_bus.py").read_text(encoding="utf-8").lower()
    assert "send" in text or "publish" in text or "message" in text
