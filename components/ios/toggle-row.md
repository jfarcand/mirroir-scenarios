---
version: 1
name: toggle-row
platform: ios
---

# Toggle Row

## Description

Row with a switch/toggle control that should be skipped during exploration.

## Visual Pattern

- Label on the left
- On/Off indicator on the right

## Match Rules

- row_has_chevron: false
- has_numeric_value: false
- min_elements: 1
- max_elements: 3
- max_row_height_pt: 90
- zone: content

## Interaction

- clickable: true
- click_target: first_text
- click_result: mutates_in_place
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
