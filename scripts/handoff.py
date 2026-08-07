#!/usr/bin/env python3
"""Validate and construct the orchestrator dispatch envelope."""
import argparse, json, sys
REQUIRED = ("goal", "priorities", "success_criteria", "constraints")
def handoff(payload):
    missing = [x for x in REQUIRED if not payload.get(x)]
    if missing: return {"ok": False, "error": {"code": "ERR-STR-002", "message": "missing pillars: " + ", ".join(missing)}}
    strategy_id = payload.get("strategy_id"); task_id = payload.get("task_id") or strategy_id
    if not strategy_id or not task_id: return {"ok": False, "error": {"code": "ERR-STR-002", "message": "strategy_id and task_id are required"}}
    dispatch = {"protocol": {"name": "HACP", "version": "1.0"}, "type": "task.dispatch", "target": "hermes-orchestrator", "payload": {k: payload.get(k) for k in ("strategy_id", "project_id", "goal", "priorities", "success_criteria", "constraints", "knowledge_links")}}
    return {"ok": True, "strategy_id": strategy_id, "task_id": task_id, "forwarded_to": "hermes-orchestrator", "dispatch": dispatch}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); args = ap.parse_args()
    try: data = json.load(open(args.input, encoding="utf-8")); result = handoff(data.get("payload", data))
    except (OSError, json.JSONDecodeError) as exc: result = {"ok": False, "error": {"code": "ERR-STR-007", "message": str(exc)}}
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result.get("ok") else 1
if __name__ == "__main__": sys.exit(main())
