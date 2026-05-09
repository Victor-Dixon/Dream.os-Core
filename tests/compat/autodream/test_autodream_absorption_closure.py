from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_autodream_absorption_closure_report_exists():
    text = (ROOT / "_ops/reports/autodream_absorption_closure.md").read_text(encoding="utf-8")
    assert "AutoDream.Os is no longer present" in text
    assert "hard runtime or test dependency" in text


def test_autodream_salvage_documents_are_preserved():
    for rel in [
        "_ops/reports/autodream_inbound_consolidation_policy.md",
        "_ops/reports/autodream_message_queue_semantic_audit.md",
        "_ops/reports/autodream_message_fsm_compare.md",
    ]:
        assert (ROOT / rel).exists(), rel
