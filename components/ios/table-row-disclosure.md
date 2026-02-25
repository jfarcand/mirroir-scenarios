---
version: 1
name: table-row-disclosure
platform: ios
---

# Table Row with Disclosure Indicator

## Description

Standard UITableViewCell with a disclosure indicator (chevron >). The most common
navigation element in iOS settings-style apps.

## Visual Pattern

- One or two text labels aligned left
- Optional detail text or value aligned right
- Chevron character (>, ›) at the far right edge
- Full-width horizontal row, 44-88pt typical height

## Match Rules

- row_has_chevron: true
- min_elements: 1
- max_elements: 4
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
