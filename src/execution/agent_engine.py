from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AgentEngineError(RuntimeError):
    """Raised when the DreamOS agent engine cannot execute a request."""


@dataclass
class AgentEngine:
    """Wrapper around dreamos_agent orchestrator as a black-box execution unit."""

    model: str = "llama3"
    verbose: bool = False

    def _ensure_import_path(self) -> None:
        zip_path = Path.cwd() / "dreamos_agent.zip"
        if zip_path.exists() and str(zip_path) not in sys.path:
            sys.path.insert(0, str(zip_path))

    def _load_orchestrator_class(self):
        self._ensure_import_path()
        module = importlib.import_module("dreamos_agent.agent.orchestrator")
        return module.Orchestrator

    def run(self, goal: str, repo: str) -> dict[str, Any]:
        if not goal or not goal.strip():
            raise AgentEngineError("goal must be a non-empty string")
        if not repo or not str(repo).strip():
            raise AgentEngineError("repo must be a non-empty path")

        repo_path = Path(repo).resolve()
        if not repo_path.exists():
            raise AgentEngineError(f"repo path does not exist: {repo_path}")

        Orchestrator = self._load_orchestrator_class()
        cwd = Path.cwd()
        os.chdir(repo_path)
        try:
            orchestrator = Orchestrator(workspace=str(repo_path), model=self.model, verbose=self.verbose)
            orchestrator.initialize()
            response = orchestrator.answer(goal)
        except Exception as exc:  # pragma: no cover - guarded by callers/tests
            raise AgentEngineError(str(exc)) from exc
        finally:
            os.chdir(cwd)

        return {
            "ok": True,
            "goal": goal,
            "repo": str(repo_path),
            "engine": "dreamos_agent.orchestrator",
            "response": response,
        }
