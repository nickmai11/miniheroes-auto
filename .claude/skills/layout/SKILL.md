---
name: layout
description: Resize and move Nick's running MuMuPlayer instance windows - layout 2 (default, every task — Nick 2026-11-07) = all instances in 1 row, evenly dividing the screen width; layout 1 = each half the screen height, packed in 2 rows at the left of the main screen, then accounts/layout.yaml `right` instances (now Kong, Cmajor) at full height against the screen's right edge; layout ct (Crystal Throne) = 1 row, every running instance 1/10 of the screen width.
---

# MuMu window layout

1. In `~/projects/chidojiro/miniheroes-auto`, run `osascript -l JavaScript scripts/layout.js` (**layout 2**, the default for every task — Nick 2026-11-07: 1 row, each
   window 1/n of the screen width, n = the accounts in `row` of `accounts/layout.yaml` (running or not; each keeps its slot), order = `row`) or `LAYOUT=1 osascript -l JavaScript scripts/layout.js`
   (**layout 1**: 2 rows + `right` column) or `LAYOUT=ct osascript -l JavaScript scripts/layout.js` (**layout ct**, Crystal Throne — Nick 2026-11-08:
   1 row, every running instance exactly 1/10 of the screen width, no empty slots, order = `row` then MuMu index). It prints `<name>: <x,y> <w,h>` per moved window.
2. Edit `accounts/layout.yaml` (MuMu instance names): `top`/`bottom` rows, `right` = full-height column after them (layout 1), `row` = layout 2's order, `exclude` = left alone.
3. If it fails with "not allowed assistive access", ask Nick to allow his terminal app in
   System Settings > Privacy & Security > Accessibility.

Only running instances are moved; start them first (`scripts/boot.sh`) if needed.
