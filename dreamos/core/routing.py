"""Swarm-informed routing policy for task messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NodeProfile:
    node_id: str
    capabilities: List[str]
    active_tasks: int = 0
    health: str = "healthy"
    tags: List[str] = field(default_factory=list)


@dataclass
class RoutingDecision:
    node_id: Optional[str]
    score: float
    reason: str
    rejected: bool = False


class RoutingPolicy:
    """Calculate best execution target using swarm scoring + node signals."""

    def __init__(self, swarm, nodes: List[NodeProfile]):
        self.swarm = swarm
        self.nodes: Dict[str, NodeProfile] = {n.node_id: n for n in nodes}

    def route(self, message: Dict[str, Any]) -> RoutingDecision:
        required = message.get("required_capabilities", [])
        payload = message.get("payload", {})
        goal = payload.get("goal", "status")
        repo = payload.get("repo")
        preferred_tags = message.get("routing_hints", {}).get("preferred_tags", [])

        best_node = None
        best_score = -1.0
        best_reason = "no eligible node"

        for node in self.nodes.values():
            score, reason = self._score_node(node, goal, repo, required, preferred_tags)
            if score > best_score:
                best_score = score
                best_node = node
                best_reason = reason

        if best_node is None or best_score <= 0:
            return RoutingDecision(None, best_score, best_reason, rejected=True)

        return RoutingDecision(best_node.node_id, best_score, best_reason, rejected=False)

    def _score_node(
        self,
        node: NodeProfile,
        goal: str,
        repo: Optional[str],
        required_capabilities: List[str],
        preferred_tags: List[str],
    ) -> tuple[float, str]:
        if node.health != "healthy":
            return 0.0, f"{node.node_id} unhealthy"

        missing = [c for c in required_capabilities if c not in node.capabilities]
        if missing:
            return 0.0, f"{node.node_id} missing capabilities: {missing}"

        capability_score = 1.0
        load_penalty = min(node.active_tasks * 0.15, 0.75)
        tag_bonus = 0.20 if preferred_tags and any(t in node.tags for t in preferred_tags) else 0.0

        swarm_score = self.swarm.route_score(
            node_id=node.node_id,
            goal=goal,
            repo=repo,
            required_capabilities=required_capabilities,
        )

        total = capability_score + swarm_score + tag_bonus - load_penalty
        reason = (
            f"capability={capability_score:.2f}, "
            f"swarm={swarm_score:.2f}, "
            f"tag_bonus={tag_bonus:.2f}, "
            f"load_penalty={load_penalty:.2f}"
        )
        return max(total, 0.0), reason
