"""
core/swarm.py — SwarmController: coordinates agents across repos and steps.

Execution model:
  For each step in the plan:
    For each repo (in parallel):
      1. Veto check — skip if blocked
      2. Memory avoid check — skip if repeated failures
      3. Negotiate — pick best agent via bidding
      4. Execute — agent runs the tool
      5. Update veto + memory
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from ..config.settings import SETTINGS
from ..logging.logger import log
from ..plans.decomposer import Decomposer
from ..plans.veto import VetoEngine
from ..tools.base import ToolRegistry


class SwarmController:
    def __init__(
        self,
        agents: list,
        rag=None,
        tool_registry: Optional[ToolRegistry] = None,
        settings=None,
    ):
        self.agents = agents
        self.rag = rag
        self.registry = tool_registry
        self.settings = settings or SETTINGS
        self.decomposer = Decomposer()
        self.veto = VetoEngine()
        self._results: List[Dict] = []
        self._lock = threading.Lock()

    # ── Agent Selection ───────────────────────────────────────────────────────

    def _negotiate(self, tool: str, repo: str) -> Optional[Any]:
        capable = [a for a in self.agents if a.can_handle(tool)]
        if not capable:
            log.warning(f"No agent can handle tool: {tool}")
            return None
        return max(capable, key=lambda a: a.bid(tool, repo, self.rag))

    # ── Per-repo step execution ───────────────────────────────────────────────

    def _run_step(self, tool: str, repo: str, goal: str) -> Optional[Dict]:
        repo_label = os.path.basename(repo)

        # Safety check
        if not self.settings.repo_is_safe(repo):
            log.warning(f"⛔ Blocked — {repo_label} not in allowlist")
            return None

        # Veto check (per-repo failure gates)
        if self.veto.is_vetoed(tool, repo):
            return None

        # Memory: avoid known-broken combos
        if self.rag and self.rag.memory.should_avoid(tool, repo, self.settings.max_retries):
            log.warning(f"⚠️  Skipping {repo_label}/{tool} (repeated failures)")
            return None

        # Dangerous tool guard (when dry_run is off)
        if not self.settings.dry_run and self.settings.tool_is_dangerous(tool):
            log.warning(f"🔒 Blocked dangerous tool '{tool}' — enable explicitly")
            return None

        agent = self._negotiate(tool, repo)
        if not agent:
            return None

        result = agent.execute(
            tool=tool,
            repo=repo,
            dry_run=self.settings.dry_run,
            goal=goal,
        )

        # Update veto state on failure
        if not result.get("ok"):
            self.veto.record_failure(tool, repo)

        return result

    # ── Main Run ──────────────────────────────────────────────────────────────

    def run(self, goal: str, repos: List[str]) -> List[Dict]:
        steps = self.decomposer.decompose(goal)
        self._results.clear()
        self.veto.reset()

        print(f"\n{'═'*52}")
        print(f"  🐝 dream.os v7  |  goal: {goal}")
        print(f"  📦 repos: {len(repos)}  |  steps: {' → '.join(steps)}")
        print(f"  {'⚠️  DRY RUN' if self.settings.dry_run else '🔴 LIVE'}")
        print(f"{'═'*52}\n")

        step_summaries: List[Dict] = []

        for step in steps:
            print(f"── {step} {'─' * (46 - len(step))}")
            step_results = []

            with ThreadPoolExecutor(max_workers=self.settings.max_workers) as pool:
                futures: Dict = {
                    pool.submit(self._run_step, step, repo, goal): repo
                    for repo in repos
                }
                for future in as_completed(futures):
                    repo = futures[future]
                    try:
                        result = future.result()
                        if result is not None:
                            step_results.append(result)
                            with self._lock:
                                self._results.append(result)
                    except Exception as exc:
                        log.error(f"Unhandled agent error on {repo}: {exc}")

            ok = sum(1 for r in step_results if r.get("ok"))
            total = len(step_results)
            icon = "✅" if ok == total else "⚠️ " if ok > 0 else "❌"
            print(f"  {icon} {ok}/{total} succeeded\n")
            step_summaries.append({"step": step, "ok": ok, "total": total})

        self._print_report(step_summaries)
        return self._results

    # ── Report ────────────────────────────────────────────────────────────────

    def _print_report(self, step_summaries: List[Dict]):
        print(f"\n{'═'*52}")
        print("  📊 REPORT")
        print(f"{'═'*52}")

        for s in step_summaries:
            ok, total, step = s["ok"], s["total"], s["step"]
            if total == 0:
                marker = "─"
            elif ok == total:
                marker = "✅"
            elif ok > 0:
                marker = "⚠️ "
            else:
                marker = "❌"
            print(f"  {step:<14} {marker}  {ok}/{total}")

        print("\n  🤖 Agents:")
        for agent in self.agents:
            s = agent.stats
            rag_note = f"  ({s.rag_queries} RAG)" if hasattr(s, "rag_queries") and s.rag_queries else ""
            print(
                f"  {agent.name:<14} [{s.bar()}] "
                f"{s.success_rate:.0%}  ({s.successes}/{s.tasks}){rag_note}"
            )

        if self.rag:
            mem = self.rag.memory.summary()
            print(f"\n  💾 Memory: {mem['total_actions']} actions, {mem['success_rate']:.0%} success rate")

        print(f"{'═'*52}\n")
