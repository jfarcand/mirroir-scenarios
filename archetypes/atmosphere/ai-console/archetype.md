```yaml
version: 1
name: atmosphere/ai-console
archetype_version: 1.0.0
description: |
  Atmosphere AI Console — the Vue SPA shipped at `/atmosphere/console/` by
  `atmosphere-spring-boot-starter` and `atmosphere-quarkus-starter`. Used by
  every Spring Boot / Quarkus sample that exposes a chat-style endpoint
  (`@AiEndpoint`, `@Broadcaster`, `@Channel`, …). Stable selectors:
  `[data-testid=status-label]`, `[data-testid=chat-input]`,
  `[data-testid=chat-send]`, `[data-testid=message-bubble]`,
  `[data-testid=tool-activity]`.
requires:
  vars:
    - name: PORT
      description: TCP port the booted sample binds to.
      required: true
    - name: MESSAGE
      description: User prompt to send through the chat input.
      default: "Hello — one short sentence please."
    - name: ASSISTANT_TIMEOUT_MS
      description: How long to wait for the streamed assistant bubble.
      default: "30000"
  env:
    - name: ATMOSPHERE_AUTH_ENABLED
      default: "false"
      description: Console does not thread an auth token; auth-enabled returns 401.
provides:
  flows:
    - chat-stream
    - chat-broadcast
    - chat-tool-call
compatible_with:
  atmosphere: ">=4.0.0,<5.0.0"
  spring-boot: ">=3.2.0"
  quarkus: ">=3.13.0"
```

# Atmosphere AI Console — Archetype

This archetype captures the **canonical Vue console** shared across 21+
Atmosphere samples. Use it for any sample whose UI is the bundled console
served from `<base>/atmosphere/console/`.

## Selectors (stable)

| Selector | Purpose |
|----------|---------|
| `[data-testid=status-label]` | Connection-status pill. Text begins with `"Connected"` when ready. |
| `[data-testid=chat-input]` | Multiline textarea for prompt entry. Placeholder: `"Type a message..."`. |
| `[data-testid=chat-send]` | Send button. Disabled while input is empty. |
| `[data-testid=message-bubble]` | One per message; class `.message--user` vs `.message--assistant` disambiguates. |
| `[data-testid=tool-activity]` | Tool-call panel (present when archetype is exercised with `chat-tool-call`). |
| `[data-testid=console-tabs]` | Top navigation (Chat / Sessions / Policies / Decisions / Commitments / OWASP). |

## Instance contract

The plan entry that extends this archetype declares:

```yaml
- name: <sample-name>
  archetypes: [mirroir-skills/atmosphere/ai-console@v1]
  flows: [chat-stream]                 # subset of {chat-stream, chat-broadcast, chat-tool-call}
  vars:
    PORT: "8080"                       # required
    MESSAGE: "Custom prompt"           # optional; defaults to a generic greeting
  boot:
    command: "<mvnw / quarkus:dev>"
    cwd: "${ATMOSPHERE_HOME:-.}"
    env:
      LLM_MODE: fake                   # required for chat-stream / chat-tool-call
      ATMOSPHERE_AUTH_ENABLED: "false"
    boot_ready_port: 8080
    boot_ready_timeout_s: 120
```

`LLM_MODE=fake` routes through `FakeLlmClient` for deterministic streaming
with no API keys. Use `remote` only when the boot env supplies a key.

## Flows

- **chat-stream** — Open console → wait for `Connected` → type prompt →
  send → wait for an `.message--assistant` bubble. Pass condition:
  exactly one assistant bubble appears.
- **chat-broadcast** — Open console → wait for `Connected` → assert a
  pre-existing broadcast bubble OR send a prompt and observe broadcast
  fan-out. Used by samples that exercise `@Broadcaster`.
- **chat-tool-call** — Send a tool-triggering prompt → assert a
  `[data-testid=tool-activity]` panel renders → wait for an assistant
  bubble. For samples exercising `@AiTool`.
