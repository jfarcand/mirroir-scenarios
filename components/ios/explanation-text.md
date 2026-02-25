---
version: 1
name: explanation-text
platform: ios
---

# Explanation Text

## Description

Informational paragraph that is not an interactive element.

## Visual Pattern

- Long text spanning most of the screen width
- Sentence-like content

## Match Rules

- row_has_chevron: false
- min_elements: 1
- max_elements: 3
- max_row_height_pt: 100
- has_long_text: true
- zone: content

## Interaction

- clickable: false
- click_target: none
- click_result: none
- back_after_click: false

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 30
- absorb_condition: info_or_decoration_only
