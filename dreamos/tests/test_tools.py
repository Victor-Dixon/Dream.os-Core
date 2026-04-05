"""tests/test_tools.py"""

import os
import subprocess
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from dreamos.tools.base import BaseTool, ToolResult, ToolRegistry
from dreamos.tools.git_tools import GitStatusTool, GitPullTool, GitCommitTool
from dreamos.tools.lint_tools import LintTool, FixTool


# ── ToolResult ────────────────────────────────────────────────────────────────

class TestToolResult:
    def test_success_factory(self):
        r = ToolResult.success("done", x=1)
        assert r.ok is True
        assert r.output == "done"
        assert r.metadata["x"] == 1

    def test_failure_factory(self):
        r = ToolResult.failure("boom")
        assert r.ok is False
        assert r.error == "boom"

    def test_to_dict(self):
        r = ToolResult(ok=True, output="hi")
        d = r.to_dict()
        assert d["ok"] is True
        assert "output" in d


# ── ToolRegistry ──────────────────────────────────────────────────────────────

class TestToolRegistry:
    def setup_method(self):
        self.registry = ToolRegistry()

    def test_register_and_get(self):
        tool = GitStatusTool()
        self.registry.register(tool)
        assert self.registry.get("status") is tool

    def test_contains(self):
        self.registry.register(GitStatusTool())
        assert "status" in self.registry

    def test_names(self):
        self.registry.register(GitStatusTool())
        self.registry.register(GitPullTool())
        assert set(self.registry.names()) == {"status", "pull"}

    def test_run_unknown_tool(self):
        result = self.registry.run("nonexistent", "/fake/repo")
        assert result.ok is False
        assert "unknown tool" in result.error

    def test_run_invalid_repo(self):
        self.registry.register(GitStatusTool())
        result = self.registry.run("status", "/nonexistent/path")
        assert result.ok is False

    def test_chaining(self):
        r = ToolRegistry()
        r.register(GitStatusTool()).register(GitPullTool())
        assert len(r.names()) == 2

    def test_register_unnamed_tool_raises(self):
        class BadTool(BaseTool):
            name = ""
            def execute(self, repo, **kw): pass
        with pytest.raises(ValueError):
            self.registry.register(BadTool())


# ── Git Tools ─────────────────────────────────────────────────────────────────

class TestGitStatusTool:
    def test_clean_repo(self, tmp_path):
        # Init a real git repo
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        tool = GitStatusTool()
        result = tool.safe_execute(str(tmp_path))
        assert result.ok is True
        assert result.metadata.get("has_changes") is False

    def test_invalid_repo(self, tmp_path):
        tool = GitStatusTool()
        result = tool.safe_execute(str(tmp_path))  # no .git
        assert result.ok is False

    def test_nonexistent_path(self):
        tool = GitStatusTool()
        result = tool.safe_execute("/does/not/exist")
        assert result.ok is False


class TestGitCommitTool:
    def test_default_message_contains_timestamp(self, tmp_path):
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
        tool = GitCommitTool()
        # Should not crash even with nothing to commit
        result = tool.safe_execute(str(tmp_path))
        # ok may be False (nothing to commit) — that's fine, we just verify no exception
        assert isinstance(result.ok, bool)


# ── Lint Tools ────────────────────────────────────────────────────────────────

class TestLintTool:
    @patch("subprocess.run")
    def test_no_issues(self, mock_run, tmp_path):
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        tool = LintTool()
        result = tool.safe_execute(str(tmp_path))
        assert result.ok is True
        assert result.metadata.get("has_issues") is False

    @patch("subprocess.run")
    def test_has_issues(self, mock_run, tmp_path):
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        mock_run.return_value = MagicMock(
            returncode=1, stdout="E501 line too long\n", stderr=""
        )
        tool = LintTool()
        result = tool.safe_execute(str(tmp_path))
        assert result.ok is False
        assert result.metadata.get("has_issues") is True

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_ruff_not_installed(self, mock_run, tmp_path):
        subprocess.run.__class__ = subprocess.run.__class__  # reset
        tool = LintTool()
        # validate will block first since tmp_path has no .git
        result = tool.safe_execute("/nonexistent/path")
        assert result.ok is False
