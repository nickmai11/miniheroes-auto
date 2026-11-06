---
name: layout
description: Resize and move Nick's running MuMuPlayer instance windows - layout 1 (default) = each half the screen height, packed in 2 rows at the left of the main screen, then accounts/layout.yaml `right` instances (now Cmajor) at full height to their right; layout 2 = all instances in 1 row, evenly dividing the screen width.
---

# MuMu window layout

1. In `~/projects/chidojiro/miniheroes-auto`, run `osascript -l JavaScript scripts/layout.js` (**layout 1**, the default:
   2 rows + `right` column) or `LAYOUT=2 osascript -l JavaScript scripts/layout.js` (**layout 2**: 1 row, each window
   1/n of the screen width, order = `row` in `accounts/layout.yaml` — Nick, 2026-11-06). It prints `<name>: <x,y> <w,h>` per moved window.
2. Edit `accounts/layout.yaml` (MuMu instance names): `top`/`bottom` rows, `right` = full-height column after them (layout 1), `row` = layout 2's order, `exclude` = left alone.
3. If it fails with "not allowed assistive access", ask Nick to allow his terminal app in
   System Settings > Privacy & Security > Accessibility.

Only running instances are moved; start them first (`scripts/boot.sh`) if needed.
