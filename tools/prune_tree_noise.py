#!/usr/bin/env python3
"""
DreamOS tree noise pruner.

Default mode: dry-run.
Apply mode:   python tools/prune_tree_noise.py --apply

Policy:
- Delete generated Python caches.
- Quarantine noisy legacy/import docs and JSONs, do not hard-delete.
- Preserve root SSOT docs and active config/schema JSONs.
- Emit a report before/after.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()

KEEP_MD_EXACT = {
    "AGENTS.md",
    "README.md",
    "README_CURATED.md",
    "00_foundation/README.md",
    "00_foundation/PROJECT_STATUS.md",
    "00_foundation/IMPLEMENTATION_ROADMAP.md",
    "00_foundation/PRODUCT_REQUIREMENTS_DOCUMENT.md",
    "00_foundation/TECHNICAL_SPECIFICATIONS.md",
    "01_core/README.md",
    "01_core/INTER_AGENT_COMMUNICATION_GUIDE.md",
    "03_execution/PROJECT_ROADMAP.md",
}

KEEP_JSON_PATTERNS = (
    "contracts/",
    "schemas/",
    "config/",
    "problems/",
    "runs/",
    "memory/",
    "99_manifest/",
)

QUARANTINE_DIR = ROOT / "_ops" / "quarantine" / f"tree_noise_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
REPORT = ROOT / "_ops" / "reports" / f"tree_noise_prune_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_under(path: Path, prefix: str) -> bool:
    return rel(path).startswith(prefix.rstrip("/") + "/")


def should_delete(path: Path) -> bool:
    r = rel(path)
    return (
        "__pycache__/" in r
        or r.endswith(".pyc")
        or r.endswith(".pyo")
        or r.endswith(".pytest_cache")
    )


def should_quarantine_md(path: Path) -> bool:
    r = rel(path)

    if r in KEEP_MD_EXACT:
        return False

    if r.startswith("_ops/reports/"):
        return False

    noisy_roots = (
        "archive/imports/",
        "04_onboarding/",
        "02_onboarding_ops/",
        "99_reference/",
    )

    noisy_names = (
        "SUMMARY",
        "COMPLETION",
        "AUDIT",
        "CLEANUP",
        "RELEASE",
        "DEMO",
        "GUIDE",
        "ORPHAN",
        "COLLABORATIVE",
        "ONBOARDING",
    )

    return r.startswith(noisy_roots) or any(token in path.name.upper() for token in noisy_names)


def should_quarantine_json(path: Path) -> bool:
    r = rel(path)

    if any(r.startswith(prefix) for prefix in KEEP_JSON_PATTERNS):
        return False

    if r.startswith("_ops/reports/"):
        return False

    noisy_tokens = (
        "processed",
        "results",
        "audit",
        "summary",
        "coords",
        "coordinates",
        "contract_update",
        "fsm_update",
        "evidence",
    )

    if r.startswith("archive/imports/"):
        return True

    return any(token in path.name.lower() for token in noisy_tokens)


def move_to_quarantine(path: Path, apply: bool) -> str:
    target = QUARANTINE_DIR / rel(path)
    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
    return rel(target)


def delete_path(path: Path, apply: bool) -> None:
    if not apply:
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually mutate files.")
    args = parser.parse_args()

    delete = []
    quarantine = []
    kept_md = []
    kept_json = []

    for path in sorted(ROOT.rglob("*")):
        if ".git/" in rel(path):
            continue
        if path == QUARANTINE_DIR or str(path).startswith(str(QUARANTINE_DIR)):
            continue

        if should_delete(path):
            delete.append(path)
            continue

        if path.is_file() and path.suffix.lower() == ".md":
            if should_quarantine_md(path):
                quarantine.append(path)
            else:
                kept_md.append(path)
            continue

        if path.is_file() and path.suffix.lower() == ".json":
            if should_quarantine_json(path):
                quarantine.append(path)
            else:
                kept_json.append(path)
            continue

    actions = {
        "mode": "apply" if args.apply else "dry-run",
        "delete_count": len(delete),
        "quarantine_count": len(quarantine),
        "kept_md_count": len(kept_md),
        "kept_json_count": len(kept_json),
        "delete": [rel(p) for p in delete],
        "quarantine": [{"from": rel(p), "to": move_to_quarantine(p, args.apply)} for p in quarantine],
        "kept_md": [rel(p) for p in kept_md],
        "kept_json": [rel(p) for p in kept_json],
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(actions, indent=2), encoding="utf-8")

    for path in delete:
        delete_path(path, args.apply)

    print(f"MODE: {actions['mode']}")
    print(f"DELETE: {actions['delete_count']}")
    print(f"QUARANTINE: {actions['quarantine_count']}")
    print(f"REPORT: {rel(REPORT)}")

    if not args.apply:
        print("")
        print("Dry-run only. Review the report, then run:")
        print("python tools/prune_tree_noise.py --apply")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
