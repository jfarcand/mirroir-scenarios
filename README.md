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
  - tap: "${RECIPIENT}"
  - tap: "Message"
  - type: "${MESSAGE:-Hey, just checking in!}"
  - press_key: "return"
  - screenshot: "message_sent"
```

## Installation

### Claude Code

```bash
claude plugin marketplace add jfarcand/iphone-mirroir-scenarios
claude plugin install scenarios@iphone-mirroir-scenarios
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add jfarcand/iphone-mirroir-scenarios
copilot plugin install scenarios@iphone-mirroir-scenarios
```

Both install the [SKILL.md](plugins/scenarios/skills/scenarios/SKILL.md) which teaches the AI how to interpret and execute scenario steps.

### Manual (all other clients)

Clone into your global scenarios directory:

```bash
git clone https://github.com/jfarcand/iphone-mirroir-scenarios ~/.iphone-mirroir-mcp/scenarios
```

Or into a project-local directory:

```bash
git clone https://github.com/jfarcand/iphone-mirroir-scenarios .iphone-mirroir-mcp/scenarios
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

### Workflows

| Scenario | Description |
|----------|-------------|
| `workflows/commute-eta-notify` | Get ETA from Waze, send it to your boss via Messages |
| `workflows/standup-autoposter` | Read today's meetings from Calendar, post standup to Slack |
| `workflows/qa-smoke-pack` | Smoke test a mobile app via Expo Go with screenshots at each checkpoint |
| `workflows/email-triage` | Check inbox for unread email — archive or flag based on content |
| `workflows/batch-archive` | Archive all unread emails in a loop until inbox is empty |

Workflows demonstrate **cross-app data extraction** — the AI reads dynamic content from one app and composes it into actions in another. This is something only an AI executor can do.

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

## Conditions

Scenarios support branching with `condition` steps. The AI checks the screen and executes the matching branch:

```yaml
steps:
  - launch: "Mail"
  - wait_for: "Inbox"
  - condition:
      if_visible: "Unread"
      then:
        - tap: "Unread"
        - tap: "Archive"
        - assert_visible: "Archived"
      else:
        - screenshot: "empty_inbox"
```

A condition step has:
- **`if_visible`** or **`if_not_visible`** — the label to check on screen
- **`then`** (required) — steps to run when the condition is true
- **`else`** (optional) — steps to run when the condition is false

Steps inside branches are regular steps, including nested conditions. See `workflows/email-triage.yaml` for a full example.

## Repeats

Scenarios support loops with `repeat` steps. The AI checks a screen condition before each iteration:

```yaml
steps:
  - launch: "Mail"
  - wait_for: "Inbox"
  - repeat:
      while_visible: "Unread"
      max: 10
      steps:
        - tap: "Unread"
        - tap: "Archive"
        - tap: "< Back"
        - wait_for: "Inbox"
```

A repeat step has:
- **Loop mode** (exactly one): `while_visible`, `until_visible`, or `times`
- **`max`** (required) — safety bound to prevent infinite loops
- **`steps`** (required) — steps to run each iteration

See `workflows/batch-archive.yaml` for a full example.

## Validation

Run the validation script to check all scenarios for required fields, valid step types, and correct variable syntax:

```bash
python3 scripts/validate-scenarios.py
```

This runs automatically on push and PR via GitHub Actions.

## Contributing

Contributions are welcome! By submitting a pull request or patch, you agree to the [Contributor License Agreement](CLA.md). Your Git commit metadata (name and email) serves as your electronic signature — no separate form to sign.

The CLA ensures the project can be maintained long-term under a consistent license. You retain full ownership of your contributions — the CLA simply grants the maintainer the right to distribute them as part of the project.

### How to contribute

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
   ios_min: "17.0"
   locale: "en_US"
   tags: ["app-name", "category", "action-type"]

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

Apache 2.0 — see [LICENSE](LICENSE). See [CLA](CLA.md) for contributor terms.
