from .base import BaseTool, ToolResult, ToolRegistry
from . import git_tools, lint_tools, scan_tools, test_tools


def build_default_registry() -> ToolRegistry:
    """Create and return a registry pre-loaded with all built-in tools."""
    registry = ToolRegistry()
    git_tools.register_all(registry)
    lint_tools.register_all(registry)
    test_tools.register_all(registry)
    scan_tools.register_all(registry)
    return registry


__all__ = ["BaseTool", "ToolResult", "ToolRegistry", "build_default_registry"]
