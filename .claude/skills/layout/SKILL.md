---
name: layout
description: Resize and move Nick's running MuMuPlayer instance windows - each half the screen height, packed in 2 rows at the left of the main screen; instances listed in accounts/layout.yaml (now Cmajor) are left alone.
---

# MuMu window layout

1. In `~/projects/chidojiro/miniheroes-auto`, run `osascript -l JavaScript scripts/layout.js`.
   It prints `<name>: <x,y> <w,h>` per moved window.
2. To change which instances stay put, edit `exclude:` in `accounts/layout.yaml` (MuMu instance names).
3. If it fails with "not allowed assistive access", ask Nick to allow his terminal app in
   System Settings > Privacy & Security > Accessibility.

Only running instances are moved; start them first (`scripts/boot.sh`) if needed.
