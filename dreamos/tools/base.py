"""
tools/base.py — Interface contracts for all tools + central registry.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ── Result ────────────────────────────────────────────────────────────────────

@dataclass
class ToolResult:
    ok: bool
    output: str = ""
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "ok": self.ok,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def failure(cls, error: str) -> "ToolResult":
        return cls(ok=False, error=error)

    @classmethod
    def success(cls, output: str = "", **meta) -> "ToolResult":
        return cls(ok=True, output=output, metadata=meta)


# ── Base Tool ─────────────────────────────────────────────────────────────────

class BaseTool(ABC):
    """
    All tools implement this interface.
    Register once, use anywhere.
    """

    name: str = ""
    description: str = ""
    dangerous: bool = False  # Set True for destructive ops (push, commit)

    @abstractmethod
    def execute(self, repo: str, **kwargs) -> ToolResult:
        """Run the tool against a repo path."""

    def validate(self, repo: str) -> Optional[str]:
        """
        Return an error string if repo is invalid, else None.
        Override to add tool-specific validation.
        """
        if not os.path.isdir(repo):
            return f"path does not exist: {repo}"
        if not os.path.isdir(os.path.join(repo, ".git")):
            return f"not a git repo: {repo}"
        return None

    def safe_execute(self, repo: str, **kwargs) -> ToolResult:
        """Validate then execute."""
        err = self.validate(repo)
        if err:
            return ToolResult.failure(err)
        try:
            return self.execute(repo, **kwargs)
        except Exception as exc:
            return ToolResult.failure(f"unhandled exception: {exc}")


# ── Registry ──────────────────────────────────────────────────────────────────

class ToolRegistry:
    """
    Central registry. Register a tool once; look it up by name anywhere.

    Usage:
        registry = ToolRegistry()
        registry.register(GitPullTool())
        result = registry.run("pull", "/path/to/repo")
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> "ToolRegistry":
        if not tool.name:
            raise ValueError(f"{type(tool).__name__} must define a `name`")
        self._tools[tool.name] = tool
        return self  # allow chaining

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def names(self):
        return list(self._tools.keys())

    def run(self, name: str, repo: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult.failure(f"unknown tool: {name}")
        return tool.safe_execute(repo, **kwargs)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __repr__(self) -> str:
        return f"ToolRegistry({self.names()})"
