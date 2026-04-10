from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = ("status", "result")


def run_agent(task: str, attempt: int, fail_attempts: int) -> dict[str, object]:
    """Deterministic demo agent used to enforce an executable closed loop."""
    if attempt <= fail_attempts:
        return {"status": "error", "error": f"forced failure on attempt {attempt}"}
    return {
        "status": "success",
        "result": {
            "task": task,
            "attempt": attempt,
            "summary": f"completed task: {task}",
        },
    }


def validate_output(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "output file missing"

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc.msg}"

    missing = [key for key in REQUIRED_KEYS if key not in payload]
    if missing:
        return False, f"missing required keys: {missing}"
    if payload["status"] != "success":
        return False, "status is not success"
    if not isinstance(payload["result"], dict):
        return False, "result must be an object"

    return True, "valid"


def execute_closed_loop(task: str, max_retries: int, fail_attempts: int, output_path: Path) -> int:
    for attempt in range(1, max_retries + 1):
        output = run_agent(task=task, attempt=attempt, fail_attempts=fail_attempts)
        output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

        is_valid, reason = validate_output(output_path)
        if is_valid:
            print(f"PASS attempt={attempt} output={output_path}")
            return 0
        print(f"FAIL attempt={attempt} reason={reason}")

    print(f"GIVE_UP max_retries={max_retries} output={output_path}")
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal closed-loop runtime pipeline")
    parser.add_argument("--task", default="demo task", help="task description")
    parser.add_argument("--max-retries", type=int, default=3, help="max retry attempts")
    parser.add_argument(
        "--fail-attempts",
        type=int,
        default=0,
        help="simulate deterministic agent failures for the first N attempts",
    )
    parser.add_argument(
        "--output",
        default="runtime_demo/output.json",
        help="path to JSON output contract",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return execute_closed_loop(
        task=args.task,
        max_retries=args.max_retries,
        fail_attempts=args.fail_attempts,
        output_path=output_path,
    )


if __name__ == "__main__":
    raise SystemExit(main())
