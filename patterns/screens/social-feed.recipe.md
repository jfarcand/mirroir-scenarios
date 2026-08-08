---
version: 1
name: social-feed
platform: ios
---

# Social Feed

## Description

Infinite-scroll feed of user-generated content. Found in TikTok, Instagram,
Reddit, Twitter/X, Facebook. Content scrolls indefinitely — exploration must
prioritize tab-based navigation over scrolling through posts.

## Required Components

- feed-post

## Supporting Components

- tab-bar-item
- action-bar
- profile-header
- compose-bar
- search-bar

## Forbidden Components

- table-row-disclosure
- summary-card
- toggle-row

## Navigation Model

- type: infinite-scroll
- backtrack: tap-tab
- scroll_behavior: infinite
- depth_pattern: flat
- calibration_scroll_limit: 2

## Exploration Hints

- Do NOT scroll through feed posts — they are infinite
- Navigate via tabs to discover app structure (Profile, Search, Notifications)
- Profile screens contain the richest navigation structure
- Search/Discover tabs reveal content categories
- Action bars on posts are engagement tools, not navigation
- Limit scroll to 2-3 pages maximum before switching tabs
