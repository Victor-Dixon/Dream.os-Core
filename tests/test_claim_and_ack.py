from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage
from src.core.types import COMPLETE_DIR, INBOX_DIR
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


def test_claim_then_ack_moves_files(tmp_path: Path) -> None:
    transport = FileTransport(tmp_path, ["desktop", "laptop", "android"])
    incoming = BusMessage(
        from_agent="desktop.supervisor",
        to_agent="laptop",
        msg_type="task",
        body="run checks",
        device_hint="laptop",
    )
    transport.send(incoming)

    relay = DeviceRelay(node_id="laptop", transport=transport)
    processed = relay.poll_once()

    assert processed == 1
    assert not (tmp_path / INBOX_DIR / "laptop" / f"{incoming.id}.json").exists()
    assert (tmp_path / COMPLETE_DIR / f"laptop__{incoming.id}.json").exists()


def test_handler_emits_response(tmp_path: Path) -> None:
    transport = FileTransport(tmp_path, ["desktop", "laptop", "android"])
    incoming = BusMessage(
        from_agent="desktop",
        to_agent="android",
        msg_type="approve",
        body="review deployment",
        device_hint="android",
    )
    transport.send(incoming)

    relay = DeviceRelay(node_id="android", transport=transport)
    relay.register_handler(
        "approve",
        lambda message: BusMessage(
            from_agent="android",
            to_agent=message.from_agent,
            msg_type="approval",
            body="approved",
            device_hint="desktop",
            reply_to=message.id,
        ),
    )
    relay.poll_once()

    out = list((tmp_path / INBOX_DIR / "desktop").glob("*.json"))
    assert len(out) == 1
