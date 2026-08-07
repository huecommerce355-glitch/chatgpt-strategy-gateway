import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from http_adapter import handle_request


def envelope(kind, payload=None, **metadata):
    result = {
        "protocol": {"name": "HACP", "version": "1.0"},
        "type": kind,
        "payload": payload or {},
    }
    result.update(metadata)
    return result


def handoff_payload():
    return {
        "strategy_id": "s1", "task_id": "t1", "goal": "ship",
        "priorities": ["correctness"], "success_criteria": ["tests"],
        "constraints": ["offline"],
    }


def test_t3a_envelope_trace_id_reaches_handoff_dispatch(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    status, body = handle_request(
        "POST", "/strategy/handoff", {"X-API-Key": "key"},
        envelope("strategy.handoff", handoff_payload(), trace_id="trace-1"),
    )
    assert status == 200
    assert body["result"]["dispatch"]["payload"]["trace_id"] == "trace-1"


def test_t3b_request_id_is_echoed(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    status, body = handle_request(
        "POST", "/strategy/handoff", {"X-API-Key": "key"},
        envelope("strategy.handoff", handoff_payload(), request_id="req-1"),
    )
    assert status == 200 and body["request_id"] == "req-1"


def test_t3c_old_request_remains_compatible(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    status, body = handle_request(
        "POST", "/strategy/handoff", {"X-API-Key": "key"},
        envelope("strategy.handoff", handoff_payload()),
    )
    assert status == 200
    assert "request_id" not in body and "trace_id" not in body
    assert "request_id" not in body["result"]["dispatch"]["payload"]
    assert "trace_id" not in body["result"]["dispatch"]["payload"]


def test_t3d_payload_metadata_takes_precedence_end_to_end(monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    request = envelope(
        "strategy.handoff", {**handoff_payload(), "trace_id": "payload-trace", "request_id": "payload-request"},
        trace_id="envelope-trace", request_id="envelope-request",
    )
    status, body = handle_request("POST", "/strategy/handoff", {"X-API-Key": "key"}, request)
    dispatch = body["result"]["dispatch"]
    assert status == 200
    assert dispatch["type"] == "task.dispatch"
    assert dispatch["target"] == "hermes-orchestrator"
    assert dispatch["payload"]["trace_id"] == "payload-trace"
    assert dispatch["payload"]["request_id"] == "payload-request"
    assert body["trace_id"] == "payload-trace"
    assert body["request_id"] == "payload-request"
