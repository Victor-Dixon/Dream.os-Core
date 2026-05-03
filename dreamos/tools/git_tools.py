"""
tools/git_tools.py — All git operations.
"""

import subprocess
from datetime import datetime, timezone
from typing import List

from .base import BaseTool, ToolResult
from ..config.settings import SETTINGS


def _git(args: List[str], cwd: str) -> ToolResult:
    """Run a git command, return a ToolResult."""
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=SETTINGS.tool_timeout,
        )
        output = (r.stdout + r.stderr).strip()
        return ToolResult(ok=r.returncode == 0, output=output)
    except subprocess.TimeoutExpired:
        return ToolResult.failure("git command timed out")
    except FileNotFoundError:
        return ToolResult.failure("git not found — is it installed?")
    except Exception as exc:
        return ToolResult.failure(str(exc))


class GitStatusTool(BaseTool):
    name = "status"
    description = "Show working-tree status"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        r = _git(["status", "--porcelain"], repo)
        if not r.ok:
            return r
        lines = [l for l in r.output.splitlines() if l.strip()]
        return ToolResult.success(
            output=r.output,
            has_changes=bool(lines),
            changed_files=len(lines),
        )


class GitPullTool(BaseTool):
    name = "pull"
    description = "Pull latest changes (rebase)"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _git(["pull", "--rebase"], repo)


class GitDiffTool(BaseTool):
    name = "diff"
    description = "Show diff summary"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _git(["diff", "--stat"], repo)


class GitAddTool(BaseTool):
    name = "add"
    description = "Stage all changes"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _git(["add", "."], repo)


class GitCommitTool(BaseTool):
    name = "commit"
    description = "Commit staged changes"
    dangerous = True

    def execute(self, repo: str, message: str = "", **kwargs) -> ToolResult:
        if not message:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            message = f"auto: dream.os v7 @ {ts}"
        _git(["add", "."], repo)
        return _git(["commit", "-m", message], repo)


class GitPushTool(BaseTool):
    name = "push"
    description = "Push commits to remote"
    dangerous = True

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _git(["push"], repo)


class GitBranchTool(BaseTool):
    name = "branch"
    description = "Show current branch"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _git(["rev-parse", "--abbrev-ref", "HEAD"], repo)


def register_all(registry):
    """Convenience: register every git tool at once."""
    for cls in [
        GitStatusTool, GitPullTool, GitDiffTool,
        GitAddTool, GitCommitTool, GitPushTool, GitBranchTool,
    ]:
        registry.register(cls())
    return registry
