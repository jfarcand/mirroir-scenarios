---
name: iphone-mirroir-scenarios
description: Community scenarios for iPhone Mirroring MCP. Provides ready-made YAML scenarios for automating iOS apps via AI-driven screen interaction.
---

# iPhone Mirroring Scenarios

This skill provides community-contributed YAML scenarios for [iphone-mirroir-mcp](https://github.com/jfarcand/iphone-mirroir-mcp), the MCP server that gives AI agents control of a real iPhone screen.

## How Scenarios Work

Scenarios are YAML files that describe multi-step iOS automation flows as **intents**, not scripts. Steps like `tap: "Email"` don't specify coordinates — you (the AI) find the element using `describe_screen` and adapt to the actual screen layout.

## Executing a Scenario

1. Use `list_scenarios` to discover available scenarios
2. Use `get_scenario` with the scenario name to load it (e.g. `get_scenario("apps/slack/send-message")`)
3. Read the YAML steps and execute each one using the appropriate MCP tools

## Step Type Reference

| Step | How to Execute |
|------|----------------|
| `launch: "App"` | Call `launch_app` |
| `tap: "Label"` | Call `describe_screen` to find the element, then `tap` at its coordinates |
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

## Variable Substitution

`${VAR}` placeholders are resolved from environment variables by `get_scenario`. `${VAR:-default}` provides a fallback. If you see unresolved `${VAR}` in the loaded scenario, ask the user for the value before proceeding.

## Adapting to Reality

Real iOS screens differ from what scenarios expect. You should:

- **Dismiss unexpected dialogs** (permission prompts, update banners, cookie consent)
- **Scroll to find off-screen elements** when `describe_screen` doesn't show the target
- **Handle localized UI** (the phone may be in French, Spanish, etc.)
- **Retry failed taps** — OCR coordinates may be slightly off, try nearby positions
- **Report assertion failures clearly** with what was expected vs. what was actually on screen
