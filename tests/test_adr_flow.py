import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from adr_propose import propose

def payload(title): return {"title": title, "context": "context", "options": "A/B", "decision": "A", "rationale": "fit", "consequences": "tradeoff"}
def test_proposed_adr_and_incrementing_number(tmp_path):
    first = propose(payload("First Choice"), tmp_path); second = propose(payload("Second Choice"), tmp_path)
    assert first["status"] == "proposed" and first["adr_number"] == 1 and Path(first["path"]).exists()
    assert second["adr_number"] == 2
    assert "status: proposed" in Path(first["path"]).read_text()
def test_non_proposed_is_permission_error(tmp_path):
    result = propose({**payload("Nope"), "status": "accepted"}, tmp_path)
    assert result["error"]["code"] == "ERR-STR-008"
def test_sensitive_content_is_blocked_without_write(tmp_path):
    result = propose({**payload("Unsafe"), "context": "token=abc"}, tmp_path)
    assert result["error"]["code"] == "ERR-STR-004"
    assert not (tmp_path / "AI-Vault" / "Decisions").exists()
