# NFC Time Tracker

A lightweight Home Assistant integration for tracking time by project using NFC tags.

It listens for NFC tag events, starts a timer when a tag is detected, and stops it when the tag is removed. The integration stores the project/tag mapping and exposes live time tracking data in Home Assistant.

## What it does

- Track working time for different projects
- Link NFC tags to a project
- Start and stop sessions automatically
- Show current project, active session duration, and total time today
- Keep project and session data stored locally

## Typical setup

1. Add a project in Home Assistant
2. Assign an NFC tag to that project
3. Use an ESPHome or similar automation to emit NFC tag present/removed events
4. The integration starts a session when the tag is seen and ends it when the tag is removed

## Installation

1. Copy this repository into your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Add the integration from the UI

## Included sensors

- Current project
- Current session duration
- Total time today
- Current tag
- Project list

## Notes

This is a simple, local-only time tracking solution intended for Home Assistant users who want to track work sessions with NFC cards or tags.
