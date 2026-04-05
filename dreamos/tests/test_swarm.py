"""tests/test_swarm.py"""

import pytest
from unittest.mock import MagicMock, patch
from dreamos.core.swarm import SwarmController
from dreamos.core.agent import BaseAgent
from dreamos.tools.base import ToolRegistry, ToolResult
from dreamos.config.settings import Settings


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
        )

    def test_negotiate_finds_capable_agent(self):
        agent = self.swarm._negotiate("pull", "/repo/x")
        assert agent is self.agent

    def test_negotiate_returns_none_for_unknown_tool(self):
        agent = self.swarm._negotiate("lint", "/repo/x")
        assert agent is None

    def test_run_returns_results(self):
        results = self.swarm.run("status", ["/repo/x"])
        assert isinstance(results, list)

    def test_blocked_repo_skipped(self):
        self.settings.safe_repos = ["allowed"]
        results = self.swarm.run("status", ["/repo/blocked_thing"])
        assert results == []

    def test_allowed_repo_runs(self):
        self.settings.safe_repos = ["myrepo"]
        results = self.swarm.run("status", ["/home/user/myrepo"])
        assert len(results) >= 1

    def test_veto_blocks_downstream(self):
        # Record a lint failure
        self.swarm.veto.record_failure("lint", "/repo/x")
        # commit should now be vetoed
        assert self.swarm.veto.is_vetoed("commit", "/repo/x") is True

    def test_multiple_repos_all_run(self):
        repos = [f"/repo/project{i}" for i in range(3)]
        results = self.swarm.run("status", repos)
        assert len(results) == 3

    def test_memory_avoid_skips_repo(self):
        rag = MagicMock()
        rag.memory.should_avoid.return_value = True
        rag.recall_repo_affinity.return_value = 0.5
        swarm = SwarmController(
            agents=[self.agent],
            rag=rag,
            settings=self.settings,
        )
        results = swarm.run("status", ["/repo/x"])
        assert results == []


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
