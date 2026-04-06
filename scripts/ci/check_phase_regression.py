"""Protect completed phases from regression using SSOT + CI job outcomes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path("00_foundation/PROJECT_STATUS.md"),
        help="Path to the SSOT project status document.",
    )
    parser.add_argument(
        "--phase-result",
        action="append",
        default=[],
        metavar="PHASE=RESULT",
        help="Phase CI result mapping, e.g. --phase-result 1=success",
    )
    return parser.parse_args()


def parse_completed_phases(status_text: str) -> set[int]:
    completed: set[int] = set()
    pattern = re.compile(r"^## .*Phase\s+(\d+):.*-\s+(COMPLETED|IN PROGRESS|FUTURE)\s*$", re.MULTILINE)
    for match in pattern.finditer(status_text):
        phase_num = int(match.group(1))
        phase_status = match.group(2)
        if phase_status == "COMPLETED":
            completed.add(phase_num)
    return completed


def parse_phase_results(entries: list[str]) -> dict[int, str]:
    results: dict[int, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise ValueError(f"Invalid phase mapping '{entry}'. Expected PHASE=RESULT format.")
        phase_raw, result = entry.split("=", maxsplit=1)
        phase = int(phase_raw.strip())
        results[phase] = result.strip().lower()
    return results


def verify_completed_phases(completed_phases: set[int], phase_results: dict[int, str]) -> list[str]:
    errors: list[str] = []
    for phase in sorted(completed_phases):
        result = phase_results.get(phase)
        if result is None:
            errors.append(f"Phase {phase} is COMPLETED in SSOT but missing CI result.")
            continue
        if result != "success":
            errors.append(
                f"Phase {phase} is COMPLETED in SSOT but CI result was '{result}', expected 'success'."
            )
    return errors


def main() -> int:
    args = parse_args()
    status_text = args.status_file.read_text(encoding="utf-8")
    completed = parse_completed_phases(status_text)
    phase_results = parse_phase_results(args.phase_result)
    errors = verify_completed_phases(completed, phase_results)

    if errors:
        print("Completed phase regression check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Completed phase regression check passed")
    print(f"Completed phases in SSOT: {sorted(completed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
