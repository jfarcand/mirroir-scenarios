---
version: 1
name: bottom-navigation-bar
platform: ios
---

# Bottom Navigation Bar

## Description

Groups all bottom tab bar labels into a single non-clickable component.
Prevents each tab label from becoming an individual fallback navigation element
that BFS would waste actions tapping. Tab switching is handled by the BFS
frontier system, not by element tapping.

## Visual Pattern

- Multiple short labels in a single row
- Bottom 12% of screen (tab_bar zone)
- Evenly spaced horizontally across the width
- Typically 2-5 tab labels

## Match Rules

- min_elements: 2
- max_elements: 10
- max_row_height_pt: 60
- zone: tab_bar

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
