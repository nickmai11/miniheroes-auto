#!/bin/bash
# Done indicator (Nick 2026-11-20, every task): an account finished the task Nick named with nothing left ->
# its instance goes to the Android home screen (visible in the tiled windows) + one Glass sound.
# Only when clean (no SKIP-for-a-problem / FAIL / MANUAL left); Kong's instance only after Kong II too. Never from a mission script.
# usage: scripts/done.sh <adb serial>...
for s in "$@"; do adb -s "$s" shell input keyevent KEYCODE_HOME; done
afplay /System/Library/Sounds/Glass.aiff &
