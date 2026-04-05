"""
plans/decomposer.py — Translates a natural-language goal into an ordered tool pipeline.
"""

from typing import List
from ..config.goals import GOAL_PLANS, DEFAULT_PLAN
from ..logging.logger import log


class Decomposer:
    """
    Match a goal string against known patterns → return ordered list of tools.
    Extend GOAL_PLANS in config/goals.py without touching this file.
    """

    def decompose(self, goal: str) -> List[str]:
        g = goal.lower().strip()

        for pattern, steps in GOAL_PLANS.items():
            if pattern in g:
                log.info(f"🧩 Goal '{goal}' → plan: {' → '.join(steps)}")
                return steps

        log.warning(f"No plan matched '{goal}' — defaulting to: {DEFAULT_PLAN}")
        return list(DEFAULT_PLAN)
