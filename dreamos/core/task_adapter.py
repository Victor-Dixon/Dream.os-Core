"""Adapter that executes task messages through swarm workflows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.message import BusMessage
from src.core.types import MessageStatus


class TaskAdapter:
    def __init__(self, swarm):
        self.swarm = swarm

    def can_handle(self, message: Dict[str, Any]) -> bool:
        return message.get("type") == "task"

    def execute(self, message: Dict[str, Any], repos: Optional[List[str]] = None) -> Dict[str, Any]:
        payload = message.get("payload", {})
        goal = payload.get("goal", "status")
        target_repos = repos if repos is not None else ([payload["repo"]] if payload.get("repo") else [])
        result = self.swarm.run(goal, target_repos)
        return {"status": "completed", "result": result}

    def execute_bus_message(self, message: BusMessage) -> BusMessage:
        payload = message.to_dict()
        goal = message.meta.get("goal") or message.body or "status"
        repos = message.meta.get("repos") or []
        if not repos and message.meta.get("repo"):
            repos = [message.meta["repo"]]
        try:
            result = self.swarm.run(goal, repos)
            payload["status"] = MessageStatus.COMPLETE.value
            payload["result"] = {"goal": goal, "repos": repos, "results": result}
            payload["error"] = None
        except Exception as exc:
            payload["status"] = MessageStatus.FAILED.value
            payload["result"] = None
            payload["error"] = str(exc)
        return BusMessage.from_dict(payload)
