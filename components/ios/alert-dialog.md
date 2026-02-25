---
version: 1
name: alert-dialog
platform: ios
---

# Alert Dialog

## Description

Modal alert dialog with dismiss/confirm buttons.

## Visual Pattern

- Overlay on screen
- OK/Cancel/Allow/Deny buttons

## Match Rules

- min_elements: 1
- max_elements: 4
- max_row_height_pt: 200
- zone: content

## Interaction

- clickable: true
- click_target: centered_element
- click_result: dismisses
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 20
- absorb_condition: any
