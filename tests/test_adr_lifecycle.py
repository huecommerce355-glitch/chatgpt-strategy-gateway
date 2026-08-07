import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from context_retrieve import retrieve


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_adr_lifecycle_states_are_defined_in_doc():
    document = (Path(__file__).parents[1] / "references" / "adr_flow.md").read_text(encoding="utf-8")
    lowered = document.lower()
    assert "## adr lifecycle" in lowered
    assert "proposed" in lowered
    assert "accepted" in lowered
    assert "superseded" in lowered


def test_accepted_adr_is_prioritized_in_context(tmp_path):
    decisions = tmp_path / "AI-Vault" / "Decisions"
    accepted = write(decisions, "ADR-1-accepted.md", "---\nstatus: accepted\n---\naccepted decision")
    proposed = write(decisions, "ADR-2-proposed.md", "---\nstatus: proposed\n---\nproposed decision")

    result = retrieve("demo", tmp_path)

    p0_paths = {entry["path"] for entry in result["priorities"]["p0"]}
    assert p0_paths == {str(accepted)}
    assert str(proposed) not in p0_paths
