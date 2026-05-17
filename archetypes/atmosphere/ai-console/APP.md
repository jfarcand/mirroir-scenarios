```yaml
version: 1
app: atmosphere/ai-console
archetype: chat-streaming
runtime: spring-boot-4 | quarkus-3 + atmosphere-ai
surface: web
url_root: http://127.0.0.1:${PORT}/atmosphere/console/
obstacle_mode: auto
```

# Atmosphere AI Console — App Structure

The single Vue SPA served at `/atmosphere/console/` by every Atmosphere
sample using `@AiEndpoint`, `@Broadcaster`, or `@Channel`. Selectors below
are **stable across the entire Atmosphere sample matrix** as of
Atmosphere 4.x — they're guaranteed by `atmosphere-spring-boot-starter`
and `atmosphere-quarkus-starter`.

## Boot prerequisites

- JVM: JDK 21
- Boot ready: TCP `${PORT}` accepting connections **AND**
  `GET /atmosphere/console/` returns 200.
- `LLM_MODE=fake` for chat-stream / chat-tool-call (deterministic
  streaming, no API keys).
- `ATMOSPHERE_AUTH_ENABLED=false` (Vue console does not thread auth).

## Structure

`/` 302-redirects to `/atmosphere/console/`. Single header,
six navigation tabs, one main pane.

### Header (banner)
- "Atmosphere" wordmark image (SVG)
- Heading: "Atmosphere AI Console"
- Subtitle from `application.yml → atmosphere.console-subtitle`
- Build-version chip (e.g., "v4")

### Navigation tabs (`[data-testid=console-tabs]`)
1. **Chat** — default tab on load. The chat UI lives here.
2. **Sessions** — active Atmosphere sessions.
3. **Policies** — governance policies (count badge when any).
4. **Decisions** — governance decisions log.
5. **Commitments** — governance commitments.
6. **OWASP** — OWASP detector findings.

### Chat tab (default)

| Element | Selector | Notes |
|---------|----------|-------|
| Status pill | `[data-testid=status-label]` | Text: `"<state> · <transport>"` — e.g. `"Connected · websocket"`. Match `Connected` prefix only; transport varies. |
| Clear button | `button:has-text('Clear')` | No `data-testid`. |
| Welcome panel | text `"Start a conversation"` | Hidden after first message. |
| Input | `[data-testid=chat-input]` | Multiline `<textarea>`. Placeholder: `"Type a message..."`. |
| Send | `[data-testid=chat-send]` | Disabled until input is non-empty. |
| Message bubble | `[data-testid=message-bubble]` | One per message. Classes: `.message--user`, `.message--assistant`. |
| Tool-activity panel | `[data-testid=tool-activity]` | Present when sample wires `@AiTool` (see `chat-tool-call` flow). |
| Approval prompt | `[data-testid=approval-prompt]` | Governance-gated samples (rare). |

## Invariants

- Status label prefix matches `"Connected"` when ready.
- Send button is disabled when input is empty.
- Message bubbles render in order: user before assistant.
- Strict-mode locators on `[data-testid=message-bubble]` must scope by
  `.message--user` or `.message--assistant` to avoid matching both.
- Markdown bodies are rendered inside assistant bubbles (`<p>`, `<code>`,
  `<pre>` elements appear inline).

## Transport negotiation

`atmosphere.js` negotiates transport per browser:

- Chromium: WebTransport over HTTP/3 if cert hash is offered, else WebSocket.
- Firefox + WebKit: WebSocket primary; SSE / long-poll fallback when
  WebSocket is blocked.

The `[data-testid=status-label]` `"Connected"` prefix check is
transport-agnostic — never assert on the transport tail.

## Known obstacles

- `ATMOSPHERE_AUTH_ENABLED=true` (the default in `application.yml`):
  console hangs at `"Connecting"` or flips to `"Disconnected"` because no
  bearer token is threaded.
- `LLM_MODE=demo` (typo): not in the `AiConfig.configure` switch; falls
  through to `remote` with no key → assistant bubble never appears.
- `:${PORT}` already bound: boot fails with `Address already in use` —
  override `PORT` per-instance or kill the prior process.
