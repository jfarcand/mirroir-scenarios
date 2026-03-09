---
version: 1
name: list-item
platform: ios
---

# List Item

## Description

Simple list item without chevron that may still be tappable.

## Visual Pattern

- Single label
- No chevron
- In a list context

## Match Rules

- row_has_chevron: false
- has_numeric_value: false
- min_elements: 1
- max_elements: 1
- max_row_height_pt: 90
- zone: content
- min_confidence: 0.60
- exclude_numeric_only: true

## Interaction

- clickable: true
- click_target: first_navigation_element
- click_result: pushes_screen
- back_after_click: true

## Exploration

- explorable: true
- role: depth_navigation
- priority: low

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
