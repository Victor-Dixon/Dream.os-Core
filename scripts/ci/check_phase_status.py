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
        choices=["COMPLETED", "IN PROGRESS", "FUTURE"],
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


def main() -> int:
    args = parse_args()
    status_text = args.status_file.read_text(encoding="utf-8")
    current = extract_phase_status(status_text, args.phase)

    if current is None:
        print(f"ERROR: Could not find Phase {args.phase} in {args.status_file}")
        return 2

    print(f"Phase {args.phase} status in SSOT: {current}")
    if current != args.expected:
        print(f"ERROR: Expected '{args.expected}' but found '{current}'")
        return 1

    print("Status check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
