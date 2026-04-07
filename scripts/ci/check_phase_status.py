"""Check project phase status from the SSOT document."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument(
        "--expected",
        type=str,
        required=True,
        help="Expected status (COMPLETED, IN_PROGRESS/IN PROGRESS, FUTURE).",
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path("00_foundation/PROJECT_STATUS.md"),
    )
    return parser.parse_args()


def extract_phase_status(text: str, phase: int) -> str | None:
    pattern = rf"^## .*Phase\s+{phase}:.*-\s+(COMPLETED|IN PROGRESS|FUTURE)\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1)


def normalize_phase_status(value: str) -> str:
    normalized = value.strip().upper().replace(" ", "_")
    aliases = {
        "IN_PROGRESS": "IN PROGRESS",
        "COMPLETED": "COMPLETED",
        "FUTURE": "FUTURE",
    }
    if normalized not in aliases:
        raise ValueError(f"Unsupported phase status '{value}'")
    return aliases[normalized]


def main() -> int:
    args = parse_args()
    try:
        expected = normalize_phase_status(args.expected)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    status_text = args.status_file.read_text(encoding="utf-8")
    current = extract_phase_status(status_text, args.phase)

    if current is None:
        print(f"ERROR: Could not find Phase {args.phase} in {args.status_file}")
        return 2

    print(f"Phase {args.phase} status in SSOT: {current}")
    if current != expected:
        print(f"ERROR: Expected '{expected}' but found '{current}'")
        return 1

    print("Status check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
