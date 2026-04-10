from __future__ import annotations

import json
from pathlib import Path

from run import execute_closed_loop, validate_output


def test_closed_loop_retries_then_succeeds(tmp_path: Path) -> None:
    output_path = tmp_path / "output.json"

    exit_code = execute_closed_loop(
        task="compile report",
        max_retries=3,
        fail_attempts=2,
        output_path=output_path,
    )

    assert exit_code == 0
    is_valid, reason = validate_output(output_path)
    assert is_valid, reason

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["status"] == "success"
    assert payload["result"]["attempt"] == 3


def test_closed_loop_fails_when_retries_exhausted(tmp_path: Path) -> None:
    output_path = tmp_path / "output.json"

    exit_code = execute_closed_loop(
        task="compile report",
        max_retries=2,
        fail_attempts=2,
        output_path=output_path,
    )

    assert exit_code == 1
    is_valid, reason = validate_output(output_path)
    assert not is_valid
    assert reason == "missing required keys: ['result']"
