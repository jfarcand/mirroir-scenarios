---
version: 1
name: search-bar
platform: ios
---

# Search Bar

## Description

Search field, typically near the top of the screen.

## Visual Pattern

- Search placeholder text
- Magnifying glass icon

## Match Rules

- min_elements: 1
- max_elements: 2
- max_row_height_pt: 50
- zone: content

## Interaction

- clickable: true
- click_target: centered_element
- click_result: navigates
- back_after_click: true

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
