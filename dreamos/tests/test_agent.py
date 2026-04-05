"""tests/test_agent.py"""

import pytest
from unittest.mock import MagicMock, patch
from dreamos.core.agent import BaseAgent, CognitiveAgent, AgentStats
from dreamos.tools.base import ToolRegistry, ToolResult


def make_registry(*tool_names):
    registry = MagicMock(spec=ToolRegistry)
    registry.__contains__ = lambda self, name: name in tool_names
    registry.run.return_value = ToolResult(ok=True, output="done")
    return registry


class TestAgentStats:
    def test_success_rate_zero_tasks(self):
        s = AgentStats()
        assert s.success_rate == 0.0

    def test_success_rate(self):
        s = AgentStats(tasks=4, successes=3)
        assert s.success_rate == 0.75

    def test_bar_length(self):
        s = AgentStats(tasks=10, successes=10)
        assert len(s.bar()) == 10
        assert "░" not in s.bar()


class TestBaseAgent:
    def setup_method(self):
        self.registry = make_registry("pull", "status")
        self.agent = BaseAgent("TestBot", ["pull", "status"], self.registry)

    def test_can_handle_known_tool(self):
        assert self.agent.can_handle("pull") is True

    def test_can_handle_unknown_tool(self):
        assert self.agent.can_handle("lint") is False

    def test_bid_zero_for_unknown_tool(self):
        assert self.agent.bid("lint", "/repo/x") == 0.0

    def test_bid_positive_for_known_tool(self):
        bid = self.agent.bid("pull", "/repo/x")
        assert 0.0 < bid <= 1.0

    def test_bid_decreases_with_load(self):
        bid1 = self.agent.bid("pull", "/repo/x")
        self.agent.stats.tasks = 10
        bid2 = self.agent.bid("pull", "/repo/x")
        assert bid2 < bid1

    def test_execute_dry_run(self):
        result = self.agent.execute("pull", "/repo/x", dry_run=True)
        assert result["ok"] is True
        assert self.agent.stats.tasks == 1
        assert self.agent.stats.successes == 1
        self.registry.run.assert_not_called()

    def test_execute_live(self):
        result = self.agent.execute("pull", "/repo/x", dry_run=False)
        assert result["ok"] is True
        self.registry.run.assert_called_once_with("pull", "/repo/x")

    def test_execute_failure_tracked(self):
        self.registry.run.return_value = ToolResult(ok=False, error="network error")
        result = self.agent.execute("pull", "/repo/x", dry_run=False)
        assert result["ok"] is False
        assert self.agent.stats.failures == 1


class TestCognitiveAgent:
    def setup_method(self):
        self.registry = make_registry("pull")
        self.rag = MagicMock()
        self.rag.get_context.return_value = {"warnings": [], "related": [], "similar_events": []}
        self.rag.recall_repo_affinity.return_value = 0.8
        self.agent = CognitiveAgent("CogBot", ["pull"], self.registry, self.rag)

    def test_queries_rag_before_execute(self):
        self.agent.execute("pull", "/repo/x", dry_run=True)
        self.rag.get_context.assert_called_once_with("/repo/x", "pull")
        assert self.agent.stats.rag_queries == 1

    def test_learns_after_live_execute(self):
        self.agent.execute("pull", "/repo/x", dry_run=False, goal="update")
        self.rag.learn.assert_called_once()

    def test_no_learn_on_dry_run(self):
        self.agent.execute("pull", "/repo/x", dry_run=True)
        self.rag.learn.assert_not_called()

    def test_rag_warning_logged(self, caplog):
        self.rag.get_context.return_value = {
            "warnings": ["pull failed 3x on this repo"],
            "related": [],
            "similar_events": [],
        }
        with caplog.at_level("WARNING"):
            self.agent.execute("pull", "/repo/x", dry_run=True)
        assert any("recalls" in r.message for r in caplog.records)

    def test_bid_uses_rag_affinity(self):
        bid = self.agent.bid("pull", "/repo/x")
        self.rag.recall_repo_affinity.assert_called_with("/repo/x", "CogBot")
        assert bid > 0
