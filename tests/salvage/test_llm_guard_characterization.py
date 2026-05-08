from pathlib import Path

SOURCE = Path(
    "/data/data/com.termux/files/home/projects/_STAGING/"
    "dreamos_incoming_unique/"
    "dream-os-hardened-v33-1/"
    "dream-os-hardened/core/llm_guard.js"
)

def test_source_exists():
    assert SOURCE.exists()

def test_guard_contains_validation_language():
    text = SOURCE.read_text(encoding="utf-8").lower()
    signals = [
        "validate",
        "prompt",
        "block",
    ]
    assert any(s in text for s in signals)

def test_guard_is_nontrivial():
    text = SOURCE.read_text(encoding="utf-8")
    assert len(text) > 1000
