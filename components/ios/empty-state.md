---
version: 1
name: empty-state
platform: ios
---

# Empty State

## Description

Empty screen with centered text and optional call-to-action button.

## Visual Pattern

- Centered text
- Possibly an icon above
- Optional button below

## Match Rules

- min_elements: 1
- max_elements: 4
- max_row_height_pt: 200
- zone: content

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 40
- absorb_condition: any
