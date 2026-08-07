#!/usr/bin/env python3
"""HTTP transport for the HACP strategy gateway."""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple
from urllib.parse import urlparse

from adr_propose import propose
from context_retrieve import read_knowledge, retrieve
from handoff import handoff
from validate_strategy_task import validate

MAX_BODY_BYTES = 1024 * 1024
ACTION_TYPES = {
    "context": "strategy.context.request",
    "knowledge": "strategy.knowledge.read",
    "adr": "strategy.adr.propose",
    "handoff": "strategy.handoff",
}


def _error(code: str, message: str) -> Dict[str, str]:
    return {"code": code, "message": message}


def _envelope(http_status: int, result: Optional[Dict[str, Any]] = None,
              error: Optional[Dict[str, str]] = None,
              request_id: Any = None, trace_id: Any = None) -> Tuple[int, Dict[str, Any]]:
    body: Dict[str, Any] = {"status": "ok" if error is None else "error"}
    body["result" if error is None else "error"] = result if error is None else error
    if request_id is not None: body["request_id"] = request_id
    if trace_id is not None: body["trace_id"] = trace_id
    return http_status, body


def _vault(payload: Mapping[str, Any]) -> str:
    return (os.environ.get("OBSIDIAN_VAULT_PATH") or
            str(payload.get("vault") or (Path.home() / "Documents/Obsidian Vault")))


def _authenticate(headers: Mapping[str, str], payload: Mapping[str, Any]) -> Optional[Tuple[int, Dict[str, Any]]]:
    configured = os.environ.get("STRATEGY_GATEWAY_API_KEY")
    if not configured:
        return _envelope(503, error=_error("ERR-STR-007", "gateway API key is not configured"))
    nested_payload = payload.get("payload")
    nested_key = nested_payload.get("api_key") if isinstance(nested_payload, dict) else None
    supplied = headers.get("X-API-Key") or headers.get("x-api-key") or payload.get("api_key") or nested_key
    if not supplied:
        return _envelope(401, error=_error("ERR-STR-007", "API key is required"))
    if supplied != configured:
        return _envelope(403, error=_error("ERR-STR-008", "invalid API key"))
    return None


def _trace_fields(envelope: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Read trace metadata from payload first, then from the HACP envelope."""
    fields: Dict[str, Any] = {}
    for key in ("request_id", "trace_id"):
        value = payload[key] if key in payload else envelope.get(key)
        if value is not None:
            fields[key] = value
    return fields


def handle_request(method: str, path: str, headers: Optional[Mapping[str, str]] = None,
                   body: Any = None) -> Tuple[int, Dict[str, Any]]:
    """Handle a request without opening a socket; useful for offline tests."""
    headers = headers or {}
    parsed_path = urlparse(path).path
    if method.upper() == "GET" and parsed_path == "/health":
        return _envelope(200, result={"ok": True})
    if method.upper() != "POST" or not parsed_path.startswith("/strategy/"):
        return _envelope(404, error=_error("ERR-STR-007", "endpoint not found"))
    action = parsed_path[len("/strategy/"):]
    if action not in ACTION_TYPES:
        return _envelope(404, error=_error("ERR-STR-007", "endpoint not found"))
    if not isinstance(body, dict):
        return _envelope(400, error=_error("ERR-STR-007", "request body must be a JSON object"))

    auth_error = _authenticate(headers, body)
    if auth_error is not None:
        return auth_error
    validation = validate(body)
    if not validation["ok"]:
        validation_error = validation["error"]
        status = 403 if validation_error["code"] == "ERR-STR-008" else 400
        return _envelope(status, error=validation_error)
    if validation["type"] != ACTION_TYPES[action]:
        return _envelope(400, error=_error("ERR-STR-001", "message type does not match endpoint"))

    payload = dict(body["payload"])
    trace = _trace_fields(body, payload)
    payload.update(trace)
    try:
        if action == "context":
            if not payload.get("project_id"):
                return _envelope(400, error=_error("ERR-STR-002", "project_id is required"))
            result = retrieve(payload["project_id"], _vault(payload), bool(payload.get("full")), int(payload.get("recent", 3)), **trace)
        elif action == "knowledge":
            result = read_knowledge(payload, _vault(payload), **trace)
        elif action == "adr":
            result = propose(payload, _vault(payload), **trace)
        else:
            result = handoff(payload, **trace)
    except (OSError, ValueError, TypeError) as exc:
        return _envelope(400, error=_error("ERR-STR-003", str(exc)))
    if not result.get("ok", True):
        return _envelope(400, error=result.get("error", _error("ERR-STR-003", "strategy operation failed")))
    return _envelope(200, result=result, **trace)


class StrategyRequestHandler(BaseHTTPRequestHandler):
    """stdlib HTTP handler delegating semantics to ``handle_request``."""
    def _send(self, status: int, body: Dict[str, Any]) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        status, body = handle_request("GET", self.path, self.headers)
        self._send(status, body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0 or length > MAX_BODY_BYTES:
                self._send(413, {"status": "error", "error": _error("ERR-STR-007", "request body too large")})
                return
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._send(400, {"status": "error", "error": _error("ERR-STR-007", str(exc))})
            return
        status, response = handle_request("POST", self.path, self.headers, body)
        self._send(status, response)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="HACP strategy HTTP transport")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), StrategyRequestHandler)
    print(f"strategy gateway listening on {args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
