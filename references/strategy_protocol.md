# Strategy Protocol

HACP v1.0 envelope:

```json
{"protocol":{"name":"HACP","version":"1.0"},"type":"strategy.context.request","payload":{}}
```

Allowed types are `strategy.context.request`, `strategy.knowledge.read`, `strategy.adr.propose`, and `strategy.handoff`. The gateway accepts no execution or provider-specific message. Required envelope fields are `protocol`, `type`, and `payload`; payload must be an object.
