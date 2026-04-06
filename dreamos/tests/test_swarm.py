"""tests/test_swarm.py"""

from unittest.mock import MagicMock

from dreamos.config.settings import Settings
from dreamos.core.agent import BaseAgent
from dreamos.core.swarm import SwarmController
from dreamos.tools.base import ToolRegistry, ToolResult


class StubAgentEngine:
    def __init__(self):
        self.calls = []

    def run(self, goal: str, repo: str):
        self.calls.append((goal, repo))
        return {"ok": True, "goal": goal, "repo": repo, "engine": "stub"}


def make_settings(**kwargs):
    s = Settings()
    s.dry_run = kwargs.get("dry_run", True)
    s.max_workers = kwargs.get("max_workers", 2)
    s.max_retries = kwargs.get("max_retries", 2)
    s.safe_repos = kwargs.get("safe_repos", [])
    s.dangerous_tools = kwargs.get("dangerous_tools", ["push", "commit"])
    return s


def make_agent(name, tools, ok=True):
    registry = MagicMock(spec=ToolRegistry)
    registry.run.return_value = ToolResult(ok=ok, output="ok")
    agent = BaseAgent(name, tools, registry)
    return agent


class TestSwarmController:
    def setup_method(self):
        self.settings = make_settings(dry_run=True)
        self.agent = make_agent("GitMaster", ["pull", "status"])
        self.swarm = SwarmController(
            agents=[self.agent],
            settings=self.settings,
            agent_engine=StubAgentEngine(),
        )

    def test_run_returns_results(self):
        results = self.swarm.run("status", ["/repo/x"], _internal=True)
        assert isinstance(results, list)

    def test_dry_run_skips_agent_engine_execution(self):
        results = self.swarm.run("status", ["/repo/x"], _internal=True)
        assert len(results) == 1
        assert results[0]["engine"] == "dry-run"
        assert results[0]["dry_run"] is True
        assert self.swarm.agent_engine.calls == []

    def test_blocked_repo_skipped(self):
        self.settings.safe_repos = ["allowed"]
        results = self.swarm.run("status", ["/repo/blocked_thing"], _internal=True)
        assert results == []

    def test_allowed_repo_runs(self):
        self.settings.safe_repos = ["myrepo"]
        results = self.swarm.run("status", ["/home/user/myrepo"], _internal=True)
        assert len(results) >= 1

    def test_veto_blocks_downstream(self):
        self.swarm.veto.record_failure("lint", "/repo/x")
        assert self.swarm.veto.is_vetoed("commit", "/repo/x") is True

    def test_multiple_repos_all_run(self):
        repos = [f"/repo/project{i}" for i in range(3)]
        results = self.swarm.run("status", repos, _internal=True)
        assert len(results) == 3

    def test_memory_avoid_skips_repo(self):
        rag = MagicMock()
        rag.memory.should_avoid.return_value = True
        rag.memory.recall_repo_affinity.return_value = 0.5
        swarm = SwarmController(
            agents=[self.agent],
            rag=rag,
            settings=self.settings,
            agent_engine=StubAgentEngine(),
        )
        results = swarm.run("status", ["/repo/x"], _internal=True)
        assert results == []

    def test_route_score_uses_memory_signals(self):
        rag = MagicMock()
        rag.memory.goal_affinity.return_value = 0.8
        rag.memory.route_affinity.return_value = 0.6
        rag.memory.should_avoid.return_value = False
        swarm = SwarmController(
            agents=[self.agent],
            rag=rag,
            settings=self.settings,
            agent_engine=StubAgentEngine(),
        )
        score = swarm.route_score(
            node_id="desktop-main",
            goal="fix lint",
            repo="/repo/x",
            required_capabilities=["git", "lint"],
        )
        assert score > 0.0

    def test_advise_route_returns_routing_decision(self):
        from dreamos.core.routing import NodeProfile

        rag = MagicMock()
        rag.memory.goal_affinity.return_value = 0.7
        rag.memory.route_affinity.return_value = 0.7
        rag.memory.should_avoid.return_value = False
        swarm = SwarmController(
            agents=[self.agent],
            rag=rag,
            settings=self.settings,
            agent_engine=StubAgentEngine(),
        )
        decision = swarm.advise_route(
            message={
                "payload": {"goal": "status", "repo": "/repo/x"},
                "required_capabilities": ["pull"],
            },
            nodes=[NodeProfile("desktop-main", ["pull"])],
        )
        assert decision.rejected is False
        assert decision.node_id == "desktop-main"


class TestVetoIntegration:
    def test_failing_lint_blocks_commit(self):
        from dreamos.plans.veto import VetoEngine

        veto = VetoEngine()
        veto.record_failure("lint", "/repo/x")
        assert veto.is_vetoed("commit", "/repo/x") is True
        assert veto.is_vetoed("push", "/repo/x") is True

    def test_passing_lint_does_not_block(self):
        from dreamos.plans.veto import VetoEngine

        veto = VetoEngine()
        assert veto.is_vetoed("commit", "/repo/x") is False

    def test_reset_clears_veto(self):
        from dreamos.plans.veto import VetoEngine

        veto = VetoEngine()
        veto.record_failure("lint", "/repo/x")
        veto.reset("/repo/x")
        assert veto.is_vetoed("commit", "/repo/x") is False
