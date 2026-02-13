# iphone-mirroir-scenarios

Community-contributed YAML scenarios for [iphone-mirroir-mcp](https://github.com/jfarcand/iphone-mirroir-mcp) — AI-driven automation flows for real iOS devices.

## What Are Scenarios?

Scenarios are YAML files that describe multi-step iOS automation as **intents**, not scripts. Steps like `tap: "Email"` don't hardcode coordinates — the AI finds elements via OCR and adapts to screen layout, localization, and unexpected dialogs.

```yaml
name: Send Slack Message
app: Slack
description: Send a direct message to a contact in Slack

steps:
  - launch: "Slack"
  - wait_for: "Home"
  - tap: "Direct Messages"
  - tap: "${RECIPIENT:-Phil Tremblay}"
  - tap: "Message"
  - type: "${MESSAGE:-Hey, just checking in!}"
  - press_key: "return"
  - screenshot: "message_sent"
```

## Installation

### Claude Code Plugin (recommended)

```bash
/plugin marketplace add jfarcand/iphone-mirroir-scenarios
```

### Manual

Clone into your global scenarios directory:

```bash
git clone https://github.com/jfarcand/iphone-mirroir-scenarios ~/.iphone-mirroir-mcp/scenarios/community
```

Or into a project-local directory:

```bash
git clone https://github.com/jfarcand/iphone-mirroir-scenarios .iphone-mirroir-mcp/scenarios/community
```

Both paths are scanned recursively by `list_scenarios`.

## Available Scenarios

### Apps

| Scenario | Description |
|----------|-------------|
| `apps/calendar/create-event` | Create a new calendar event |
| `apps/calendar/check-today` | View today's schedule |
| `apps/clock/set-alarm` | Create a new alarm |
| `apps/clock/set-timer` | Start a countdown timer |
| `apps/settings/check-about` | Navigate to Settings > About |
| `apps/slack/send-message` | Send a DM to a contact |
| `apps/slack/check-unread` | Check Slack activity feed |
| `apps/weather/check-forecast` | View current weather and 10-day forecast |
| `apps/weather/add-city` | Add a city to Weather |

### Testing

| Scenario | Description |
|----------|-------------|
| `testing/expo-go/login-flow` | Test login screen with credentials |
| `testing/expo-go/shake-debug-menu` | Open React Native debug menu via shake |

## Variable Substitution

Scenarios use `${VAR}` placeholders resolved from environment variables. Use `${VAR:-default}` for fallback values.

```bash
# Set credentials for testing scenarios
export TEST_EMAIL=user@example.com
export TEST_PASSWORD=secret

# Or use direnv
echo 'export TEST_EMAIL=user@example.com' >> .envrc
direnv allow
```

Unresolved variables without defaults are left as-is — the AI will ask for values before proceeding.

## Contributing

1. Fork this repository
2. Create your scenario in the appropriate directory:
   - `apps/<app-name>/` for iOS app automation
   - `testing/<framework>/` for mobile testing frameworks
   - `workflows/` for multi-app sequences
3. Follow the YAML format:
   ```yaml
   name: Human-readable name
   app: App Name
   description: What this scenario does
   ios_min: "17.0"  # optional

   steps:
     - launch: "App Name"
     - wait_for: "Expected Element"
     - tap: "Element Label"
     - type: "${VAR:-sensible default}"
     - assert_visible: "Success Indicator"
     - screenshot: "result"
   ```
4. Use `${VAR:-default}` for configurable values, never hardcode credentials
5. Include at least one `assert_visible` step so the scenario is self-verifying
6. Submit a pull request

## License

Apache 2.0 — see [LICENSE](LICENSE).
