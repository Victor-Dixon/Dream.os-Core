from __future__ import annotations

import time

from src.relay.device_relay import DeviceRelay


def run_sync_loop(relay: DeviceRelay, max_cycles: int = 20, sleep_seconds: float = 0.1) -> int:
    processed = 0
    for _ in range(max_cycles):
        processed += relay.poll_once()
        time.sleep(sleep_seconds)
    return processed
