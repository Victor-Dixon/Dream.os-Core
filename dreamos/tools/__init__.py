"""DreamOS tools package.

Keep package import side effects minimal. Tool implementations should be loaded
by explicit module import or registry discovery, not by importing this package.
"""

__all__ = [
    "ToolRegistry",
    "ToolResult",
]


def __getattr__(name: str):
    if name in __all__:
        from .base import ToolRegistry, ToolResult

        values = {
            "ToolRegistry": ToolRegistry,
            "ToolResult": ToolResult,
        }
        return values[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
