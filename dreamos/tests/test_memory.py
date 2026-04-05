"""tests/test_memory.py"""

import pytest
import tempfile
import json
from pathlib import Path
from dreamos.core.memory import Memory, VectorMemory, KnowledgeGraph, RAGEngine


class TestMemory:
    def setup_method(self):
        self.mem = Memory()

    def _record(self, ok=True, tool="pull", repo="/repo/a", worker="GitMaster"):
        self.mem.record("test goal", tool, repo, {"ok": ok}, worker)

    def test_record_success(self):
        self._record(ok=True)
        assert self.mem.summary()["total_actions"] == 1
        assert self.mem.summary()["successes"] == 1

    def test_record_failure_increments_pattern(self):
        self._record(ok=False)
        assert self.mem.failure_count("pull", "/repo/a") == 1

    def test_affinity_neutral_no_history(self):
        assert self.mem.affinity("/repo/x", "agent") == 0.5

    def test_affinity_all_success(self):
        for _ in range(4):
            self._record(ok=True)
        assert self.mem.affinity("/repo/a", "GitMaster") == 1.0

    def test_affinity_mixed(self):
        self._record(ok=True)
        self._record(ok=False)
        assert self.mem.affinity("/repo/a", "GitMaster") == 0.5

    def test_should_avoid_below_threshold(self):
        self._record(ok=False)
        assert self.mem.should_avoid("pull", "/repo/a", threshold=2) is False

    def test_should_avoid_at_threshold(self):
        self._record(ok=False)
        self._record(ok=False)
        assert self.mem.should_avoid("pull", "/repo/a", threshold=2) is True

    def test_recent_returns_last_n(self):
        for i in range(10):
            self._record(ok=True, repo=f"/repo/{i}")
        assert len(self.mem.recent(5)) == 5

    def test_persistence(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        mem1 = Memory(persist_path=path)
        mem1.record("goal", "pull", "/repo/a", {"ok": True}, "agent")
        mem2 = Memory(persist_path=path)
        assert mem2.summary()["total_actions"] == 1

    def test_route_affinity_neutral_without_history(self):
        assert self.mem.route_affinity("desktop-main", "/repo/a") == 0.5

    def test_goal_affinity_updates_from_node_records(self):
        self.mem.record("fix lint", "lint", "/repo/a", {"ok": True}, "agent", node_id="desktop-main")
        self.mem.record("fix lint", "lint", "/repo/a", {"ok": False}, "agent", node_id="desktop-main")
        assert self.mem.goal_affinity("desktop-main", "fix lint") == 0.5


class TestVectorMemory:
    def setup_method(self):
        self.vm = VectorMemory()

    def test_add_and_query(self):
        self.vm.add("pull failed on myrepo", metadata={"tool": "pull"})
        results = self.vm.query("pull myrepo")
        assert len(results) >= 1

    def test_query_empty_store(self):
        results = self.vm.query("anything")
        assert results == []

    def test_top_k_limit(self):
        for i in range(10):
            self.vm.add(f"pull failed on repo{i}")
        results = self.vm.query("pull failed", top_k=3)
        assert len(results) <= 3


class TestKnowledgeGraph:
    def setup_method(self):
        self.kg = KnowledgeGraph()

    def test_add_node(self):
        self.kg.add_node("pull::repo_a", status="ok")
        assert "pull::repo_a" in self.kg._nodes

    def test_add_edge_creates_both_nodes(self):
        self.kg.add_edge("pull::repo_a", "failures", label="has")
        assert "failures" in self.kg._nodes

    def test_neighbors(self):
        self.kg.add_edge("lint::repo_a", "failures", label="has")
        assert "failures" in self.kg.neighbors("lint::repo_a")

    def test_persistence(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        kg1 = KnowledgeGraph(path)
        kg1.add_node("pull::repo_a", x=1)
        kg2 = KnowledgeGraph(path)
        assert "pull::repo_a" in kg2._nodes


class TestRAGEngine:
    def setup_method(self):
        self.mem = Memory()
        self.vm = VectorMemory()
        self.kg = KnowledgeGraph()
        self.rag = RAGEngine(self.mem, self.vm, self.kg)

    def test_get_context_no_history(self):
        ctx = self.rag.get_context("/repo/x", "pull")
        assert "warnings" in ctx
        assert ctx["warnings"] == []

    def test_get_context_with_failures(self):
        self.mem.record("g", "pull", "/repo/x", {"ok": False}, "agent")
        ctx = self.rag.get_context("/repo/x", "pull")
        assert len(ctx["warnings"]) > 0

    def test_learn_updates_memory(self):
        self.rag.learn("/repo/x", "pull", {"ok": True}, "agent", goal="update")
        assert self.mem.summary()["total_actions"] == 1

    def test_recall_repo_affinity(self):
        self.mem.record("g", "pull", "/repo/x", {"ok": True}, "agent")
        score = self.rag.recall_repo_affinity("/repo/x", "agent")
        assert score == 1.0
