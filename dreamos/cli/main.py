#!/usr/bin/env python3
"""
cli/main.py — dream.os v7 entry point.

Usage:
  python -m dreamos.cli.main "update all repos"
  python -m dreamos.cli.main "fix lint" --dry-run
  python -m dreamos.cli.main --list-repos
"""

import argparse
import sys
from pathlib import Path

# Make sure package root is on path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dreamos.config.settings import SETTINGS
from dreamos.config.goals import GOAL_PLANS
from dreamos.tools import build_default_registry
from dreamos.core.agent import CognitiveAgent
from dreamos.core.memory import Memory, VectorMemory, KnowledgeGraph, RAGEngine
from dreamos.core.swarm import SwarmController
from dreamos.logging.logger import setup_logger


def find_repos():
    github_dir = Path(SETTINGS.github_dir)
    if not github_dir.exists():
        return []
    repos = [str(p.parent) for p in github_dir.rglob(".git")]
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
        CognitiveAgent("MetaAgent",  ["status", "diff"],                                       registry, rag),
    ]

    swarm = SwarmController(agents=agents, rag=rag, tool_registry=registry)
    return swarm, agents, registry


def print_help_goals():
    print("\nKnown goals:")
    for pattern, steps in GOAL_PLANS.items():
        print(f"  {pattern:<20} → {' → '.join(steps)}")
    print()


def main():
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

    repos = find_repos()
    if not repos:
        print(f"⚠️  No repos found in {SETTINGS.github_dir}")
        print(f"   Set DREAMOS_GITHUB_DIR or DREAMOS_SAFE_REPOS env vars.")
        sys.exit(1)

    swarm, agents, registry = build_swarm(verbose=args.verbose)

    print(f"\n  🔧 Tools  : {registry.names()}")
    print(f"  👥 Agents : {[a.name for a in agents]}")
    print(f"  📝 Log    : {SETTINGS.log_file}")

    swarm.run(goal, repos)


if __name__ == "__main__":
    main()
