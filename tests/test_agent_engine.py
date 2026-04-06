from __future__ import annotations

from pathlib import Path

from src.execution.agent_engine import AgentEngine


class CwdCapturingOrchestrator:
    observed_cwd: Path | None = None

    def __init__(self, workspace: str, model: str, verbose: bool):
        self.workspace = workspace
        self.model = model
        self.verbose = verbose
        CwdCapturingOrchestrator.observed_cwd = Path.cwd()

    def initialize(self):
        return self

    def answer(self, query: str) -> str:
        return f"ok:{query}"


def test_agent_engine_run_does_not_change_process_cwd(monkeypatch, tmp_path: Path) -> None:
    original_cwd = Path.cwd()
    monkeypatch.setattr(
        AgentEngine,
        "_load_orchestrator_class",
        lambda self, repo_path: CwdCapturingOrchestrator,
    )

    engine = AgentEngine()
    result = engine.run(goal="status", repo=str(tmp_path))

    assert CwdCapturingOrchestrator.observed_cwd == original_cwd
    assert Path.cwd() == original_cwd
    assert result["ok"] is True
    assert result["repo"] == str(tmp_path.resolve())
