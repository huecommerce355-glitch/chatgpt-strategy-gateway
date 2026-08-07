# HTTP Transport

v1.2 adds trace metadata passthrough to the thin HTTPS-facing adapter. HACP envelopes and the existing
`strategy.*` protocol do not change; HTTP only supplies routing, authentication,
JSON decoding, and response status mapping.

## Trace passthrough

`request_id` and `trace_id` may be supplied in the request `payload` or at the
HACP envelope level. Payload values take precedence when the same field appears
in both locations. The adapter passes the metadata to the selected business
script. A handoff preserves it in the outgoing `task.dispatch.payload`, and
successful HTTP responses echo it at the response top level. Requests without
these fields retain the v1.1 response and dispatch shapes.

## Endpoints

- `GET /health` is unauthenticated and returns HTTP 200 when the process is up.
- `POST /strategy/context` accepts `strategy.context.request`.
- `POST /strategy/knowledge` accepts `strategy.knowledge.read`.
- `POST /strategy/adr` accepts `strategy.adr.propose`.
- `POST /strategy/handoff` accepts `strategy.handoff`.

The request body is an HACP envelope. `X-API-Key` is preferred; `payload.api_key`
is accepted for clients that cannot set the header. The server compares the
provided value with `STRATEGY_GATEWAY_API_KEY`. If that environment variable is
absent, every protected request returns 503 (`ERR-STR-007`). Missing credentials
return 401; an incorrect credential returns 403.

## Boundary and errors

The adapter calls the existing `validate()` before dispatch. Non-`strategy.*`
messages are HTTP 403 with `ERR-STR-008`; malformed HACP protocol is HTTP 400
with `ERR-STR-007`. The endpoint action must match the strategy message type.
Business errors retain their existing `ERR-STR-*` code in the top-level
`{"status":"error","error":{...}}` response.

## Deployment

Run `python3 scripts/http_adapter.py --host 127.0.0.1 --port 8080` behind an
HTTPS reverse proxy or a custom GPT Action HTTPS endpoint. Set
`STRATEGY_GATEWAY_API_KEY` and, when applicable, `OBSIDIAN_VAULT_PATH` in the
service environment. Do not expose the development HTTP listener directly to
the public internet; terminate TLS, restrict ingress, and keep the API key out
of logs and documents.
