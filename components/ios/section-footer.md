---
version: 1
name: section-footer
platform: ios
---

# Section Footer

## Description

Explanatory text below a group of rows, providing context about the section above.

## Visual Pattern

- Small text below a group of rows
- Often multiple lines

## Match Rules

- min_elements: 1
- max_elements: 3
- max_row_height_pt: 80
- zone: content

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 50
- absorb_condition: info_or_decoration_only
