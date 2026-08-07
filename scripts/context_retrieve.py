#!/usr/bin/env python3
"""Retrieve strategic context in P0-P3 priority groups."""
import argparse, json, os, re, sys
from pathlib import Path

def summary(text, full=False):
    text = text.strip()
    if full: return text
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.S)
    return " ".join(text.split())[:240]

def item(path, priority, full=False):
    try: body = path.read_text(encoding="utf-8")
    except OSError: return None
    result = {"path": str(path), "name": path.name, "priority": priority, "summary": summary(body, full)}
    if full: result["body"] = body
    return result

def retrieve(project_id, vault, full=False, recent=3):
    root = Path(vault).expanduser(); result = {"p0": [], "p1": [], "p2": [], "p3": []}
    project = root / "Projects" / project_id / "project-summary.md"
    if project.exists(): result["p0"].append(item(project, "P0", full))
    decisions = root / "Decisions"
    if decisions.exists():
        for path in sorted(decisions.glob("*.md")):
            body = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^status:\s*accepted\s*$", body, re.I | re.M): result["p0"].append(item(path, "P0", full))
    reports = root / "Execution-Reports"
    if reports.exists():
        paths = sorted(reports.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:recent]
        result["p1"].extend(filter(None, (item(p, "P1", full) for p in paths)))
    lessons = root / "Knowledge" / "lessons-learned.md"
    if lessons.exists(): result["p2"].append(item(lessons, "P2", full))
    for category in ("Goals", "Plans", "Options", "Reviews"):
        archive = root / "AI-Vault" / "Strategy" / category
        if archive.exists(): result["p3"].extend(filter(None, (item(p, "P3", full) for p in sorted(archive.rglob("*.md")))))
    for key in result: result[key] = [x for x in result[key] if x]
    parts = [f"{key.upper()}: " + "; ".join(x["summary"] for x in result[key]) for key in ("p0", "p1", "p2", "p3") if result[key]]
    return {"priorities": result, "context_summary": " | ".join(parts)}

def read_knowledge(payload, vault):
    requested = payload.get("path") or payload.get("document")
    if not requested: raise ValueError("path is required")
    root = Path(vault).expanduser().resolve(); path = (root / requested).resolve()
    if root not in path.parents and path != root: raise ValueError("document outside vault")
    if not path.is_file(): return {"ok": False, "error": {"code": "ERR-STR-005", "message": "document not found"}}
    body = path.read_text(encoding="utf-8")
    result = {"ok": True, "path": str(path), "summary": summary(body, False)}
    if payload.get("full"): result["body"] = body
    return result

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--project-id"); ap.add_argument("--input"); ap.add_argument("--vault"); ap.add_argument("--full", action="store_true"); ap.add_argument("--recent", type=int, default=3)
    args = ap.parse_args()
    try:
        data = json.load(open(args.input, encoding="utf-8")) if args.input else {}
        payload = data.get("payload", data)
        vault = os.environ.get("OBSIDIAN_VAULT_PATH") or args.vault or str(Path.home() / "Documents/Obsidian Vault")
        if data.get("type") == "strategy.knowledge.read":
            result = read_knowledge(payload, vault); print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result.get("ok") else 1
        project = args.project_id or payload.get("project_id")
        if not project: raise ValueError("project_id is required")
        print(json.dumps(retrieve(project, vault, args.full or payload.get("full", False), args.recent), ensure_ascii=False, indent=2)); return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": {"code": "ERR-STR-003", "message": str(exc)}}, ensure_ascii=False)); return 1
if __name__ == "__main__": sys.exit(main())
