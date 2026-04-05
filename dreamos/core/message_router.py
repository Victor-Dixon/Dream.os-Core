"""Message router that asks swarm-informed policy for target node."""

from __future__ import annotations

from typing import Any, Dict, List

from .routing import NodeProfile, RoutingPolicy


class MessageRouter:
    def __init__(self, swarm, nodes: List[NodeProfile]):
        self.policy = RoutingPolicy(swarm=swarm, nodes=nodes)

    def route_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        decision = self.policy.route(message)

        if decision.rejected:
            message["state"] = "blocked"
            message["routing"] = {
                "node_id": None,
                "score": decision.score,
                "reason": decision.reason,
            }
            return message

        message["state"] = "routed"
        message["assigned_to"] = decision.node_id
        message["routing"] = {
            "node_id": decision.node_id,
            "score": decision.score,
            "reason": decision.reason,
        }
        return message


def default_nodes() -> List[NodeProfile]:
    return [
        NodeProfile(
            node_id="desktop-main",
            capabilities=["git", "lint", "test"],
            active_tasks=0,
            health="healthy",
            tags=["desktop", "primary"],
        ),
        NodeProfile(
            node_id="laptop-fallback",
            capabilities=["git", "lint"],
            active_tasks=1,
            health="healthy",
            tags=["laptop", "secondary"],
        ),
        NodeProfile(
            node_id="android-bridge",
            capabilities=["relay"],
            active_tasks=0,
            health="healthy",
            tags=["mobile", "control-plane"],
        ),
    ]
