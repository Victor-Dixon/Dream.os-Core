"""Adapter that executes task messages through swarm workflows."""

from __future__ import annotations

from typing import List, Optional

from src.core.execution_guard import (
    InvalidExecutionPathError,
    assert_execution_entrypoint,
    require_bus_message,
    validate_transition,
)
from src.core.message import BusMessage
from src.core.types import MessageStatus


class TaskAdapter:
    def __init__(self, swarm):
        self.swarm = swarm

    def can_handle(self, message: BusMessage) -> bool:
        return message.msg_type == "task"

    def execute(self, message: BusMessage, repos: Optional[List[str]] = None) -> BusMessage:
        assert_execution_entrypoint(source="TaskAdapter.execute", payload=message)
        validated = require_bus_message(message)
        if repos is not None:
            payload = validated.to_dict()
            payload["meta"] = dict(payload.get("meta") or {})
            payload["meta"]["repos"] = repos
            validated = BusMessage.from_dict(payload)
        return self.execute_bus_message(validated)

    def execute_bus_message(self, message: BusMessage) -> BusMessage:
        if not isinstance(message, BusMessage):
            raise InvalidExecutionPathError(
                "Execution rejected: execute_bus_message requires BusMessage."
            )

        payload = message.to_dict()
        goal = message.meta.get("goal") or message.body or "status"
        repos = message.meta.get("repos") or []
        if not repos and message.meta.get("repo"):
            repos = [message.meta["repo"]]

        try:
            result = self.swarm.execute_message(message, goal=goal, repos=repos)
            validate_transition(message.status.value, MessageStatus.COMPLETE.value)
            payload["status"] = MessageStatus.COMPLETE.value
            payload["result"] = {"goal": goal, "repos": repos, "results": result}
            payload["error"] = None
        except Exception as exc:
            validate_transition(message.status.value, MessageStatus.FAILED.value)
            payload["status"] = MessageStatus.FAILED.value
            payload["result"] = None
            payload["error"] = str(exc)

        return BusMessage.from_dict(payload)
