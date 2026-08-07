# chatgpt-strategy-gateway

ChatGPT Strategy Gateway - strategic boundary between ChatGPT and Hermes agent system (v1.0).

ChatGPT is the "strategy brain", Hermes is the "execution system". This gateway is the only boundary between them.

## Capabilities

- strategy.context.request: P0-P3 prioritized context retrieval
- strategy.knowledge.read: summary-first knowledge reads
- strategy.adr.propose: proposed-only ADR creation (accepted/superseded require human/orchestrator)
- strategy.handoff: 4-pillar validated handoff via hermes-orchestrator
- Security: ChatGPT never executes code / writes files / touches GitHub

## Tests

```bash
python3 -m pytest tests/ -v
```
