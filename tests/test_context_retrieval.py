import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from context_retrieve import retrieve

def write(root, rel, text):
    p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8"); return p
def test_p0_to_p3_aggregation_and_summary(tmp_path):
    vault = tmp_path / "AI-Vault"
    write(vault, "Projects/p1/project-summary.md", "# Summary\nproject body secret detail")
    write(vault, "Decisions/ADR-1-old.md", "---\nstatus: accepted\n---\naccepted decision body")
    for i in range(4): write(vault, f"Execution-Reports/r{i}.md", f"report {i} body")
    write(vault, "Knowledge/lessons-learned.md", "lesson body")
    write(vault, "Strategy/Plans/archive.md", "archive body")
    result = retrieve("p1", tmp_path)
    assert len(result["priorities"]["p0"]) == 2
    assert len(result["priorities"]["p1"]) == 3
    assert result["priorities"]["p2"] and result["priorities"]["p3"]
    assert all("body" not in entry for group in result["priorities"].values() for entry in group)
    assert "project body" in result["context_summary"]

def test_retrieve_regression_uses_ai_vault_paths(tmp_path):
    vault = tmp_path / "AI-Vault"
    adr = write(vault, "Decisions/ADR-1-greet-feature-adr.md", "---\nstatus: accepted\n---\naccepted ADR")
    summary = write(vault, "Projects/hermes-codex-test/project-summary.md", "project summary")
    report = write(vault, "Execution-Reports/greet-feature.md", "execution report")

    result = retrieve("hermes-codex-test", tmp_path)

    p0_paths = {entry["path"] for entry in result["priorities"]["p0"]}
    p1_paths = {entry["path"] for entry in result["priorities"]["p1"]}
    assert str(adr) in p0_paths
    assert str(summary) in p0_paths
    assert str(report) in p1_paths

def test_read_knowledge_resolves_paths_relative_to_ai_vault(tmp_path):
    from context_retrieve import read_knowledge

    document = write(tmp_path / "AI-Vault", "Decisions/ADR-1.md", "accepted decision")
    result = read_knowledge({"path": "Decisions/ADR-1.md", "full": True}, tmp_path)

    assert result["ok"] is True
    assert result["path"] == str(document.resolve())
    assert result["body"] == "accepted decision"

def test_read_knowledge_rejects_paths_outside_ai_vault(tmp_path):
    from context_retrieve import read_knowledge

    write(tmp_path, "outside.md", "must not be read")

    try:
        read_knowledge({"path": "../outside.md"}, tmp_path)
    except ValueError as exc:
        assert str(exc) == "document outside vault"
    else:
        raise AssertionError("expected outside-vault path to be rejected")
