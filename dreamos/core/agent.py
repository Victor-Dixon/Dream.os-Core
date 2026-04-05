"""
core/agent.py — BaseAgent and CognitiveAgent.

BaseAgent   — pure bidding + execution logic, no memory dependency.
CognitiveAgent — wraps BaseAgent with RAG context and learning.
"""

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..tools.base import ToolRegistry, ToolResult
from ..logging.logger import log


# ── Stats ─────────────────────────────────────────────────────────────────────

@dataclass
class AgentStats:
    tasks: int = 0
    successes: int = 0
    failures: int = 0
    rag_queries: int = 0
    skipped: int = 0

    @property
    def success_rate(self) -> float:
        return self.successes / max(self.tasks, 1)

    def bar(self, width: int = 10) -> str:
        filled = int(self.success_rate * width)
        return "█" * filled + "░" * (width - filled)


# ── Base Agent ────────────────────────────────────────────────────────────────

class BaseAgent:
    """
    Stateless-ish agent: knows its tools, can bid on tasks, can execute.
    No memory dependency — pure logic.
    """

    def __init__(self, name: str, expertise: List[str], registry: ToolRegistry):
        self.name = name
        self.expertise = set(expertise)
        self.registry = registry
        self.stats = AgentStats()
        self._lock = threading.Lock()

    # ── Bidding ───────────────────────────────────────────────────────────────

    def can_handle(self, tool_name: str) -> bool:
        return tool_name in self.expertise

    def bid(self, tool: str, repo: str, memory=None) -> float:
        """
        Higher bid = agent wants this task more.
        Formula: capability × affinity × inverse-load
        """
        if not self.can_handle(tool):
            return 0.0

        affinity = (
            memory.recall_repo_affinity(repo, self.name)
            if memory else 0.5
        )
        with self._lock:
            load_factor = 1.0 / (self.stats.tasks + 1)

        return round(affinity * load_factor, 4)

    # ── Execution ─────────────────────────────────────────────────────────────

    def execute(
        self,
        tool: str,
        repo: str,
        dry_run: bool = False,
        goal: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        with self._lock:
            self.stats.tasks += 1

        repo_label = repo.split("/")[-1]
        log.info(f"🤖 {self.name}: {tool} → {repo_label}")

        if dry_run:
            result = ToolResult(ok=True, output="[dry run]", metadata={"dry": True})
        else:
            result = self.registry.run(tool, repo, **kwargs)

        with self._lock:
            if result.ok:
                self.stats.successes += 1
            else:
                self.stats.failures += 1

        icon = "✅" if result.ok else "❌"
        log.info(f"{icon} {self.name}/{tool} → {repo_label}")
        if result.error:
            log.warning(f"   error: {result.error}")

        return {
            "agent": self.name,
            "tool": tool,
            "repo": repo,
            **result.to_dict(),
        }

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name} expertise={sorted(self.expertise)}>"


# ── Cognitive Agent ───────────────────────────────────────────────────────────

class CognitiveAgent(BaseAgent):
    """
    Agent with RAG memory: retrieves context before executing,
    and learns from every result.
    """

    def __init__(
        self,
        name: str,
        expertise: List[str],
        registry: ToolRegistry,
        rag=None,  # RAGEngine | None
    ):
        super().__init__(name, expertise, registry)
        self.rag = rag

    def bid(self, tool: str, repo: str, memory=None) -> float:
        # Use injected RAG engine as memory if none provided
        return super().bid(tool, repo, memory or self.rag)

    def execute(
        self,
        tool: str,
        repo: str,
        dry_run: bool = False,
        goal: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        # ── Pre-execution: retrieve context ───────────────────────────────────
        if self.rag:
            with self._lock:
                self.stats.rag_queries += 1
            ctx = self.rag.get_context(repo, tool)
            if ctx.get("warnings"):
                log.warning(f"  🧠 {self.name} recalls: {ctx['warnings'][0]}")

        # ── Execute ───────────────────────────────────────────────────────────
        result = super().execute(tool, repo, dry_run=dry_run, goal=goal, **kwargs)

        # ── Post-execution: learn ─────────────────────────────────────────────
        if self.rag and not dry_run:
            self.rag.learn(repo, tool, result, worker=self.name, goal=goal)

        return result
