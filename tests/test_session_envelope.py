import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
from http_adapter import handle_request


def envelope(payload=None, **metadata):
    result = {
        "protocol": {"name": "HACP", "version": "1.0"},
        "type": "strategy.handoff",
        "payload": payload or {},
    }
    result.update(metadata)
    return result


def handoff_payload(**extra):
    return {
        "strategy_id": "s1", "task_id": "t1", "goal": "ship",
        "priorities": ["correctness"], "success_criteria": ["tests"],
        "constraints": ["offline"], **extra,
    }


def call(request, monkeypatch):
    monkeypatch.setenv("STRATEGY_GATEWAY_API_KEY", "key")
    return handle_request("POST", "/strategy/handoff", {"X-API-Key": "key"}, request)


def test_envelope_session_id_is_echoed(monkeypatch):
    status, body = call(envelope(handoff_payload(), session_id="session-1"), monkeypatch)
    assert status == 200
    assert body["session_id"] == "session-1"
    assert body["result"]["dispatch"]["payload"]["session_id"] == "session-1"


def test_payload_session_id_takes_precedence(monkeypatch):
    request = envelope(handoff_payload(session_id="payload-session"), session_id="envelope-session")
    status, body = call(request, monkeypatch)
    assert status == 200
    assert body["session_id"] == "payload-session"
    assert body["result"]["dispatch"]["payload"]["session_id"] == "payload-session"


def test_missing_protocol_or_type_returns_invalid_envelope_error(monkeypatch):
    request = envelope(handoff_payload())
    del request["protocol"]
    status, body = call(request, monkeypatch)
    assert status == 400
    assert body["error"]["code"] == "ERR-STR-009"

    request = envelope(handoff_payload())
    del request["type"]
    status, body = call(request, monkeypatch)
    assert status == 400
    assert body["error"]["code"] == "ERR-STR-009"


def test_case_insensitive_envelope_members_are_normalized(monkeypatch):
    request = {
        "Protocol": {"Name": "HACP", "Version": "1.0"},
        "Type": "strategy.handoff",
        "Payload": handoff_payload(),
    }
    status, body = call(request, monkeypatch)
    assert status == 200 and body["result"]["dispatch"]["type"] == "task.dispatch"


def test_old_request_has_no_session_or_trace_injection(monkeypatch):
    status, body = call(envelope(handoff_payload()), monkeypatch)
    assert status == 200
    assert "session_id" not in body and "request_id" not in body and "trace_id" not in body
    dispatch_payload = body["result"]["dispatch"]["payload"]
    assert "session_id" not in dispatch_payload
    assert "request_id" not in dispatch_payload
    assert "trace_id" not in dispatch_payload


def test_trace_and_session_are_forwarded_together(monkeypatch):
    request = envelope(
        handoff_payload(request_id="payload-request", trace_id="payload-trace", session_id="payload-session"),
        request_id="envelope-request", trace_id="envelope-trace", session_id="envelope-session",
    )
    status, body = call(request, monkeypatch)
    forwarded = body["result"]["dispatch"]["payload"]
    assert status == 200
    assert {key: forwarded[key] for key in ("request_id", "trace_id", "session_id")} == {
        "request_id": "payload-request", "trace_id": "payload-trace", "session_id": "payload-session",
    }
