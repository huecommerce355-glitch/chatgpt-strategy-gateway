import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from handoff import handoff

def complete(): return {"strategy_id": "s1", "task_id": "t1", "project_id": "p1", "goal": "ship", "priorities": ["correctness"], "success_criteria": ["tests"], "constraints": ["offline"], "knowledge_links": []}
def test_four_pillars_forward_to_orchestrator():
    result = handoff(complete())
    assert result["forwarded_to"] == "hermes-orchestrator"
    assert result["dispatch"]["target"] == "hermes-orchestrator"
    assert result["dispatch"]["target"] != "ai-development-manager"
def test_missing_pillar_rejected():
    data = complete(); del data["constraints"]
    assert handoff(data)["error"]["code"] == "ERR-STR-002"
