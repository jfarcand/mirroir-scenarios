---
version: 1
name: tab-bar-item
platform: ios
---

# Tab Bar Item

## Description

Tab bar button at the bottom of the screen for top-level navigation.
These are global navigation controls, not drill-down navigation.

## Visual Pattern

- Short label
- Bottom 12% of screen
- Evenly spaced horizontally
- Often paired with an icon character

## Match Rules

- min_elements: 1
- max_elements: 6
- max_row_height_pt: 60
- zone: tab_bar

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: false
- absorbs_below_within_pt: 0
- absorb_condition: any
