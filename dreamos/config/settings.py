"""
config/settings.py — All configuration in one place.
Override anything with environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    # Paths
    github_dir: str = field(
        default_factory=lambda: os.path.expanduser(
            os.getenv("DREAMOS_GITHUB_DIR", "~/github")
        )
    )
    log_file: str = field(
        default_factory=lambda: os.path.expanduser(
            os.getenv("DREAMOS_LOG", "~/dreamos.log")
        )
    )
    vector_db_path: str = field(
        default_factory=lambda: os.path.expanduser(
            os.getenv("DREAMOS_VECTOR_DB", "~/dreamos_vectors")
        )
    )
    graph_path: str = field(
        default_factory=lambda: os.path.expanduser(
            os.getenv("DREAMOS_GRAPH", "~/dreamos_graph.json")
        )
    )

    # Execution
    dry_run: bool = field(
        default_factory=lambda: os.getenv("DREAMOS_DRY_RUN", "1") == "1"
    )
    max_workers: int = field(
        default_factory=lambda: int(os.getenv("DREAMOS_WORKERS", "4"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("DREAMOS_RETRIES", "2"))
    )
    tool_timeout: int = field(
        default_factory=lambda: int(os.getenv("DREAMOS_TIMEOUT", "30"))
    )

    # Safety
    safe_repos: List[str] = field(default_factory=list)
    dangerous_tools: List[str] = field(
        default_factory=lambda: ["push", "commit"]
    )

    def __post_init__(self):
        raw = os.getenv("DREAMOS_SAFE_REPOS", "")
        if raw:
            self.safe_repos = [s.strip() for s in raw.split(",") if s.strip()]

    def repo_is_safe(self, repo_path: str) -> bool:
        if not self.safe_repos:
            return True  # no allowlist = all repos allowed
        name = os.path.basename(repo_path).lower()
        return any(s.lower() in name for s in self.safe_repos)

    def tool_is_dangerous(self, tool_name: str) -> bool:
        return tool_name in self.dangerous_tools


# Singleton — import this everywhere
SETTINGS = Settings()
