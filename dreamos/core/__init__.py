"""DreamOS core package.

Keep this package initializer lightweight.

Do not eagerly import agent/tool implementations here. Several transport and
relay tests import narrow modules such as ``dreamos.core.task_adapter``; eager
imports from this file can accidentally pull optional tool dependencies during
test collection.
"""

__all__ = [
    "BaseAgent",
    "CognitiveAgent",
    "AgentStats",
]


def __getattr__(name: str):
    if name in __all__:
        from .agent import AgentStats, BaseAgent, CognitiveAgent

        values = {
            "BaseAgent": BaseAgent,
            "CognitiveAgent": CognitiveAgent,
            "AgentStats": AgentStats,
        }
        return values[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
