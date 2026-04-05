"""
tools/test_tools.py — Test runners.
"""

import subprocess
from .base import BaseTool, ToolResult
from ..config.settings import SETTINGS


class PytestTool(BaseTool):
    name = "test"
    description = "Run tests with pytest"

    def execute(self, repo: str, **kwargs) -> ToolResult:
        try:
            r = subprocess.run(
                ["pytest", "--tb=short", "-q", "--no-header"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=SETTINGS.tool_timeout * 2,  # tests can be slow
            )
            output = (r.stdout + r.stderr).strip()
            passed = r.returncode == 0

            # Parse quick summary from pytest output
            summary_line = ""
            for line in reversed(output.splitlines()):
                if "passed" in line or "failed" in line or "error" in line:
                    summary_line = line.strip()
                    break

            return ToolResult(
                ok=passed,
                output=output,
                metadata={"summary": summary_line, "tests_passed": passed},
            )
        except FileNotFoundError:
            return ToolResult.failure("pytest not found — run: pip install pytest")
        except subprocess.TimeoutExpired:
            return ToolResult.failure("pytest timed out")
        except Exception as exc:
            return ToolResult.failure(str(exc))


def register_all(registry):
    registry.register(PytestTool())
    return registry
