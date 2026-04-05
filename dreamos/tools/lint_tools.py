"""
tools/lint_tools.py — Linting and auto-fix via ruff.
Falls back gracefully if ruff isn't installed.
"""

import subprocess
from .base import BaseTool, ToolResult
from ..config.settings import SETTINGS


def _ruff(args, cwd) -> ToolResult:
    try:
        r = subprocess.run(
            ["ruff"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=SETTINGS.tool_timeout,
        )
        output = (r.stdout + r.stderr).strip()
        return ToolResult(ok=r.returncode == 0, output=output)
    except FileNotFoundError:
        return ToolResult.failure("ruff not found — run: pip install ruff")
    except subprocess.TimeoutExpired:
        return ToolResult.failure("ruff timed out")
    except Exception as exc:
        return ToolResult.failure(str(exc))


class LintTool(BaseTool):
    name = "lint"
    description = "Check for lint issues with ruff"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        r = _ruff(["check", "."], repo)
        issue_count = len(r.output.splitlines()) if not r.ok else 0
        return ToolResult(
            ok=r.ok,
            output=r.output,
            error=r.error,
            metadata={"has_issues": not r.ok, "issue_count": issue_count},
        )


class FixTool(BaseTool):
    name = "fix"
    description = "Auto-fix lint issues with ruff"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        r = _ruff(["check", "--fix", "."], repo)
        return ToolResult(
            ok=r.ok,
            output=r.output,
            error=r.error,
            metadata={"fixed": r.ok},
        )


class FormatTool(BaseTool):
    name = "format"
    description = "Auto-format code with ruff format"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        return _ruff(["format", "."], repo)


def register_all(registry):
    for cls in [LintTool, FixTool, FormatTool]:
        registry.register(cls())
    return registry
