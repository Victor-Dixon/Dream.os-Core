#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT = ROOT / "_ops" / "reports" / f"finalize_tree_cleanup_{STAMP}.json"

DELETE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

DELETE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

MOVE_OUT_OF_TREE = [
    ROOT / "_ops" / "quarantine",
]

ARCHIVE_DEEP_NOISE_DIRS = [
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "DOCUMENTATION",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "PRDs",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "agent_workspaces",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "fsm_data",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "runtime" / "collaborative_tasks",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "src" / "collaborative" / "task_manager" / "demo_output",
    ROOT / "archive" / "imports" / "Agent_Cellphone" / "project_repository" / "PRDs",
]

EXTERNAL_QUARANTINE = ROOT.parent / f"DreamOS_quarantine_{STAMP}"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def move_path(src: Path, dst_root: Path, moved: list[dict]) -> None:
    if not src.exists():
        return
    dst = dst_root / rel(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    moved.append({"from": rel(src), "to": str(dst)})


def main() -> int:
    deleted = []
    moved = []

    # Delete generated files first.
    for path in sorted(ROOT.rglob("*"), reverse=True):
        if ".git" in path.parts:
            continue
        if path.is_file() and path.suffix in DELETE_SUFFIXES:
            path.unlink()
            deleted.append(rel(path))

    # Delete generated cache dirs.
    for path in sorted(ROOT.rglob("*"), reverse=True):
        if ".git" in path.parts:
            continue
        if path.is_dir() and path.name in DELETE_DIR_NAMES:
            shutil.rmtree(path)
            deleted.append(rel(path))

    # Move quarantine out of repo tree so tree becomes readable.
    for src in MOVE_OUT_OF_TREE:
        move_path(src, EXTERNAL_QUARANTINE, moved)

    # Move deep imported runtime/demo/PRD noise out of repo tree.
    for src in ARCHIVE_DEEP_NOISE_DIRS:
        move_path(src, EXTERNAL_QUARANTINE, moved)

    # Remove empty dirs.
    empty_removed = []
    for path in sorted(ROOT.rglob("*"), reverse=True):
        if ".git" in path.parts:
            continue
        if path.is_dir():
            try:
                path.rmdir()
                empty_removed.append(rel(path))
            except OSError:
                pass

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(
            {
                "deleted_count": len(deleted),
                "moved_count": len(moved),
                "empty_removed_count": len(empty_removed),
                "external_quarantine": str(EXTERNAL_QUARANTINE),
                "deleted": deleted,
                "moved": moved,
                "empty_removed": empty_removed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"deleted: {len(deleted)}")
    print(f"moved: {len(moved)}")
    print(f"empty dirs removed: {len(empty_removed)}")
    print(f"external quarantine: {EXTERNAL_QUARANTINE}")
    print(f"report: {rel(REPORT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
