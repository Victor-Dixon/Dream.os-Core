"""Transport pre-routing envelope validation."""

from __future__ import annotations

import pytest

from src.core.message import BusMessage, MessageValidationError
from src.transports.file_transport import FileTransport


def test_file_transport_send_rejects_invalid_envelope(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_to_dict = BusMessage.to_dict

    def bad_to_dict(self: BusMessage):
        d = real_to_dict(self)
        d["unexpected_field"] = True
        return d

    monkeypatch.setattr(BusMessage, "to_dict", bad_to_dict)
    transport = FileTransport(tmp_path, ["cli", "worker"])
    msg = BusMessage(
        from_agent="cli",
        to_agent="worker",
        msg_type="task",
        body="scan",
        device_hint="worker",
    )
    with pytest.raises(MessageValidationError, match="envelope schema|Additional properties"):
        transport.send(msg)
