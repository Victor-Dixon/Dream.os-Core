"""
config/goals.py — Goal → pipeline mappings.
Add new goals here without touching any other file.
"""

from typing import Dict, List

# Each value is an ordered list of tool names to run per-repo.
# Steps run sequentially; the veto engine can short-circuit on failure.
GOAL_PLANS: Dict[str, List[str]] = {
    # Substring match on lowered goal (e.g. "run projectscanner on all repos")
    "projectscanner": ["scan"],
    "fix lint":   ["pull", "lint", "fix", "test", "commit", "push"],
    "deploy":     ["pull", "lint", "test", "commit", "push"],
    "test":       ["pull", "lint", "test"],
    "check":      ["status", "lint"],
    "sync":       ["pull", "status", "diff"],
    "update all": ["pull", "status"],
    "update":     ["pull", "status"],
    "status":     ["status"],
    "diff":       ["diff"],
}

DEFAULT_PLAN: List[str] = ["status"]
