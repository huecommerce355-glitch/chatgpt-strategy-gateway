#!/usr/bin/env python3
"""Create a safety-filtered proposed ADR."""
import argparse, json, re, sys
from pathlib import Path

def safety_filter(text): return not re.search(r"secret|\.env|token|PII", text, re.I)
def slugify(value): return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "decision"
def propose(payload, vault):
    status = payload.get("status", "proposed")
    if status != "proposed": return {"ok": False, "error": {"code": "ERR-STR-008", "message": "gateway may only create proposed ADRs"}}
    title = payload.get("title") or payload.get("decision")
    if not title: return {"ok": False, "error": {"code": "ERR-STR-002", "message": "title is required"}}
    fields = {k: payload.get(k, "") for k in ("context", "options", "decision", "rationale", "consequences")}; fields["decision"] = fields["decision"] or title
    if not safety_filter(json.dumps(payload, ensure_ascii=False)): return {"ok": False, "error": {"code": "ERR-STR-004", "message": "safety filter blocked sensitive content"}}
    directory = Path(vault) / "AI-Vault" / "Decisions"; directory.mkdir(parents=True, exist_ok=True)
    numbers = [int(m.group(1)) for p in directory.glob("ADR-*.md") if (m := re.match(r"ADR-(\d+)-", p.name))]
    number = max(numbers, default=0) + 1; path = directory / f"ADR-{number}-{slugify(title)}.md"
    text = f"---\ntitle: {title}\nstatus: proposed\nadr_number: {number}\n---\n\n# {title}\n\n## Context\n{fields['context']}\n\n## Options\n{fields['options']}\n\n## Decision\n{fields['decision']}\n\n## Rationale\n{fields['rationale']}\n\n## Consequences\n{fields['consequences']}\n"
    if not safety_filter(text): return {"ok": False, "error": {"code": "ERR-STR-004", "message": "safety filter blocked sensitive content"}}
    path.write_text(text, encoding="utf-8")
    return {"ok": True, "adr_number": number, "path": str(path), "status": "proposed"}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); args = ap.parse_args()
    try:
        data = json.load(open(args.input, encoding="utf-8")); payload = data.get("payload", data); vault = payload.get("vault") or str(Path.home() / "Documents/Obsidian Vault"); result = propose(payload, vault)
    except (OSError, json.JSONDecodeError) as exc: result = {"ok": False, "error": {"code": "ERR-STR-007", "message": str(exc)}}
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if result.get("ok") else 1
if __name__ == "__main__": sys.exit(main())
