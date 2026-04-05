from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage
from src.relay.device_relay import DeviceRelay
from src.relay.sync_loop import run_sync_loop
from src.transports.file_transport import FileTransport


def laptop_task_handler(message: BusMessage) -> BusMessage:
    return BusMessage(
        from_agent="laptop.relay",
        to_agent=message.from_agent,
        msg_type="result",
        body=f"laptop processed: {message.body}",
        device_hint="laptop",
        reply_to=message.id,
    )


def main() -> None:
    transport = FileTransport(Path("agent-bus"), ["desktop", "laptop", "android"])
    relay = DeviceRelay(node_id="laptop", transport=transport)
    relay.register_handler("task", laptop_task_handler)
    run_sync_loop(relay, max_cycles=50, sleep_seconds=0.2)


if __name__ == "__main__":
    main()
