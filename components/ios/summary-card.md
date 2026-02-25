---
version: 1
name: summary-card
platform: ios
---

# Summary Card

## Description

Card showing a metric with title, large numeric value, and optional chevron.
Common in Health, Fitness, and dashboard-style apps.

## Visual Pattern

- Title text on first line
- Large numeric value on second line
- Unit or description near the value
- Optional chevron for navigation

## Match Rules

- min_elements: 2
- max_elements: 6
- max_row_height_pt: 120
- has_numeric_value: true
- zone: content

## Interaction

- clickable: true
- click_target: first_navigation_element
- click_result: navigates
- back_after_click: true

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 50
- absorb_condition: info_or_decoration_only
