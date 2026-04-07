from __future__ import annotations

from pathlib import Path

import pytest

from scripts.ci.check_phase_status import extract_phase_status
from src.core.command_router_phase2 import CommandRouter
from src.core.inbox_listener import InboxListener
from src.core.message_pipeline import MessagePipeline, RetryPolicy
from src.core.phase2_contracts import CommandMessage, CommandResult, PipelineError


@pytest.mark.phase2
@pytest.mark.unit
def test_ocr_detector_normalizes_messages() -> None:
    text = "2026-04-06 12:00 @agent-2 sync repo=core"
    detected = InboxListener.simple_ocr_detector(text)
    assert detected == "@agent-2 sync repo=core"


@pytest.mark.phase2
@pytest.mark.integration
def test_file_tail_detects_new_input(tmp_path: Path) -> None:
    listener = InboxListener(ocr_detector=InboxListener.simple_ocr_detector)
    log = tmp_path / "inbox.log"
    log.write_text("skip this\n@agent-1 resume now\n", encoding="utf-8")

    first = listener.poll_file(log)
    assert len(first) == 1
    assert first[0].text == "@agent-1 resume now"

    log.write_text("skip this\n@agent-1 resume now\n@agent-1 sync all\n", encoding="utf-8")
    second = listener.poll_file(log)
    assert [m.text for m in second] == ["@agent-1 sync all"]


@pytest.mark.phase2
@pytest.mark.unit
def test_filter_excludes_irrelevant_messages() -> None:
    listener = InboxListener(
        ocr_detector=lambda line: line.strip(),
        message_filter=lambda msg: "sync" in msg.text,
    )
    messages = listener.consume_stream(["hello", "@agent-1 sync all"])
    assert [m.text for m in messages] == ["@agent-1 sync all"]


@pytest.mark.phase2
@pytest.mark.unit
def test_listener_emits_valid_inbound_message() -> None:
    listener = InboxListener(ocr_detector=InboxListener.simple_ocr_detector)
    messages = listener.consume_stream(["@agent-9 restart service"], source="runtime")
    assert len(messages) == 1
    inbound = messages[0]
    assert inbound.source == "runtime"
    assert inbound.channel == "ocr"
    assert inbound.message_id


@pytest.mark.phase2
@pytest.mark.unit
def test_routes_resume_sync_restart() -> None:
    router = CommandRouter()
    resume = router.route(CommandMessage(command="resume", args={"target": "worker"}, source_message_id="m1"))
    sync = router.route(CommandMessage(command="sync", args={"scope": "repo"}, source_message_id="m2"))
    restart = router.route(CommandMessage(command="restart", args={"target": "bridge"}, source_message_id="m3"))

    assert resume.status == "ok"
    assert sync.status == "ok"
    assert restart.status == "ok"


@pytest.mark.phase2
@pytest.mark.unit
def test_handles_unknown_command_safely() -> None:
    router = CommandRouter()
    result = router.route(CommandMessage(command="unknown", args={}, source_message_id="m4"))
    assert result.status == "ignored"
    assert "unknown command" in result.detail


@pytest.mark.phase2
@pytest.mark.unit
def test_supports_custom_registration() -> None:
    router = CommandRouter()

    def custom_handler(message: CommandMessage) -> CommandResult:
        return CommandResult(command=message.command, status="ok", detail="custom", data={"k": 1})

    router.register("ship", custom_handler)
    result = router.route(CommandMessage(command="ship", args={}, source_message_id="m5"))
    assert result.status == "ok"
    assert result.detail == "custom"


@pytest.mark.phase2
@pytest.mark.unit
def test_queue_accepts_messages_and_preserves_deterministic_order() -> None:
    pipeline = MessagePipeline()
    pipeline.enqueue(CommandMessage(command="a", args={}, source_message_id="1", priority=5))
    pipeline.enqueue(CommandMessage(command="b", args={}, source_message_id="2", priority=5))

    handled: list[str] = []

    def handler(message: CommandMessage) -> CommandResult:
        handled.append(message.command)
        return CommandResult(command=message.command, status="ok", detail="done")

    pipeline.process_all(handler)
    assert handled == ["a", "b"]


@pytest.mark.phase2
@pytest.mark.unit
def test_high_priority_preempts_low_priority() -> None:
    pipeline = MessagePipeline()
    pipeline.enqueue(CommandMessage(command="low", args={}, source_message_id="1", priority=50))
    pipeline.enqueue(CommandMessage(command="high", args={}, source_message_id="2", priority=1))

    order: list[str] = []

    def handler(message: CommandMessage) -> CommandResult:
        order.append(message.command)
        return CommandResult(command=message.command, status="ok", detail="done")

    pipeline.process_all(handler)
    assert order == ["high", "low"]


@pytest.mark.phase2
@pytest.mark.unit
def test_retries_transient_failures_and_succeeds() -> None:
    pipeline = MessagePipeline(retry_policy=RetryPolicy(max_retries=2))
    pipeline.enqueue(CommandMessage(command="sync", args={}, source_message_id="r1", priority=1))
    attempts = {"count": 0}

    def flaky_handler(message: CommandMessage) -> CommandResult:
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise PipelineError(stage="dispatch", reason="temporary", transient=True)
        return CommandResult(command=message.command, status="ok", detail="recovered")

    result = pipeline.process_next(flaky_handler)
    assert result.status == "ok"
    assert result.retries == 1


@pytest.mark.phase2
@pytest.mark.unit
def test_dead_letters_after_retry_limit() -> None:
    pipeline = MessagePipeline(retry_policy=RetryPolicy(max_retries=1))
    command = CommandMessage(command="sync", args={}, source_message_id="d1", priority=1)
    pipeline.enqueue(command)

    def failing_handler(_: CommandMessage) -> CommandResult:
        raise PipelineError(stage="dispatch", reason="still broken", transient=True)

    result = pipeline.process_next(failing_handler)
    assert result.status == "dead_lettered"
    assert len(pipeline.dead_letters) == 1


@pytest.mark.phase2
@pytest.mark.unit
def test_survives_handler_exception() -> None:
    pipeline = MessagePipeline()
    pipeline.enqueue(CommandMessage(command="restart", args={}, source_message_id="x1", priority=1))

    def broken_handler(_: CommandMessage) -> CommandResult:
        raise RuntimeError("boom")

    result = pipeline.process_next(broken_handler)
    assert result.status == "dead_lettered"
    assert "unhandled exception" in result.detail


@pytest.mark.phase2
@pytest.mark.contract
def test_phase_3_unlocks_when_phase_2_completed() -> None:
    status_text = Path("00_foundation/PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert extract_phase_status(status_text, 2) == "COMPLETED"
    assert extract_phase_status(status_text, 3) == "COMPLETED"


@pytest.mark.phase2
@pytest.mark.contract
def test_project_status_matches_actual_state() -> None:
    status_text = Path("00_foundation/PROJECT_STATUS.md").read_text(encoding="utf-8")
    required_items = [
        "InboxListener Path",
        "Command Router",
        "Message Processing Pipeline",
        "Reliability Enhancements",
        "Error Handling",
    ]
    for item in required_items:
        assert item in status_text


@pytest.mark.phase2
@pytest.mark.contract
def test_ci_fails_on_prerequisite_violation() -> None:
    ci_text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "needs: [phase2_full_listener_loop]" in ci_text
    assert "needs.phase2_full_listener_loop.result == 'success'" in ci_text
