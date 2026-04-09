#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dream.os REPL - Interactive Goal Runner
"""

import sys
import logging
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dreamos.config.settings import SETTINGS
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

# -----------------------------------------------------------------------------
# Tool Discovery
# -----------------------------------------------------------------------------

def get_available_tools() -> list:
    """Get list of available swarm tools from the tool registry."""
    try:
        registry = build_default_registry()
        return registry.names()
    except (ImportError, AttributeError) as e:
        logging.warning(f"Could not load tool registry: {e}. Using fallback list.")
        return ['status', 'pull', 'diff', 'add', 'commit', 'push', 'branch', 'lint', 'fix', 'format', 'test']

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

LOG_FILE: Path = Path("dreamos_logs/repl.log")
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [REPL] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Swarm Factory
# -----------------------------------------------------------------------------

def build_swarm_and_relay(verbose: bool = False):
    """Build and return swarm, transport, and relay."""
    log = setup_logger(log_file=SETTINGS.log_file, verbose=verbose)
    
    registry = build_default_registry()
    
    memory = Memory(persist_path=SETTINGS.graph_path.replace(".json", "_mem.json"))
    vectors = VectorMemory(SETTINGS.vector_db_path)
    graph = KnowledgeGraph(SETTINGS.graph_path)
    rag = RAGEngine(memory, vectors, graph)
    
    agents = [
        CognitiveAgent("GitMaster",  ["pull", "push", "commit", "status", "diff", "branch"], registry, rag),
        CognitiveAgent("LintLord",   ["lint", "fix", "format"], registry, rag),
        CognitiveAgent("TestRunner", ["test"], registry, rag),
        CognitiveAgent("MetaAgent",  ["status", "diff", "scan"], registry, rag),
    ]
    
    swarm = SwarmController(agents=agents, rag=rag, tool_registry=registry)
    
    # Setup bus/relay
    bus_root = Path(SETTINGS.github_dir).expanduser() / ".dreamos_bus"
    worker_node = "dreamos-worker"
    cli_node = "dreamos-cli"
    transport = FileTransport(bus_root=bus_root, nodes=[worker_node, cli_node])
    relay = DeviceRelay(
        node_id=worker_node,
        transport=transport,
        task_adapter=TaskAdapter(swarm),
    )
    
    return swarm, transport, relay, worker_node, cli_node


# -----------------------------------------------------------------------------
# REPL Implementation
# -----------------------------------------------------------------------------

class DreamRepl:
    """Interactive REPL for Dream.os goal execution."""
    
    def __init__(self) -> None:
        """Initialize REPL with swarm controller and relay."""
        print("🔧 Initializing Swarm Controller and Bus...")
        self.swarm, self.transport, self.relay, self.worker_node, self.cli_node = build_swarm_and_relay()
        self.running = True
        
    def run_goal(self, goal_text: str) -> bool:
        """Execute a goal using the bus/relay path."""
        print(f"\n📋 Goal: {goal_text}")
        print("🚌 Sending to bus...")
        
        try:
            # Find repos (same as main.py)
            def find_repos():
                github_dir = Path(SETTINGS.github_dir).expanduser().resolve()
                if not github_dir.is_dir():
                    return []
                repos = [str(p) for p in discover_git_repo_roots(github_dir)]
                if SETTINGS.safe_repos:
                    repos = [r for r in repos if SETTINGS.repo_is_safe(r)]
                return sorted(repos)
            
            repos = find_repos()
            if not repos:
                print("⚠️  No repos found. Check SETTINGS.github_dir")
                return False
            
            # Create and send message (same as main.py lines 95-105)
            message = BusMessage(
                from_agent=self.cli_node,
                to_agent=self.worker_node,
                msg_type="task",
                body=goal_text,
                device_hint=self.worker_node,
                meta={"goal": goal_text, "repos": repos},
            )
            
            print("📨 Sending message to bus...")
            self.transport.send(message)
            
            print("🔄 Polling for completion...")
            self.relay.poll_once()
            
            # Check result (same as main.py lines 107-111)
            complete_path = self.transport.bus_root / "complete" / f"{self.worker_node}__{message.id}.json"
            if complete_path.exists():
                final_message = load_message(complete_path)
                if final_message.result:
                    print(f"\n✅ Result: {final_message.result}")
                    logger.info(f"Goal succeeded: {goal_text[:100]}")
                    return True
                elif final_message.error:
                    print(f"\n❌ Error: {final_message.error}")
                    logger.error(f"Goal failed: {goal_text[:100]} - {final_message.error}")
                    return False
            else:
                print(f"\n⚠️  No completion message found at {complete_path}")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            logger.error(f"Goal failed: {goal_text[:100]} - {e}")
            return False
    
    def cmd_tools(self) -> None:
        """Display available swarm tools."""
        tools = get_available_tools()
        print("\n🔧 Available tools:")
        for tool in tools:
            print(f"   - {tool}")
    
    def cmd_help(self) -> None:
        """Display help text."""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                      Dream.os REPL Commands                       ║
╠══════════════════════════════════════════════════════════════════╣
║  goal: <description>  - Execute a goal with confirmation         ║
║  tools                - List all available tools                 ║
║  help                 - Show this help                           ║
║  exit / quit / Ctrl+C - Exit REPL                                ║
╚══════════════════════════════════════════════════════════════════╝

Examples:
  goal: status
  goal: run pytest on tests/
  goal: fix lint errors
""")
    
    def run(self) -> None:
        """Main REPL event loop."""
        print("\n" + "=" * 60)
        print("🎯 Dream.os REPL - Interactive Goal Runner")
        print("=" * 60)
        self.cmd_help()
        
        while self.running:
            try:
                user_input = input("\nDream.os> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'tools':
                    self.cmd_tools()
                elif user_input.lower() == 'help':
                    self.cmd_help()
                elif user_input.lower().startswith('goal:'):
                    goal = user_input[5:].strip()
                    if goal:
                        self.run_goal(goal)
                    else:
                        print("⚠️  No goal provided. Usage: goal: <description>")
                else:
                    print("❓ Unknown command. Type 'help' for options.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                logger.exception("REPL crash")


def main() -> None:
    """Entry point for REPL."""
    repl = DreamRepl()
    repl.run()


if __name__ == "__main__":
    main()