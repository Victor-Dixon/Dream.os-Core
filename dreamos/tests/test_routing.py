"""tests/test_routing.py"""

from unittest.mock import MagicMock

from dreamos.core.message_router import MessageRouter
from dreamos.core.routing import NodeProfile, RoutingPolicy


class TestRoutingPolicy:
    def test_routes_to_highest_scored_node(self):
        swarm = MagicMock()

        def _score(node_id, goal, repo, required_capabilities):
            return 0.9 if node_id == "desktop-main" else 0.2

        swarm.route_score.side_effect = _score
        policy = RoutingPolicy(
            swarm=swarm,
            nodes=[
                NodeProfile("desktop-main", ["git", "lint"], tags=["desktop"]),
                NodeProfile("laptop-fallback", ["git", "lint"], tags=["laptop"]),
            ],
        )
        message = {
            "payload": {"goal": "fix lint", "repo": "/repo/a"},
            "required_capabilities": ["git", "lint"],
            "routing_hints": {"preferred_tags": ["desktop"]},
        }

        decision = policy.route(message)
        assert decision.rejected is False
        assert decision.node_id == "desktop-main"

    def test_rejects_when_no_capability_match(self):
        swarm = MagicMock()
        swarm.route_score.return_value = 0.7
        policy = RoutingPolicy(
            swarm=swarm,
            nodes=[NodeProfile("android-bridge", ["relay"])],
        )
        message = {
            "payload": {"goal": "run tests", "repo": "/repo/a"},
            "required_capabilities": ["test"],
        }

        decision = policy.route(message)
        assert decision.rejected is True
        assert decision.node_id is None


class TestMessageRouter:
    def test_marks_message_routed(self):
        swarm = MagicMock()
        swarm.route_score.return_value = 0.8
        router = MessageRouter(swarm, [NodeProfile("desktop-main", ["git"])])
        message = {
            "type": "task",
            "payload": {"goal": "status", "repo": "/repo/a"},
            "required_capabilities": ["git"],
        }

        routed = router.route_message(message)
        assert routed["state"] == "routed"
        assert routed["assigned_to"] == "desktop-main"
