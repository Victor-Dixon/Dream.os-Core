from src.core.execution_guard import ALLOWED_TRANSITIONS

AUTODREAM_TO_DREAMOS_STATE = {
    "pending": "new",
    "processing": "running",
    "delivered": "complete",
    "retry": "failed",
    "failed": "failed",
    "expired": "expired",
}

def test_autodream_state_mapping_targets_canonical_states():
    canonical = set(ALLOWED_TRANSITIONS)
    for mapped in AUTODREAM_TO_DREAMOS_STATE.values():
        assert mapped in canonical

def test_autodream_state_mapping_does_not_extend_canonical_fsm():
    assert "pending" not in ALLOWED_TRANSITIONS
    assert "processing" not in ALLOWED_TRANSITIONS
    assert "delivered" not in ALLOWED_TRANSITIONS

def test_autodream_state_mapping_preserves_terminal_failure_states():
    assert AUTODREAM_TO_DREAMOS_STATE["failed"] == "failed"
    assert AUTODREAM_TO_DREAMOS_STATE["expired"] == "expired"
