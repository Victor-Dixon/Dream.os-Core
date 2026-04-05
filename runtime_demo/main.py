from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.message import BusMessage
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


def main() -> None:
    bus_root = PROJECT_ROOT / "runtime_demo" / "agent-bus"
    transport = FileTransport(bus_root, ["desktop", "laptop", "android"])

    desktop = DeviceRelay("desktop", transport)
    laptop = DeviceRelay("laptop", transport)

    laptop.register_handler(
        "task",
        lambda message: BusMessage(
            from_agent="laptop",
            to_agent=message.from_agent,
            msg_type="result",
            body=f"done: {message.body}",
            device_hint="desktop",
            reply_to=message.id,
        ),
    )

    transport.send(
        BusMessage(
            from_agent="desktop",
            to_agent="laptop",
            msg_type="task",
            body="run scanner tests",
            device_hint="laptop",
        )
    )

    laptop.poll_once()
    desktop.poll_once()
    print("desktop log", desktop.event_log)
    print("laptop log", laptop.event_log)


if __name__ == "__main__":
    main()
