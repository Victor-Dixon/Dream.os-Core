#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC, UTC

ROOT = Path.cwd()

LANES = {
    "PROMOTE_CORE_CANDIDATE": [
        "CORE/SECURE_COMMUNICATION_HUB.py",
        "CORE/COLLABORATIVE_EXECUTION_SYSTEM.py",
        "CORE/inter_agent_framework.py",
        "CORE/enhanced_agent_coordination_framework.py",
        "CORE/fixed_stall_detection_system.py",
        "CORE/unified_stall_detection_system.py",
        "CORE/collaborative_knowledge_management_system.py",
        "CORE/enhanced_collaborative_knowledge_system.py",
        "advanced_workflows/workflow_engine.py",
        "advanced_workflows/multi_agent_dev.py",
        "advanced_workflows/autonomous_pm.py",
    ],
    "REFERENCE_DOCS": [
        "DOCUMENTATION",
        "PRDs",
        "README.md",
        "ROADMAP.md",
        "MASTER_COORDINATION_PLAN.md",
        "ORGANIZATION_SUMMARY.md",
        "REPOSITORY_CLEANUP_STRATEGY.md",
        "VICTOR_CAMPAIGN_EXECUTION_PLAN.md",
    ],
    "MIGRATE_AS_ARCHIVE_EVIDENCE": [
        "CONTRACTS",
        "FSM_UPDATES",
        "agent_workspaces",
        "DEMOS",
    ],
    "REJECT_OR_QUARANTINE": [
        "CORE/debug_import.py",
        "CORE/enter_press_calibration.py",
        "CORE/improved_calibration.py",
        "CORE/calibrate_5_agent_coordinates.py",
        "CORE/restore_coordinate_backup.py",
        "LAUNCHERS",
    ],
}

def classify(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()

    for lane, patterns in LANES.items():
        for pattern in patterns:
            if rel == pattern or rel.startswith(pattern.rstrip("/") + "/"):
                return lane

    if path.suffix.lower() in {".md", ".txt"}:
        return "REFERENCE_DOCS"

    if path.suffix.lower() == ".json":
        return "MIGRATE_AS_ARCHIVE_EVIDENCE"

    if path.suffix.lower() == ".py":
        return "INSPECT_BEFORE_PROMOTE"

    return "UNCLASSIFIED"

def main() -> None:
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]

    rows = []
    counts = {}

    for p in sorted(files):
        lane = classify(p)
        rel = p.relative_to(ROOT).as_posix()
        size = p.stat().st_size
        rows.append({
            "path": rel,
            "lane": lane,
            "size_bytes": size,
            "suffix": p.suffix.lower(),
        })
        counts[lane] = counts.get(lane, 0) + 1

    report = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "root": str(ROOT),
        "file_count": len(rows),
        "lane_counts": counts,
        "lanes": LANES,
        "files": rows,
    }

    out_json = ROOT / "_ops/reports/agent_cellphone_flatten_audit.json"
    out_md = ROOT / "_ops/reports/agent_cellphone_flatten_audit.md"

    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Agent_Cellphone Flatten Audit",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Root: `{ROOT}`",
        f"- Files scanned: `{len(rows)}`",
        "",
        "## Lane Counts",
        "",
        "| Lane | Count |",
        "|---|---:|",
    ]

    for lane, count in sorted(counts.items()):
        lines.append(f"| `{lane}` | {count} |")

    lines.extend([
        "",
        "## Migration Interpretation",
        "",
        "| Lane | Action |",
        "|---|---|",
        "| `PROMOTE_CORE_CANDIDATE` | Inspect and port useful logic into Dream.os-Core modules/tests. Do not copy blindly. |",
        "| `INSPECT_BEFORE_PROMOTE` | Review for reusable primitives. Most likely one-off scripts. |",
        "| `REFERENCE_DOCS` | Move useful doctrine into Dream.os-Core `_ops/reports/imports/agent_cellphone/` or curated docs. |",
        "| `MIGRATE_AS_ARCHIVE_EVIDENCE` | Preserve as historical evidence only. Do not wire into runtime. |",
        "| `REJECT_OR_QUARANTINE` | Keep out of Dream.os-Core unless a specific modern need exists. |",
        "| `UNCLASSIFIED` | Manual review. |",
        "",
        "## High-Value Candidates",
        "",
    ])

    for row in rows:
        if row["lane"] == "PROMOTE_CORE_CANDIDATE":
            lines.append(f"- `{row['path']}`")

    lines.extend([
        "",
        "## Full Inventory",
        "",
        "| Lane | Path | Size |",
        "|---|---|---:|",
    ])

    for row in rows:
        lines.append(f"| `{row['lane']}` | `{row['path']}` | {row['size_bytes']} |")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"WROTE: {out_json}")
    print(f"WROTE: {out_md}")
    print(json.dumps(counts, indent=2))

if __name__ == "__main__":
    main()
