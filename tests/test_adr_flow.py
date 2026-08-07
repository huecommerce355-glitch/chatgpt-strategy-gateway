import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from adr_propose import propose

def payload(title): return {"title": title, "context": "context", "options": "A/B", "decision": "A", "rationale": "fit", "consequences": "tradeoff"}

def test_proposed_adr_and_incrementing_number(tmp_path):
    directory = tmp_path / "AI-Vault" / "Decisions"
    directory.mkdir(parents=True)
    (directory / "ADR-1-historical.md").write_text("historical", encoding="utf-8")
    result = propose(payload("Second Choice"), tmp_path)
    assert result["status"] == "proposed" and result["adr_number"] == 2
    assert Path(result["path"]).name == "ADR-002-second-choice.md"
    assert Path(result["path"]).exists()
    assert "status: proposed" in Path(result["path"]).read_text()

def test_written_adr_is_added_to_knowledge_index(tmp_path):
    result = propose({**payload("Indexed Choice"), "project_id": "demo", "tags": ["phase7b"]}, tmp_path)
    index = json.loads((tmp_path / "AI-Vault" / ".knowledge-index.yaml").read_text(encoding="utf-8"))
    entry = next(item for item in index["documents"] if item["title"] == "Indexed Choice")
    assert entry["path"] == "Decisions/ADR-001-indexed-choice.md"
    assert entry["type"] == "decision-record"
    assert entry["project_id"] == "demo"
    assert entry["tags"] == ["phase7b"]
    assert entry["date"]
    assert index["last_indexed"]

def test_corrupt_knowledge_index_is_reported(tmp_path):
    index = tmp_path / "AI-Vault" / ".knowledge-index.yaml"
    index.parent.mkdir(parents=True)
    index.write_text("not yaml/json", encoding="utf-8")
    result = propose(payload("Corrupt Index"), tmp_path)
    assert result["ok"] is False
    assert result["error"]["code"] == "ERR-KNG-006"

def test_non_proposed_is_permission_error(tmp_path):
    result = propose({**payload("Nope"), "status": "accepted"}, tmp_path)
    assert result["error"]["code"] == "ERR-STR-008"
def test_sensitive_content_is_blocked_without_write(tmp_path):
    result = propose({**payload("Unsafe"), "context": "token=abc"}, tmp_path)
    assert result["error"]["code"] == "ERR-STR-004"
    assert not (tmp_path / "AI-Vault" / "Decisions").exists()
