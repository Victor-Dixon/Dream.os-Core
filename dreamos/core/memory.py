"""
core/memory.py — Shared memory: episodic logs, failure tracking, affinity scores.

VectorMemory and RAGEngine are lightweight stubs ready to swap in
ChromaDB / FAISS when you're ready for semantic retrieval.
"""

import json
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Episodic Memory ───────────────────────────────────────────────────────────

class Memory:
    """
    Thread-safe episodic log + failure-pattern tracker.
    All agents share one instance via the swarm.
    """

    def __init__(self, persist_path: Optional[str] = None):
        self._log: List[Dict] = []
        self._failures: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._path = Path(persist_path) if persist_path else None

        if self._path and self._path.exists():
            self._load()

    # ── Public API ────────────────────────────────────────────────────────────

    def record(
        self,
        goal: str,
        tool: str,
        repo: str,
        result: Dict,
        worker: str,
    ):
        entry = {
            "goal": goal,
            "tool": tool,
            "repo": repo,
            "ok": result.get("ok", False),
            "worker": worker,
            "ts": datetime.utcnow().isoformat(),
        }
        with self._lock:
            self._log.append(entry)
            if not entry["ok"]:
                self._failures[f"{tool}::{repo}"] += 1

        if self._path:
            self._save()

    def affinity(self, repo: str, worker: str) -> float:
        """0–1 score: how well has this worker done on this repo before?"""
        with self._lock:
            relevant = [
                e for e in self._log
                if e["repo"] == repo and e["worker"] == worker
            ]
        if not relevant:
            return 0.5  # neutral
        hits = sum(1 for e in relevant if e["ok"])
        return hits / len(relevant)

    def failure_count(self, tool: str, repo: str) -> int:
        with self._lock:
            return self._failures[f"{tool}::{repo}"]

    def should_avoid(self, tool: str, repo: str, threshold: int = 2) -> bool:
        return self.failure_count(tool, repo) >= threshold

    def recent(self, n: int = 20) -> List[Dict]:
        with self._lock:
            return list(self._log[-n:])

    def summary(self) -> Dict:
        with self._lock:
            total = len(self._log)
            ok = sum(1 for e in self._log if e["ok"])
        return {
            "total_actions": total,
            "successes": ok,
            "failures": total - ok,
            "success_rate": round(ok / total, 2) if total else 0.0,
        }

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self):
        try:
            data = {"log": self._log[-500:], "failures": dict(self._failures)}
            self._path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass  # don't crash the swarm over a log write

    def _load(self):
        try:
            data = json.loads(self._path.read_text())
            self._log = data.get("log", [])
            self._failures = defaultdict(int, data.get("failures", {}))
        except Exception:
            pass


# ── Vector Memory (stub — swap in ChromaDB / FAISS) ──────────────────────────

class VectorMemory:
    """
    Lightweight in-memory vector store stub.
    Replace `add` / `query` with real embeddings when needed.
    """

    def __init__(self, path: Optional[str] = None):
        self._store: List[Dict] = []
        self._path = Path(path) if path else None

    def add(self, text: str, metadata: Dict = None):
        self._store.append({"text": text, "meta": metadata or {}})

    def query(self, text: str, top_k: int = 3) -> List[Dict]:
        """Naive keyword match — replace with cosine similarity."""
        words = set(text.lower().split())
        scored = []
        for item in self._store:
            overlap = words & set(item["text"].lower().split())
            if overlap:
                scored.append((len(overlap), item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]


# ── Knowledge Graph (lightweight JSON-backed) ─────────────────────────────────

class KnowledgeGraph:
    """
    Simple directed graph: node → {edges, metadata}.
    Backed by a JSON file. Swap for NetworkX / Neo4j later.
    """

    def __init__(self, path: Optional[str] = None):
        self._nodes: Dict[str, Dict] = {}
        self._path = Path(path) if path else None
        if self._path and self._path.exists():
            self._load()

    def add_node(self, key: str, **meta):
        self._nodes.setdefault(key, {"edges": [], "meta": {}})
        self._nodes[key]["meta"].update(meta)
        self._save()

    def add_edge(self, src: str, dst: str, label: str = ""):
        self.add_node(src)
        self.add_node(dst)
        edge = {"to": dst, "label": label}
        if edge not in self._nodes[src]["edges"]:
            self._nodes[src]["edges"].append(edge)
        self._save()

    def neighbors(self, key: str) -> List[str]:
        return [e["to"] for e in self._nodes.get(key, {}).get("edges", [])]

    def _save(self):
        if self._path:
            try:
                self._path.write_text(json.dumps(self._nodes, indent=2))
            except Exception:
                pass

    def _load(self):
        try:
            self._nodes = json.loads(self._path.read_text())
        except Exception:
            pass


# ── RAG Engine ────────────────────────────────────────────────────────────────

class RAGEngine:
    """
    Retrieval-Augmented Generation context provider.
    Combines episodic memory + vector store + knowledge graph.
    """

    def __init__(
        self,
        memory: Memory,
        vector_store: Optional[VectorMemory] = None,
        knowledge_graph: Optional[KnowledgeGraph] = None,
    ):
        self.memory = memory
        self.vectors = vector_store or VectorMemory()
        self.graph = knowledge_graph or KnowledgeGraph()

    def get_context(self, repo: str, tool: str) -> Dict[str, Any]:
        """Build context dict for an agent before it executes."""
        warnings = []

        # Check failure history
        failures = self.memory.failure_count(tool, repo)
        if failures > 0:
            warnings.append(f"{tool} has failed {failures}x on this repo before")

        # Check related nodes in knowledge graph
        related = self.graph.neighbors(f"{tool}::{repo}")

        # Retrieve similar past events
        similar = self.vectors.query(f"{tool} {repo}", top_k=2)

        return {
            "warnings": warnings,
            "related": related,
            "similar_events": [s["text"] for s in similar],
        }

    def learn(self, repo: str, tool: str, result: Dict, worker: str, goal: str = ""):
        """Update all memory systems after a tool execution."""
        self.memory.record(goal, tool, repo, result, worker)

        # Index into vector store
        status = "succeeded" if result.get("ok") else "failed"
        text = f"{tool} {status} on {repo}"
        if result.get("error"):
            text += f": {result['error']}"
        self.vectors.add(text, metadata={"tool": tool, "repo": repo, "ok": result.get("ok")})

        # Update knowledge graph
        self.graph.add_node(f"{tool}::{repo}", last_status=status)
        if not result.get("ok"):
            self.graph.add_edge(f"{tool}::{repo}", "failures", label="has")

    def recall_repo_affinity(self, repo: str, worker: str) -> float:
        return self.memory.affinity(repo, worker)
