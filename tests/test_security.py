import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from validate_strategy_task import validate
from adr_propose import propose

def test_execution_attempt_is_permission_error():
    task = {"protocol": {"name": "HACP", "version": "1.0"}, "type": "shell.execute", "payload": {"command": "rm"}}
    assert validate(task)["error"]["code"] == "ERR-STR-008"
def test_safety_filter_blocks_secret_and_pii(tmp_path):
    for marker in ("secret value", "PII record"):
        result = propose({"title": "safe title", "context": marker}, tmp_path)
        assert result["error"]["code"] == "ERR-STR-004"
