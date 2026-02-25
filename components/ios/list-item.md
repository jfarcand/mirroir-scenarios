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
- min_elements: 1
- max_elements: 2
- max_row_height_pt: 90
- zone: content

## Interaction

- clickable: true
- click_target: first_navigation_element
- click_result: navigates
- back_after_click: true

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
