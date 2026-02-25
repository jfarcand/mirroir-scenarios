---
version: 1
name: table-row-detail
platform: ios
---

# Table Row with Detail

## Description

Table row with label and value but no chevron, indicating non-navigable detail.

## Visual Pattern

- Label on the left
- Value or detail text on the right
- No chevron indicator

## Match Rules

- row_has_chevron: false
- min_elements: 1
- max_elements: 4
- max_row_height_pt: 90
- zone: content

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
