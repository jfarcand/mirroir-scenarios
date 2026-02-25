---
version: 1
name: navigation-bar
platform: ios
---

# Navigation Bar

## Description

Nav bar at the top of the screen with back button, title, and optional action buttons.
The back chevron and action buttons are clickable navigation targets.

## Visual Pattern

- Back chevron (<, ‹) or label on the left
- Title centered or left-aligned
- Optional action buttons on the right (Edit, Done, +)
- Located in the top ~10% of screen

## Match Rules

- row_has_chevron: false
- min_elements: 1
- max_elements: 4
- max_row_height_pt: 50
- zone: nav_bar

## Interaction

- clickable: true
- click_target: first_navigation_element
- click_result: navigates
- back_after_click: true

## Grouping

- absorbs_same_row: true
- absorbs_below_within_pt: 0
- absorb_condition: any
