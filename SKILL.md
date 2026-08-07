---
name: chatgpt-strategy-gateway
description: "Strategic boundary for ChatGPT-to-Hermes strategy tasks: context retrieval, ADR proposals, and orchestrated handoff."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: ["linux", "macos"]
metadata:
  hermes:
    tags: [strategy, gateway, HACP, orchestration, knowledge]
    related_skills: [hermes-orchestrator, ai-development-manager, obsidian-knowledge-gateway, hermes-gateway-registry, coding-agent-gateway]
---

# ChatGPT Strategy Gateway

## Overview

`chatgpt-strategy-gateway` 是 ChatGPT 与 Hermes 多 Agent 体系之间的唯一战略交互边界。ChatGPT 是战略大脑，只发送结构化 `strategy.*` 消息；Hermes 负责执行。Gateway 不执行代码、没有 terminal、文件写入或 GitHub 写权限。

## When to Use

用于战略上下文检索（`strategy.context.request`）、知识读取（`strategy.knowledge.read`）、提出待人工确认的 ADR（`strategy.adr.propose`）和把完整战略任务交给 Hermes 编排层（`strategy.handoff`）。

不要用于直接执行编码或直接 GitHub 操作；应委托 coding-agent-gateway / github gateway。不要直接调用 `ai-development-manager`；handoff 必须经 `hermes-orchestrator` 转发。

## How to Load

先读取相关 `references/*.md`，再运行对应 `scripts/*.py`。所有脚本仅依赖 Python 3.9+ 标准库，输入为 JSON，输出为 JSON；失败时使用 `ERR-STR-*` 并返回非零退出码。

## Core Architecture

```text
ChatGPT → chatgpt-strategy-gateway → registry / knowledge / orchestrator
                                      ├─ context_retrieve.py
                                      ├─ adr_propose.py → knowledge-gateway semantics
                                      └─ handoff.py → hermes-orchestrator → ai-development-manager
```

协议为 `{name: "HACP", version: "1.0"}`，消息类型前缀必须是 `strategy.`。

## HTTP Transport (v1.2)

HTTP 适配层与 HACP 协议层分离，消息信封保持不变。`GET /health` 无需认证；
`POST /strategy/context`、`/strategy/knowledge`、`/strategy/adr` 和
`/strategy/handoff` 使用 `X-API-Key`（或 payload 中的 `api_key`）认证。服务端
从 `STRATEGY_GATEWAY_API_KEY` 读取密钥，未配置时受保护请求返回 503。只有与
端点匹配的 `strategy.*` 类型可被转发，非 strategy 消息返回 403 和
`ERR-STR-008`。详见 [HTTP transport](references/http_transport.md) 与
[OpenAPI](references/openapi.yaml)。

### Trace Passthrough

`strategy.*` 请求可在 `payload` 或 HACP 信封顶层携带 `request_id` 和/或
`trace_id`。payload 字段优先，信封级字段作为兼容回退。HTTP adapter 会将
这些字段传给 context、knowledge、ADR 和 handoff 业务脚本；handoff 生成的
`task.dispatch.payload` 保留相同字段，HTTP 响应也回显请求级字段。没有 trace
字段的旧请求保持原有输出结构。

## Four Approved Corrections

1. ADR 只能以 `status=proposed` 创建；`accepted` / `superseded` 由人工或编排层确认，脚本拒绝越权状态。
2. Handoff 先验证 `goal`, `priorities`, `success_criteria`, `constraints` 四支柱，再生成 `task.dispatch` 给 `hermes-orchestrator`。
3. 战略知识位于 `AI-Vault/Strategy/{Goals,Plans,Options,Reviews}`，ADR 位于 `AI-Vault/Decisions/`。
4. Context 按 P0（项目摘要、accepted ADR）、P1（最近执行报告）、P2（经验教训）、P3（Strategy 归档）聚合。

## Error Codes

| Code | Meaning |
|---|---|
| ERR-STR-001 | 无效消息类型 |
| ERR-STR-002 | 必填字段缺失 |
| ERR-STR-003 | 检索失败 |
| ERR-STR-004 | ADR 安全拦截 |
| ERR-STR-005 | 文档不存在 |
| ERR-STR-006 | 转交失败 |
| ERR-STR-007 | 输入无效 |
| ERR-STR-008 | 权限越界（含非 proposed ADR） |

## Common Pitfalls

- 任何非 `strategy.*` 的消息都是权限越界；Gateway 不接受执行类操作。
- ADR 的 `proposed` 是权限边界，不是审批结果；不能由 ChatGPT 伪造 accepted。
- handoff 的 target 永远是 `hermes-orchestrator`，不能写成 `ai-development-manager`。
- 不要把 token、secret、`.env` 或 PII 放进 ADR；安全过滤失败必须停止写入。
- `OBSIDIAN_VAULT_PATH` 优先于默认 `~/Documents/Obsidian Vault`。

## Verification Checklist

- HACP protocol 和 `strategy.*` 类型通过验证。
- context 输出包含 p0–p3 和 `context_summary`，默认不泄露正文。
- ADR 文件编号递增、状态为 proposed，且安全过滤生效。
- 四支柱完整后只向 orchestrator 生成 `task.dispatch`。
- 运行 `python3 -m pytest tests/ -v` 并检查非零错误路径。

## Related Skills

`hermes-orchestrator`, `ai-development-manager`, `obsidian-knowledge-gateway`, `hermes-gateway-registry`, `coding-agent-gateway`
