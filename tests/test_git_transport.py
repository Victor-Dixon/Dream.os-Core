from __future__ import annotations

from pathlib import Path

from src.core.message import BusMessage
from src.transports.git_transport import GitTransport


class FakeGitTransport(GitTransport):
    def __init__(self, bus_root: Path, nodes: list[str]) -> None:
        super().__init__(bus_root, nodes)
        self.commands: list[list[str]] = []

    def _run(self, cmd: list[str]) -> str:
        self.commands.append(cmd)
        if cmd[:3] == ["git", "status", "--porcelain"]:
            return "M inbox/desktop/x.json\n"
        return ""


def test_git_transport_send_triggers_sync(tmp_path: Path) -> None:
    transport = FakeGitTransport(tmp_path, ["desktop", "laptop", "android"])
    msg = BusMessage(
        from_agent="desktop",
        to_agent="laptop",
        msg_type="task",
        body="sync me",
        device_hint="laptop",
    )
    transport.send(msg)

    assert ["git", "pull", "--rebase", "origin", "main"] in transport.commands
    assert ["git", "push", "origin", "main"] in transport.commands
