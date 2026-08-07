import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from context_retrieve import retrieve

def write(root, rel, text):
    p = root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8"); return p
def test_p0_to_p3_aggregation_and_summary(tmp_path):
    write(tmp_path, "Projects/p1/project-summary.md", "# Summary\nproject body secret detail")
    write(tmp_path, "Decisions/ADR-1-old.md", "---\nstatus: accepted\n---\naccepted decision body")
    for i in range(4): write(tmp_path, f"Execution-Reports/r{i}.md", f"report {i} body")
    write(tmp_path, "Knowledge/lessons-learned.md", "lesson body")
    write(tmp_path, "AI-Vault/Strategy/Plans/archive.md", "archive body")
    result = retrieve("p1", tmp_path)
    assert len(result["priorities"]["p0"]) == 2
    assert len(result["priorities"]["p1"]) == 3
    assert result["priorities"]["p2"] and result["priorities"]["p3"]
    assert all("body" not in entry for group in result["priorities"].values() for entry in group)
    assert "project body" in result["context_summary"]
