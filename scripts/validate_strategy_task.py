#!/usr/bin/env python3
"""Validate HACP strategy envelopes."""
import argparse, json, sys

ALLOWED = {"strategy.context.request", "strategy.knowledge.read", "strategy.adr.propose", "strategy.handoff"}

def error(code, message): return {"ok": False, "error": {"code": code, "message": message}}

def validate(task):
    if not isinstance(task, dict): return error("ERR-STR-007", "input must be an object")
    protocol = task.get("protocol")
    if not isinstance(protocol, dict) or protocol.get("name") != "HACP" or protocol.get("version") != "1.0":
        return error("ERR-STR-007", "invalid HACP protocol")
    msg_type = task.get("type")
    if not isinstance(msg_type, str) or not msg_type.startswith("strategy."): return error("ERR-STR-008", "only strategy.* messages are permitted")
    if msg_type not in ALLOWED: return error("ERR-STR-001", "unsupported strategy message type")
    if not isinstance(task.get("payload"), dict): return error("ERR-STR-002", "payload is required")
    return {"ok": True, "protocol": protocol, "type": msg_type}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--input", required=True)
    try:
        with open(parser.parse_args().input, encoding="utf-8") as f: result = validate(json.load(f))
    except (OSError, json.JSONDecodeError) as exc: result = error("ERR-STR-007", str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result["ok"] else 1

if __name__ == "__main__": sys.exit(main())
