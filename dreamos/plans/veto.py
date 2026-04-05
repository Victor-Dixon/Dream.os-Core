"""
plans/veto.py — Swarm veto rules.
Blocks downstream steps if critical upstream steps failed.
"""

from typing import Dict, List
from ..logging.logger import log


# Tools that gate downstream execution
GATES: Dict[str, List[str]] = {
    # If lint failed → block commit and push
    "lint": ["commit", "push"],
    # If tests failed → block commit and push
    "test": ["commit", "push"],
    # If pull failed → block everything downstream
    "pull": ["lint", "fix", "test", "commit", "push"],
}


class VetoEngine:
    """
    Tracks which tools failed per-repo and vetoes downstream steps.
    Call `record_failure` after each failed step,
    then `is_vetoed` before scheduling the next step.
    """

    def __init__(self):
        # repo → set of failed tools
        self._failures: Dict[str, set] = {}

    def record_failure(self, tool: str, repo: str):
        self._failures.setdefault(repo, set()).add(tool)

    def is_vetoed(self, tool: str, repo: str) -> bool:
        failed = self._failures.get(repo, set())
        for failed_tool, blocked_tools in GATES.items():
            if failed_tool in failed and tool in blocked_tools:
                log.warning(
                    f"🛑 Veto: '{tool}' blocked on {repo.split('/')[-1]} "
                    f"('{failed_tool}' failed)"
                )
                return True
        return False

    def reset(self, repo: str = None):
        if repo:
            self._failures.pop(repo, None)
        else:
            self._failures.clear()
