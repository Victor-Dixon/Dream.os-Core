from __future__ import annotations

from pathlib import Path

from dreamos.core.swarm import SwarmController
from dreamos.core.task_adapter import TaskAdapter
from src.relay.device_relay import DeviceRelay
from src.relay.sync_loop import run_sync_loop
from src.transports.file_transport import FileTransport


def main() -> None:
    transport = FileTransport(Path("agent-bus"), ["desktop", "laptop", "android"])
    swarm = SwarmController(agents=[])
    task_adapter = TaskAdapter(swarm)
    relay = DeviceRelay(node_id="laptop", transport=transport, task_adapter=task_adapter)
    run_sync_loop(relay, max_cycles=50, sleep_seconds=0.2)


if __name__ == "__main__":
    main()
