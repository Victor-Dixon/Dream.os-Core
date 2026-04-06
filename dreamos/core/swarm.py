"""core/swarm.py — SwarmController: routes bus-task execution through AgentEngine."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from src.core.execution_guard import assert_execution_entrypoint, require_bus_message
from src.execution.agent_engine import AgentEngine

from ..config.settings import SETTINGS
from ..logging.logger import log
from ..plans.veto import VetoEngine
from ..tools.base import ToolRegistry
from .routing import RoutingDecision, RoutingPolicy


class SwarmController:
    def __init__(
        self,
        agents: list,
        rag=None,
        tool_registry: Optional[ToolRegistry] = None,
        settings=None,
        agent_engine: Optional[AgentEngine] = None,
    ):
        self.agents = agents
        self.rag = rag
        self.registry = tool_registry
        self.settings = settings or SETTINGS
        self.veto = VetoEngine()
        self.agent_engine = agent_engine or AgentEngine()
        self._results: List[Dict[str, Any]] = []

    def _negotiate(self, tool: str, repo: str) -> Optional[Any]:
        capable = [a for a in self.agents if a.can_handle(tool)]
        if not capable:
            log.warning(f"No agent can handle tool: {tool}")
            return None
        return max(capable, key=lambda a: a.bid(tool, repo, self.rag))

    def route_score(
        self,
        node_id: str,
        goal: str,
        repo: Optional[str],
        required_capabilities: List[str],
    ) -> float:
        if not self.rag or not hasattr(self.rag, "memory"):
            return 0.5
        memory = self.rag.memory
        goal_aff = memory.goal_affinity(node_id, goal) if hasattr(memory, "goal_affinity") else 0.5
        repo_aff = memory.route_affinity(node_id, repo) if hasattr(memory, "route_affinity") else 0.5
        capability_bonus = min(len(required_capabilities) * 0.05, 0.25) if required_capabilities else 0.0
        avoid_penalty = 0.0
        if repo and "lint" in (goal or "").lower() and memory.should_avoid("lint", repo, self.settings.max_retries):
            avoid_penalty = 0.5
        return (goal_aff * 0.5) + (repo_aff * 0.5) + capability_bonus - avoid_penalty

    def advise_route(self, message: Dict[str, Any], nodes: List[Any]) -> RoutingDecision:
        policy = RoutingPolicy(swarm=self, nodes=nodes)
        return policy.route(message)

    def execute_message(
        self,
        message,
        *,
        goal: str | None = None,
        repos: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        validated = require_bus_message(message)
        final_goal = goal or validated.meta.get("goal") or validated.body or "status"
        final_repos = repos or validated.meta.get("repos") or []
        if not final_repos and validated.meta.get("repo"):
            final_repos = [validated.meta["repo"]]
        return self.run(final_goal, final_repos, _internal=True)

    def _run_repo(self, goal: str, repo: str) -> Optional[Dict[str, Any]]:
        repo_label = os.path.basename(repo)

        if not self.settings.repo_is_safe(repo):
            log.warning(f"⛔ Blocked — {repo_label} not in allowlist")
            return None

        if self.rag and self.rag.memory.should_avoid("execute", repo, self.settings.max_retries):
            log.warning(f"⚠️  Skipping {repo_label} (repeated failures)")
            return None

        result = self.agent_engine.run(goal=goal, repo=repo)
        if not result.get("ok"):
            self.veto.record_failure("execute", repo)
        return result

    def run(self, goal: str, repos: List[str], *, _internal: bool = False) -> List[Dict[str, Any]]:
        assert_execution_entrypoint(
            source="SwarmController.run",
            internal_only=True,
            internal_call=_internal,
        )
        self._results.clear()

        if not repos:
            return []

        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as pool:
            futures = {pool.submit(self._run_repo, goal, repo): repo for repo in repos}
            for future in as_completed(futures):
                repo = futures[future]
                try:
                    result = future.result()
                    if result is not None:
                        self._results.append(result)
                except Exception as exc:
                    log.error(f"Unhandled engine error on {repo}: {exc}")

        return list(self._results)
