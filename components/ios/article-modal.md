---
version: 1
name: article-modal
platform: ios
---

# Article Modal

## Description

Full-screen modal presenting an informational article with a title bar and X dismiss
button. Common in Health/Santé (medication articles, health tips), App Store (app
descriptions), and other apps that present read-only content as a modal overlay.
The YOLO icon detector reports the X button as "icon" rather than text.

## Visual Pattern

- Title text centered or left-aligned in a header bar
- Dismiss icon (X) on the right side of the header, detected as "icon" by YOLO
- Large content area below with article text (paragraphs, images)
- No back chevron (modal, not push navigation)
- No tab bar visible (modal covers the underlying screen)

## Match Rules

- has_dismiss_button: true
- row_has_chevron: false
- min_elements: 2
- max_elements: 3
- max_row_height_pt: 60
- zone: content

## Interaction

- clickable: true
- click_target: first_dismiss_button
- click_result: dismisses
- back_after_click: false

## Exploration

- explorable: false
- role: info
- priority: normal

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
