#!/usr/bin/env python3
"""
cli/main.py — dream.os v7 entry point.

Usage:
  python -m dreamos.cli.main "update all repos"
  python -m dreamos.cli.main run "fix my repo"
  python -m dreamos.cli.main "fix lint" --dry-run
  python -m dreamos.cli.main --list-repos
  python -m dreamos.cli.main repos sync --owner YOU --target D:\\GitHub
  python -m dreamos.cli.main scan all --root D:\\GitHub
  python -m dreamos.cli.main bootstrap run --owner YOU --target D:\\GitHub
"""

import argparse
import sys
from pathlib import Path

# Make sure package root is on path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dreamos.config.settings import SETTINGS
from dreamos.config.task_context import require_task_id_or_exit
from dreamos.config.goals import GOAL_PLANS
from dreamos.scan.local_scanner import discover_git_repo_roots
from dreamos.tools import build_default_registry
from dreamos.core.agent import CognitiveAgent
from dreamos.core.memory import Memory, VectorMemory, KnowledgeGraph, RAGEngine
from dreamos.core.swarm import SwarmController
from dreamos.core.task_adapter import TaskAdapter
from dreamos.logging.logger import setup_logger
from src.core.message import BusMessage, load_message
from src.relay.device_relay import DeviceRelay
from src.transports.file_transport import FileTransport


def find_repos():
    """Immediate git children of github_dir (or github_dir itself if it is a repo)."""
    github_dir = Path(SETTINGS.github_dir).expanduser().resolve()
    if not github_dir.is_dir():
        return []
    repos = [str(p) for p in discover_git_repo_roots(github_dir)]
    if SETTINGS.safe_repos:
        repos = [r for r in repos if SETTINGS.repo_is_safe(r)]
    return sorted(repos)


def build_swarm(verbose: bool = False):
    log = setup_logger(log_file=SETTINGS.log_file, verbose=verbose)

    registry = build_default_registry()

    memory = Memory(persist_path=SETTINGS.graph_path.replace(".json", "_mem.json"))
    vectors = VectorMemory(SETTINGS.vector_db_path)
    graph = KnowledgeGraph(SETTINGS.graph_path)
    rag = RAGEngine(memory, vectors, graph)

    agents = [
        CognitiveAgent("GitMaster",  ["pull", "push", "commit", "status", "diff", "branch"], registry, rag),
        CognitiveAgent("LintLord",   ["lint", "fix", "format"],                               registry, rag),
        CognitiveAgent("TestRunner", ["test"],                                                 registry, rag),
        CognitiveAgent("MetaAgent",  ["status", "diff", "scan"],                              registry, rag),
    ]

    swarm = SwarmController(agents=agents, rag=rag, tool_registry=registry)
    return swarm, agents, registry


def print_help_goals():
    print("\nKnown goals:")
    for pattern, steps in GOAL_PLANS.items():
        print(f"  {pattern:<20} → {' → '.join(steps)}")
    print()


def execute_swarm_goal(goal: str, *, verbose: bool = False) -> None:
    """Run a single swarm goal via file-transport relay (shared by `main` and `dreamos run`)."""
    require_task_id_or_exit()
    repos = find_repos()
    if not repos:
        print(f"⚠️  No repos found in {SETTINGS.github_dir}")
        print("   Set DREAMOS_GITHUB_DIR or DREAMOS_SAFE_REPOS env vars.")
        sys.exit(1)

    swarm, agents, registry = build_swarm(verbose=verbose)

    print(f"\n  🔧 Tools  : {registry.names()}")
    print(f"  👥 Agents : {[a.name for a in agents]}")
    print(f"  📝 Log    : {SETTINGS.log_file}")

    bus_root = Path(SETTINGS.github_dir).expanduser() / ".dreamos_bus"
    worker_node = "dreamos-worker"
    cli_node = "dreamos-cli"
    transport = FileTransport(bus_root=bus_root, nodes=[worker_node, cli_node])
    relay = DeviceRelay(
        node_id=worker_node,
        transport=transport,
        task_adapter=TaskAdapter(swarm),
    )
    message = BusMessage(
        from_agent=cli_node,
        to_agent=worker_node,
        msg_type="task",
        body=goal,
        device_hint=worker_node,
        meta={"goal": goal, "repos": repos},
    )
    transport.send(message)
    relay.poll_once()
    complete_path = bus_root / "complete" / f"{worker_node}__{message.id}.json"
    final_message = load_message(complete_path)
    if final_message.result:
        print(f"\n  ✅ Message execution complete: {final_message.id}")
    if final_message.error:
        print(f"\n  ❌ Message execution failed: {final_message.error}")


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "repos":
        from dreamos.cli.repos_sync import main as repos_main

        repos_main(argv[1:])
        return

    if argv and argv[0] == "scan":
        from dreamos.cli.scan_cmd import main as scan_main

        scan_main(argv[1:])
        return

    if argv and argv[0] == "bootstrap":
        from dreamos.cli.bootstrap_cmd import main as bootstrap_main

        bootstrap_main(argv[1:])
        return

    if argv and argv[0] == "headers":
        from dreamos.cli.headers_cmd import main as headers_main

        headers_main(argv[1:])
        return

    if argv and argv[0] == "run":
        from dreamos.cli.command_router import resolve_phrase, run_route

        i = 1
        verbose = False
        while i < len(argv):
            a = argv[i]
            if a in ("-v", "--verbose"):
                verbose = True
                i += 1
                continue
            if a == "--dry-run":
                SETTINGS.dry_run = True
                i += 1
                continue
            if a == "--live":
                SETTINGS.dry_run = False
                i += 1
                continue
            if a.startswith("-"):
                print(f"Unknown flag: {a}", file=sys.stderr)
                sys.exit(2)
            break
        phrase = " ".join(argv[i:]).strip()
        if not phrase:
            print(
                "Usage: dreamos run [--verbose] [--dry-run] [--live] <phrase>",
                file=sys.stderr,
            )
            sys.exit(2)
        route = resolve_phrase(phrase)
        raise SystemExit(run_route(route, verbose=verbose))

    parser = argparse.ArgumentParser(
        prog="dreamos",
        description="dream.os v7 — Modular Cognitive Swarm",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "goal", nargs="?",
        help="Goal to execute (e.g. 'update all repos', 'fix lint')"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate without making real changes")
    parser.add_argument("--live",    action="store_true", help="Disable dry-run (real changes!)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--list-repos",  action="store_true", help="List discovered repos and exit")
    parser.add_argument("--list-goals",  action="store_true", help="List known goal patterns and exit")
    parser.add_argument("--list-tools",  action="store_true", help="List registered tools and exit")

    args = parser.parse_args()

    # Apply flags
    if args.dry_run:
        SETTINGS.dry_run = True
    if args.live:
        SETTINGS.dry_run = False

    if args.list_goals:
        print_help_goals()
        return

    if args.list_repos:
        repos = find_repos()
        print(f"\nFound {len(repos)} repos in {SETTINGS.github_dir}:")
        for r in repos:
            print(f"  {r}")
        print()
        return

    if args.list_tools:
        registry = build_default_registry()
        print(f"\nRegistered tools: {registry.names()}\n")
        return

    goal = args.goal
    if not goal:
        goal = input("Enter goal: ").strip()
    if not goal:
        parser.print_help()
        sys.exit(1)

    execute_swarm_goal(goal, verbose=args.verbose)


if __name__ == "__main__":
    main()
