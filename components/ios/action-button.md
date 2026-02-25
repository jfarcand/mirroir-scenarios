---
version: 1
name: action-button
platform: ios
---

# Action Button

## Description

Standalone button for triggering an action.

## Visual Pattern

- Centered text
- Button styling or distinct color

## Match Rules

- min_elements: 1
- max_elements: 1
- max_row_height_pt: 60
- zone: content

## Interaction

- clickable: true
- click_target: centered_element
- click_result: navigates
- back_after_click: true

## Grouping

- absorbs_same_row: false
- absorbs_below_within_pt: 0
- absorb_condition: any
