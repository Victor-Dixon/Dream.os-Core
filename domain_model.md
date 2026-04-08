# Domain Model (Evidence-Based)
**Date:** 2026-04-08 (UTC)

## 1) Proven Core Domain
The proven domain is a **message-driven swarm automation runtime** for repository operations.

## 2) Core Entities
- **BusMessage**: canonical task/result envelope with lifecycle state, routing hints, capabilities, and result/error payload.
- **MessageStatus**: lifecycle states used in execution guard transitions.
- **FileTransport**: filesystem-backed bus queues (`inbox`, `claimed`, `complete`).
- **DeviceRelay**: node-side receive/claim/execute/ack loop.
- **TaskAdapter**: constrained execution adapter from bus message to swarm run.
- **SwarmController**: decomposes goals into steps and coordinates agent execution per repo.
- **BaseAgent/CognitiveAgent**: execution workers with bidding and optional RAG memory influence.
- **RoutingPolicy/NodeProfile**: route scoring model for assigning task execution targets.
- **CommandMessage/CommandResult/InboundMessage**: phase2 contracts for listener/pipeline flow.

## 3) Domain Boundaries (Observed)
- **Inside proven runtime domain:** orchestration + transport + relay + contracts + tests.
- **Outside proven runtime domain:** historical ACP GUI/PyAutoGUI/Cursor-bidirectional capture claims (not present as active implementation in this tree).

## 4) Domain Confidence
- **domain_partial**: core runtime domain is clear, but broader product identity in docs is inconsistent with code reality.

