---
name: mirroir-skills
description: Community skills for iPhone Mirroring MCP. Provides ready-made skills (SKILL.md and YAML) for automating iOS apps via AI-driven screen interaction.
---

# iPhone Mirroring Skills

This skill provides community-contributed skills for [mirroir-mcp](https://github.com/jfarcand/mirroir-mcp), the MCP server that gives AI agents control of a real iPhone screen.

Skills come in two formats:
- **SKILL.md** (`.md`) — natural-language markdown with YAML front matter, the primary format for AI execution
- **YAML** (`.yaml`) — structured step definitions in `legacy/`, used by the deterministic `mirroir test` and `mirroir compile` CLI tools

## How Skills Work

Skills describe multi-step iOS automation flows as **intents**, not scripts. Steps like "Tap Email" don't specify coordinates — you (the AI) find the element using `describe_screen` and adapt to the actual screen layout.

## Executing a Skill

1. Use `list_skills` to discover available skills
2. Use `get_skill` with the skill name to load it (e.g. `get_skill("apps/slack/send-message")`)
3. Read the steps and execute each one using the appropriate MCP tools

## Step Type Reference

| Step | How to Execute |
|------|----------------|
| `launch: "App"` | Call `launch_app` |
| `tap: "Label"` | Call `describe_screen` to find the element, then `tap` at its coordinates |
| `long_press: "Label"` | Call `describe_screen` to find the element, then `long_press` at its coordinates |
| `type: "text"` | Call `type_text` |
| `swipe: "up"` | Call `swipe` with appropriate coordinates based on screen size |
| `wait_for: "Label"` | Poll `describe_screen` until the element appears (retry with short delays) |
| `assert_visible: "Label"` | Call `describe_screen` and verify the label is present. Report failure if not found. |
| `assert_not_visible: "Label"` | Call `describe_screen` and verify the label is absent. Report failure if found. |
| `screenshot: "label"` | Call `screenshot` and label it in your response |
| `press_key: "return"` | Call `press_key` |
| `press_home: true` | Call `press_home` to return to the home screen |
| `open_url: "https://..."` | Call `open_url` |
| `shake: true` | Call `shake` |
| `remember: "instruction"` | Read dynamic data from the screen and hold it in memory. Use `{NAME}` (single braces) in later steps to insert the remembered value. |
| `condition:` | Branch based on screen state. See **Conditions** below. |
| `repeat:` | Loop over steps until a screen condition is met. See **Repeats** below. |

## Conditions

Skills can branch using `condition` steps. Call `describe_screen` to evaluate the condition, then execute the matching branch.

```yaml
- condition:
    if_visible: "Label"      # or if_not_visible: "Label"
    then:
      - tap: "Label"
      - screenshot: "found"
    else:                     # optional
      - screenshot: "not_found"
```

**How to execute:**

1. Call `describe_screen` and check whether the label from `if_visible` (or `if_not_visible`) is present
2. If the condition is **true**, execute the `then` steps sequentially
3. If the condition is **false** and `else` is provided, execute the `else` steps
4. If the condition is **false** and there is no `else`, skip and continue to the next step

Steps inside `then` and `else` are regular steps — including nested `condition` steps if needed. Avoid nesting deeper than 2-3 levels to keep skills readable.

## Repeats

Skills can loop using `repeat` steps. The AI checks a screen condition before each iteration and stops when the condition fails or `max` iterations are reached.

```yaml
- repeat:
    while_visible: "Unread"     # keep going while element is on screen
    max: 10                      # required safety bound
    steps:
      - tap: "Unread"
      - tap: "Archive"
      - tap: "< Back"
```

**Loop modes** (use exactly one):
- `while_visible: "Label"` — continue while the label is on screen
- `until_visible: "Label"` — continue until the label appears
- `times: N` — repeat exactly N times (no screen check)

**How to execute:**

1. Before each iteration, call `describe_screen` and evaluate the loop condition (`while_visible` or `until_visible`). For `times`, just count.
2. If the condition allows another iteration **and** `max` is not reached, execute the `steps` sequentially
3. After the steps complete, go back to step 1
4. When the condition fails or `max` is reached, stop and continue to the next step after the repeat

Steps inside `repeat` are regular steps — including `condition` and nested `repeat` if needed.

## Skill Metadata

Skills include metadata in the YAML front matter (for `.md` files) or as top-level keys (for `.yaml` files):

| Field | Purpose |
|-------|---------|
| `version` | Format version (currently `1`). Required in `.md` files. |
| `name` | Human-readable skill name. |
| `app` | Target iOS app name. |
| `ios_min` | Minimum iOS version (e.g. `"17.0"`). Skip the skill if the device is below this version. |
| `locale` | Expected locale (e.g. `"en_US"`, `"fr_CA"`). Adapt UI labels if the phone's locale differs. |
| `tags` | List of strings for discovery (e.g. `["calendar", "create"]`). Used for filtering, not execution. |

## Variable Substitution

`${VAR}` placeholders are resolved from environment variables by `get_skill`. `${VAR:-default}` provides a fallback. If you see unresolved `${VAR}` in the loaded skill, ask the user for the value before proceeding.

## Auto-Compilation

When you execute a skill, `get_skill` appends a compilation status line at the end of the response. Use it to decide whether to compile:

- **`[Not compiled]`** — No compiled version exists. Follow the compilation steps below.
- **`[Compiled: stale — ...]`** — Source changed since last compile. Recompile using the steps below.
- **`[Compiled: fresh]`** — Up to date. Skip compilation (no `record_step` calls needed).

### How to compile during execution

1. After each step, call `record_step` with the step index, type, label, and any data you observed:
   - For **tap** steps: include `tap_x`, `tap_y`, `confidence` from `describe_screen`
   - For **wait_for** / **assert** steps: include `elapsed_ms` (approximate time waited)
   - For **scroll_to** steps: include `scroll_count` and `scroll_direction`
   - For **launch**, **type**, **press_key**, **swipe**, **home**, **open_url**, **shake**, **reset_app**, **set_network**, **screenshot**, **switch_target**: just index, type, and label
   - For **remember**, **condition**, **repeat** (AI-only steps): just index, type, and label (hints will be null)
2. After all steps complete successfully, call `save_compiled` with the skill name

The compiled file (`.compiled.json`) enables `mirroir test` to replay the skill deterministically without OCR. Your first execution IS the compilation — no separate learning run needed.

## Adapting to Reality

Real iOS screens differ from what skills expect. You should:

- **Dismiss unexpected dialogs** (permission prompts, update banners, cookie consent)
- **Scroll to find off-screen elements** when `describe_screen` doesn't show the target
- **Handle localized UI** (the phone may be in French, Spanish, etc.)
- **Retry failed taps** — OCR coordinates may be slightly off, try nearby positions
- **Report assertion failures clearly** with what was expected vs. what was actually on screen
