import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from adr_propose import _update_index, propose


def payload(title):
    return {
        "title": title,
        "context": "context",
        "options": "A/B",
        "decision": "A",
        "rationale": "fit",
        "consequences": "tradeoff",
    }


def read_index(vault):
    return json.loads((vault / "AI-Vault" / ".knowledge-index.yaml").read_text(encoding="utf-8"))


def test_new_proposed_adr_index_entry_has_status_and_schema_fields(tmp_path):
    result = propose(payload("Proposed Status"), tmp_path)

    entry = next(item for item in read_index(tmp_path)["documents"] if item["title"] == "Proposed Status")
    assert entry["status"] == "proposed"
    assert entry["path"] == "Decisions/ADR-001-proposed-status.md"
    assert entry["type"] == "decision-record"


def test_status_update_changes_only_target_entry(tmp_path):
    result = propose(payload("Accepted Status"), tmp_path)
    entry = next(item for item in read_index(tmp_path)["documents"] if item["title"] == "Accepted Status")

    assert _update_index(tmp_path / "AI-Vault", entry, status="accepted")["ok"]
    updated = next(item for item in read_index(tmp_path)["documents"] if item["title"] == "Accepted Status")
    assert updated["status"] == "accepted"


def test_legacy_entry_without_status_remains_readable_after_new_write(tmp_path):
    root = tmp_path / "AI-Vault"
    root.mkdir(parents=True)
    legacy = {"path": "Decisions/ADR-003-legacy.md", "title": "Legacy", "type": "decision-record"}
    (root / ".knowledge-index.yaml").write_text(
        json.dumps({"last_indexed": None, "documents": [legacy]}), encoding="utf-8"
    )

    result = propose(payload("New Status"), tmp_path)

    assert result["ok"]
    documents = read_index(tmp_path)["documents"]
    assert next(item for item in documents if item["title"] == "Legacy") == legacy
    assert next(item for item in documents if item["title"] == "New Status")["status"] == "proposed"
