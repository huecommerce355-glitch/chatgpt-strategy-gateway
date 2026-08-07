import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from http_adapter import handle_request


def envelope(kind, payload=None, api_key=None):
    result = {
        "protocol": {"name": "HACP", "version": "1.0"},
        "type": kind,
        "payload": payload or {},
    }
    if api_key is not None:
        result["api_key"] = api_key
    return result


def test_health_is_public(monkeypatch):
    monkeypatch.delenv("STRATEGY_GATEWAY_API_KEY", raising=False)
    status, body = handle_request("GET", "/health")
    assert status == 200 and body == {"status": "ok", "result": {"ok": True}}


def test_missing_and_wrong_key_are_rejected(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "correct")
    request = envelope("strategy.handoff", {})
    assert handle_request("POST", "/strategy/handoff", body=request)[0] == 401
    status, body = handle_request("POST", "/strategy/handoff", {"X-API-Key": "wrong"}, request)
    assert status == 403 and body["error"]["code"] == "ERR-STR-008"


def test_unconfigured_key_is_service_error(monkeypatch):
    monkeypatch.delenv("STRATEGY_GATEWAY_API_KEY", raising=False)
    status, body = handle_request("POST", "/strategy/context", body=envelope("strategy.context.request"))
    assert status == 503 and body["error"]["code"] == "ERR-STR-007"


def test_non_strategy_message_is_boundary_error(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    status, body = handle_request("POST", "/strategy/context", {"X-API-Key": "key"}, envelope("task.execute"))
    assert status == 403 and body["error"]["code"] == "ERR-STR-008"


def test_protocol_validation_is_preserved(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    request = envelope("strategy.context.request", {"project_id": "p1"})
    request["protocol"]["version"] = "2.0"
    status, body = handle_request("POST", "/strategy/context", {"X-API-Key": "key"}, request)
    assert status == 400 and body["error"]["code"] == "ERR-STR-007"


def test_context_adr_and_handoff_dispatch(monkeypatch, tmp_path):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path))
    (tmp_path / "AI-Vault" / "Projects" / "p1").mkdir(parents=True)
    (tmp_path / "AI-Vault" / "Projects" / "p1" / "project-summary.md").write_text("summary", encoding="utf-8")
    headers = {"X-API-Key": "key"}

    status, body = handle_request("POST", "/strategy/context", headers,
                                  envelope("strategy.context.request", {"project_id": "p1"}))
    assert status == 200 and body["result"]["priorities"]["p0"]

    adr_payload = {"title": "HTTP transport", "context": "ctx", "options": "A/B",
                   "decision": "A", "rationale": "fit", "consequences": "tradeoff"}
    status, body = handle_request("POST", "/strategy/adr", headers,
                                  envelope("strategy.adr.propose", adr_payload))
    assert status == 200 and body["result"]["status"] == "proposed"

    handoff_payload = {"strategy_id": "s1", "task_id": "t1", "goal": "ship",
                       "priorities": ["correctness"], "success_criteria": ["tests"],
                       "constraints": ["offline"]}
    status, body = handle_request("POST", "/strategy/handoff", headers,
                                  envelope("strategy.handoff", handoff_payload))
    assert status == 200 and body["result"]["forwarded_to"] == "hermes-orchestrator"
