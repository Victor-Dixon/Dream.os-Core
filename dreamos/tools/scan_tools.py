"""Local repository scan tool (ProjectScanner-compatible artifacts)."""

from __future__ import annotations

import os
from pathlib import Path

from dreamos.scan.local_scanner import write_scan_artifacts

from .base import BaseTool, ToolResult


class LocalScanTool(BaseTool):
    name = "scan"
    description = "Write .dreamos/metadata.json and .dreamos/analysis.json (optional projectscanner hook)."
    dangerous = False

    def execute(self, repo: str, **kwargs) -> ToolResult:
        root = Path(repo).resolve()
        task_id = kwargs.get("task_id") or os.getenv("DREAMOS_TASK_ID", "").strip() or None
        try:
            out = write_scan_artifacts(root, task_id=task_id)
            return ToolResult.success(
                output=str(out / "analysis.json"),
                metadata={"artifacts_dir": str(out)},
            )
        except OSError as exc:
            return ToolResult.failure(str(exc))


def register_all(registry) -> None:
    registry.register(LocalScanTool())
