# Handoff Protocol

The gateway validates four pillars: non-empty `goal`, `priorities`, `success_criteria`, and `constraints`. On success it emits a `task.dispatch` envelope with `target: hermes-orchestrator` and payload fields `strategy_id`, `project_id`, `goal`, `priorities`, `success_criteria`, `constraints`, and `knowledge_links`. The orchestrator is responsible for forwarding to `ai-development-manager`.
