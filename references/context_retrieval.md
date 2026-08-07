# Context Retrieval

The vault is selected by `OBSIDIAN_VAULT_PATH`, then `--vault`, then `~/Documents/Obsidian Vault` (the explicit CLI path is useful for tests and isolated runs). Results are grouped by priority:

- P0: `Projects/{project_id}/project-summary.md` and accepted ADRs in `Decisions/`.
- P1: newest three files in `Execution-Reports/` by default.
- P2: `Knowledge/lessons-learned.md`.
- P3: archived material below `AI-Vault/Strategy/{Goals,Plans,Options,Reviews}`.

Each default item is metadata plus a short summary, never the full body. `full: true` can include body where supported. Missing optional tiers remain empty.
