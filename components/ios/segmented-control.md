---
version: 1
name: segmented-control
platform: ios
---

# Segmented Control

## Description

Tab-like selector with 2-4 short labels for switching content views.

## Visual Pattern

- 2-4 short labels in a row
- Evenly spaced
- One appears selected

## Match Rules

- min_elements: 2
- max_elements: 4
- max_row_height_pt: 50
- zone: content

## Interaction

- clickable: true
- click_target: centered_element
- click_result: navigates
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
