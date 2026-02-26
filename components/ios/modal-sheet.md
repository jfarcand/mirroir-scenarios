---
version: 1
name: modal-sheet
platform: ios
---

# Modal Sheet

## Description

iOS modal sheet presented from the bottom with a title and dismiss button (X).
Common for share sheets, detail views, and pickers. The dismiss button is always
the correct tap target to escape back to the previous screen.

## Visual Pattern

- Title text on the left or centered
- Dismiss button (X, ✕, ×) on the right side of the same row
- Located in the upper portion of the content zone
- Content below the header row (contacts, options, actions)

## Match Rules

- has_dismiss_button: true
- row_has_chevron: false
- min_elements: 2
- max_elements: 4
- max_row_height_pt: 60
- zone: content

## Interaction

- clickable: true
- click_target: first_dismiss_button
- click_result: dismisses
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
