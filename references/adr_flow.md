# ADR Flow

`adr_propose.py` writes with the knowledge-gateway `write_knowledge` semantic to `AI-Vault/Decisions/ADR-{n}-{slug}.md`. It creates only `status: proposed`; approval and supersession are outside this gateway.

The supported Strategy document types are `goal`, `plan`, `option`, and `review`, mapped to `AI-Vault/Strategy/Goals/`, `Plans/`, `Options/`, and `Reviews/`. ADRs themselves remain under `Decisions/`. Safety filtering rejects `secret`, `.env`, `token`, and `PII` markers.
