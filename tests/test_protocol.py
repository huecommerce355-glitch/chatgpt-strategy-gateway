import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_strategy_task import validate

def envelope(kind="strategy.context.request"):
    return {"protocol": {"name": "HACP", "version": "1.0"}, "type": kind, "payload": {}}
def test_valid_strategy_types_pass():
    for kind in ("strategy.context.request", "strategy.knowledge.read", "strategy.adr.propose", "strategy.handoff"):
        assert validate(envelope(kind))["ok"]
def test_non_strategy_is_permission_error():
    assert validate(envelope("task.execute"))["error"]["code"] == "ERR-STR-008"
def test_protocol_is_structured_and_exact():
    bad = envelope(); bad["protocol"] = {"name": "HACP", "version": "2.0"}
    assert validate(bad)["error"]["code"] == "ERR-STR-007"
