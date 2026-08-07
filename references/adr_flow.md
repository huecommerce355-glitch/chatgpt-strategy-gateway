# ADR Flow

`adr_propose.py` writes with the knowledge-gateway `write_knowledge` semantic to `AI-Vault/Decisions/ADR-{n}-{slug}.md`. It creates only `status: proposed`; approval and supersession are outside this gateway.

The supported Strategy document types are `goal`, `plan`, `option`, and `review`, mapped to `AI-Vault/Strategy/Goals/`, `Plans/`, `Options/`, and `Reviews/`. ADRs themselves remain under `Decisions/`. Safety filtering rejects `secret`, `.env`, `token`, and `PII` markers.

## ADR Lifecycle

| 状态 | 含义 | 谁可设置 |
|---|---|---|
| `proposed` | AI 生成的待确认建议；`strategy-gateway` 可创建此状态的 ADR。 | `strategy-gateway` |
| `accepted` | 已由人工或编排流程确认并采纳的决策。 | 人工批准流程或编排层 |
| `superseded` | 已被新的 ADR 取代、因此不再作为当前决策的旧 ADR。 | 人工批准流程或编排层 |
