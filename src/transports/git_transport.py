from __future__ import annotations

from pathlib import Path
import subprocess

from src.core.message import BusMessage
from src.transports.file_transport import FileTransport


class GitTransport(FileTransport):
    def __init__(self, bus_root: Path, nodes: list[str], remote: str = "origin", branch: str = "main") -> None:
        super().__init__(bus_root=bus_root, nodes=nodes)
        self.remote = remote
        self.branch = branch

    def sync(self, commit_message: str) -> None:
        self._run(["git", "pull", "--rebase", self.remote, self.branch])
        self._run(["git", "add", "."])
        status = self._run(["git", "status", "--porcelain"]).strip()
        if status:
            self._run(["git", "commit", "-m", commit_message])
            self._run(["git", "push", self.remote, self.branch])

    def _run(self, cmd: list[str]) -> str:
        proc = subprocess.run(
            cmd,
            cwd=self.bus_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout

    def send(self, message: BusMessage) -> str:
        stored = super().send(message)
        self.sync(f"bus: send {message.id}")
        return stored

    def ack(self, message_id: str, node_id: str) -> None:
        super().ack(message_id=message_id, node_id=node_id)
        self.sync(f"bus: ack {message_id}")
