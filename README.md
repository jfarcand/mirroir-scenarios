<p align="center">
  <img src="https://raw.githubusercontent.com/jfarcand/mirroir-mcp/main/website/public/mirroir-wordmark.svg" alt="mirroir-mcp" width="128" />
</p>

# mirroir-skills

Community marketplace of skills for [mirroir-mcp](https://github.com/jfarcand/mirroir-mcp) — AI-driven automation flows for real iOS devices.

## What Are Skills?

Skills describe multi-step iOS automation as **intents**, not scripts. Steps like "Tap Email" don't hardcode coordinates — the AI finds elements via OCR and adapts to screen layout, localization, and unexpected dialogs.

The primary format is **SKILL.md** — markdown files with YAML front matter:

```markdown
---
version: 1
name: Send Slack Message
app: Slack
tags: ["slack", "messaging"]
---

Send a direct message to a contact in Slack.

## Steps

1. Launch **Slack**
2. Wait for "Home" to appear
3. Tap "Direct Messages"
4. Tap "${RECIPIENT}"
5. Tap "Message"
6. Type "${MESSAGE:-Hey, just checking in!}"
7. Press **Return**
8. Screenshot: "message_sent"
```

<details>
<summary>Legacy YAML format (used by <code>mirroir test</code> and <code>mirroir compile</code>)</summary>

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

YAML files live in the `legacy/` directory. They are used by the deterministic `mirroir test` and `mirroir compile` CLI tools which require structured step definitions. Use `mirroir migrate` to convert YAML to SKILL.md format.

</details>

## Installation

### Claude Code

```bash
claude plugin marketplace add jfarcand/mirroir-skills
claude plugin install skills@mirroir-skills
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add jfarcand/mirroir-skills
copilot plugin install skills@mirroir-skills
```

Both install the [SKILL.md](.claude/skills/skills/SKILL.md) which teaches the AI how to interpret and execute skill steps.

### Manual (all other clients)

Clone into your global skills directory:

```bash
git clone https://github.com/jfarcand/mirroir-skills ~/.mirroir-mcp/skills
```

Or into a project-local directory:

```bash
git clone https://github.com/jfarcand/mirroir-skills .mirroir-mcp/skills
```

Both paths are scanned recursively by `list_skills`.

## Available Skills

### Apps

| Skill | Description |
|-------|-------------|
| `apps/appstore/install-app` | Search for an app in the App Store and install it |
| `apps/calendar/create-event` | Create a new calendar event |
| `apps/calendar/check-today` | Read today's events using `remember` to extract meeting details |
| `apps/clock/set-alarm` | Create a new alarm |
| `apps/clock/set-timer` | Start a countdown timer and verify it's running |
| `apps/mail/email-triage` | Check inbox for unread email — archive or flag based on content |
| `apps/mail/batch-archive` | Archive all unread emails in a loop until inbox is empty |
| `apps/maps/save-directions` | Search for a destination, get directions, extract travel time with `remember` |
| `apps/photos/share-recent` | Long-press a recent photo and share it via Messages |
| `apps/settings/check-about` | Extract device model, iOS version, and storage via `remember` |
| `apps/settings/check-about-fr` | Same as check-about but for French locale (Réglages) |
| `apps/settings/list-apps` | List installed apps with sizes from iPhone Storage |
| `apps/settings/uninstall-app` | Remove an app via Settings > General > iPhone Storage |
| `apps/slack/send-message` | Send a DM to a contact |
| `apps/slack/check-unread` | Read unread notifications with channel names and message previews |
| `apps/weather/check-forecast` | Extract current conditions and 10-day forecast with `remember` |
| `apps/weather/add-city` | Add a city to Weather |

### Testing

| Skill | Description |
|-------|-------------|
| `testing/expo-go/login-flow` | Test login with conditional branching for signup vs existing account |
| `testing/expo-go/shake-debug-menu` | Open React Native debug menu via shake |
| `testing/expo-go/qa-smoke-pack` | Visual regression test — screenshot key screens and use `remember` to detect UI anomalies |

### Workflows

| Skill | Description |
|-------|-------------|
| `workflows/morning-briefing` | Read weather + calendar, compose and send a morning summary via iMessage |
| `workflows/commute-eta-notify` | Get ETA from Waze, send it to your boss via Messages |
| `workflows/standup-autoposter` | Read today's meetings from Calendar, post standup to Slack |

Workflows demonstrate **cross-app data extraction** — the AI reads dynamic content from one app and composes it into actions in another. This is something only an AI executor can do.

## Variable Substitution

Skills use `${VAR}` placeholders resolved from environment variables. Use `${VAR:-default}` for fallback values.

```bash
# Set credentials for testing skills
export TEST_EMAIL=user@example.com
export TEST_PASSWORD=secret

# Or use direnv
echo 'export TEST_EMAIL=user@example.com' >> .envrc
direnv allow
```

Unresolved variables without defaults are left as-is — the AI will ask for values before proceeding.

## Conditions

Skills support branching with `condition` steps. The AI checks the screen and executes the matching branch:

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

Steps inside branches are regular steps, including nested conditions. See `apps/mail/email-triage.md` for a full example.

## Repeats

Skills support loops with `repeat` steps. The AI checks a screen condition before each iteration:

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

See `apps/mail/batch-archive.md` for a full example.

## Migration from YAML

The `mirroir migrate` command converts YAML skills to SKILL.md format:

```bash
mirroir migrate apps/settings/check-about.yaml           # single file
mirroir migrate --dir ../iphone-mirroir-skills/apps       # entire directory
mirroir migrate --dry-run apps/mail/email-triage.yaml     # preview without writing
```

Legacy YAML files live in the `legacy/` directory and remain accessible for the deterministic `mirroir test` and `mirroir compile` CLI tools.

## Validation

Run the validation script to check all skills for required fields, valid metadata, and correct variable syntax:

```bash
python3 scripts/validate-skills.py
```

This validates both SKILL.md files (in `apps/`, `testing/`, `workflows/`, `ci/`) and legacy YAML files (in `legacy/`). It runs automatically on push and PR via GitHub Actions.

## Contributing

Contributions are welcome! By submitting a pull request or patch, you agree to the [Contributor License Agreement](CLA.md). Your Git commit metadata (name and email) serves as your electronic signature — no separate form to sign.

The CLA ensures the project can be maintained long-term under a consistent license. You retain full ownership of your contributions — the CLA simply grants the maintainer the right to distribute them as part of the project.

### How to contribute

1. Fork this repository
2. Create your skill in the appropriate directory:
   - `apps/<app-name>/` for single-app iOS automation
   - `testing/<framework>/` for mobile testing and QA
   - `workflows/` for multi-app sequences that extract data across apps
3. Use the SKILL.md format:
   ```markdown
   ---
   version: 1
   name: Human-readable name
   app: App Name
   ios_min: "17.0"
   locale: "en_US"
   tags: ["app-name", "category", "action-type"]
   ---

   What this skill does.

   ## Steps

   1. Launch **App Name**
   2. Wait for "Expected Element" to appear
   3. Tap "Element Label"
   4. Type "${VAR:-sensible default}"
   5. Verify "Success Indicator" is visible
   6. Screenshot: "result"
   ```
4. Use `${VAR:-default}` for configurable values, never hardcode credentials
5. Include at least one "Verify" step so the skill is self-verifying
6. Submit a pull request

## License

Apache 2.0 — see [LICENSE](LICENSE). See [CLA](CLA.md) for contributor terms.
