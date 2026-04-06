from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import heapq
from typing import Any

from src.core.phase2_contracts import CommandMessage, CommandResult, PipelineError


@dataclass(slots=True)
class RetryPolicy:
    max_retries: int = 2


class MessagePipeline:
    """Priority queue pipeline with deterministic ordering and recovery flow."""

    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self.retry_policy = retry_policy or RetryPolicy()
        self._queue: list[tuple[int, int, CommandMessage]] = []
        self._counter = 0
        self.dead_letters: list[tuple[CommandMessage, PipelineError]] = []

    def enqueue(self, message: CommandMessage) -> None:
        heapq.heappush(self._queue, (message.priority, self._counter, message))
        self._counter += 1

    def has_messages(self) -> bool:
        return bool(self._queue)

    def process_next(
        self,
        handler: Callable[[CommandMessage], CommandResult],
    ) -> CommandResult:
        if not self._queue:
            raise PipelineError(stage="dequeue", reason="queue is empty", transient=False)

        _, _, message = heapq.heappop(self._queue)
        return self._dispatch_with_recovery(message, handler)

    def _dispatch_with_recovery(
        self,
        message: CommandMessage,
        handler: Callable[[CommandMessage], CommandResult],
    ) -> CommandResult:
        attempts = 0
        while True:
            try:
                result = handler(message)
                return CommandResult(
                    command=result.command,
                    status=result.status,
                    detail=result.detail,
                    retries=attempts,
                    data=dict(result.data),
                )
            except PipelineError as err:
                attempts += 1
                if err.transient and attempts <= self.retry_policy.max_retries:
                    continue
                self.dead_letters.append((message, err))
                return CommandResult(
                    command=message.command,
                    status="dead_lettered",
                    detail=str(err),
                    retries=attempts,
                    data={"stage": err.stage, "transient": err.transient},
                )
            except Exception as exc:  # structured conversion for unknown handler errors
                wrapped = PipelineError(
                    stage="handler",
                    reason=f"unhandled exception: {exc}",
                    transient=False,
                    message_id=message.source_message_id,
                )
                self.dead_letters.append((message, wrapped))
                return CommandResult(
                    command=message.command,
                    status="dead_lettered",
                    detail=str(wrapped),
                    retries=attempts,
                    data={"stage": wrapped.stage, "transient": wrapped.transient},
                )

    def process_all(
        self,
        handler: Callable[[CommandMessage], CommandResult],
    ) -> list[CommandResult]:
        results: list[CommandResult] = []
        while self._queue:
            results.append(self.process_next(handler))
        return results

    def snapshot(self) -> list[dict[str, Any]]:
        return [
            {
                "priority": priority,
                "sequence": sequence,
                "command": message.command,
                "source_message_id": message.source_message_id,
            }
            for priority, sequence, message in sorted(self._queue)
        ]
