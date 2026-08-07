# Strategy Protocol

HACP v1.0 envelope:

```json
{"protocol":{"name":"HACP","version":"1.0"},"type":"strategy.context.request","payload":{}}
```

Allowed types are `strategy.context.request`, `strategy.knowledge.read`, `strategy.adr.propose`, and `strategy.handoff`. The gateway accepts no execution or provider-specific message. Required envelope fields are `protocol`, `type`, and `payload`; payload must be an object.

## HTTP transport

HTTP is an optional transport adapter introduced in v1.1; it does not alter HACP
or the allowed message types. Protected `POST /strategy/{action}` requests use
`X-API-Key` (with `payload.api_key` as a compatibility fallback), while
`GET /health` is unauthenticated. The adapter validates the same envelope with
`validate()` and then dispatches to the existing strategy functions. See
`references/http_transport.md` and `references/openapi.yaml` for the HTTP
contract and deployment guidance.
