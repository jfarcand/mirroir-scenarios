```yaml
version: 1
name: atmosphere/ai-console
archetype_version: 1.0.0
surface: web
tags: ["atmosphere", "ai-console", "must-pass"]
flows:
  - chat-stream
  - chat-broadcast
  - chat-tool-call
inputs:
  PORT: "8080"
  MESSAGE: "Hello — one short sentence please."
```

# Atmosphere AI Console — Skill prompts

The flows below are LLM-followable. Each is also emitted as a mirroir-run
scenario YAML under `scenarios/<flow>.yaml`. The two stay in sync.

## chat-stream

Single-turn AI chat against the bundled Vue console. The canonical
happy-path for any `@AiEndpoint`-bearing Spring Boot / Quarkus sample.

### Steps

1. Open `http://127.0.0.1:${PORT}/atmosphere/console/`.
2. Wait for `[data-testid=status-label]` text to begin with `"Connected"`
   (the full label appends a transport tail).
3. Tap `[data-testid=chat-input]` to focus.
4. Type `${MESSAGE}`.
5. Tap `[data-testid=chat-send]`. (Button is disabled until input is
   non-empty; do not race the click ahead of the keystroke.)
6. Wait for `[data-testid=message-bubble].message--assistant` to be
   visible (up to `${ASSISTANT_TIMEOUT_MS}` milliseconds).
7. Assert exactly one user bubble + at least one assistant bubble.

## chat-broadcast

Used by `@Broadcaster` samples — broadcast a chat message to one or more
attached subscribers. For single-browser replay we assert the local
bubble; cross-browser broadcast verification is a future flow extension.

### Steps

1. Open `http://127.0.0.1:${PORT}/atmosphere/console/`.
2. Wait for `[data-testid=status-label]` to be `"Connected"`.
3. Type `${MESSAGE}` into `[data-testid=chat-input]`; send.
4. Wait for `[data-testid=message-bubble].message--user` to render.
5. Wait for `[data-testid=message-bubble].message--assistant` (echo or
   broadcast response).

## chat-tool-call

Sample exercises `@AiTool` — assistant invokes a tool before producing
the response. Distinguishing assertion: a
`[data-testid=tool-activity]` panel renders.

### Steps

1. Open `http://127.0.0.1:${PORT}/atmosphere/console/`.
2. Wait for `[data-testid=status-label]` to be `"Connected"`.
3. Type a tool-triggering prompt (sample-specific; instance may override
   via `MESSAGE`).
4. Tap `[data-testid=chat-send]`.
5. Wait for `[data-testid=tool-activity]` to be visible.
6. Wait for `[data-testid=message-bubble].message--assistant`.

## Cross-browser

All three flows run on chromium + firefox + webkit. The Connected prefix
match is transport-agnostic; transport negotiation is described in the
archetype's `APP.md`.

## Skip / obstacles

- `ATMOSPHERE_AUTH_ENABLED=true` (default in sample `application.yml`):
  step 2 never succeeds. Override in `boot.env`.
- `LLM_MODE` unset or invalid for chat-stream / chat-tool-call: step 6
  hangs. Set to `fake` for replay.
