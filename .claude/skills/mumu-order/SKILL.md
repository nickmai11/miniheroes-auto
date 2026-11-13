---
name: mumu-order
description: Restore / change the order of the instances in Nick's MuMuPlayer launcher list ("the order of mumu instances is messed up, bring it back") from accounts/layout.yaml `mumu:` (scripts/mumu_order.py). Not the window tiling — that's the layout skill.
---

# MuMu launcher order

1. The order is `mumu:` in `accounts/layout.yaml` (MuMu instance names, top to bottom). Nick changes it there; show
   him the line when he asks for the list.
2. `scripts/mumu_order.py` (`--dry` = print only) writes it to MuMu's
   `~/Library/Application Support/com.netease.mumu.nemux-global/setting/common.json` → `managerListIndexs`
   (`<instance index>-<position>`, unlisted instances last), with a timestamped `.bak-…` copy next to it.
3. The launcher reads the file at start: the new order shows after MuMuPlayer is quit and reopened. Quitting the
   launcher asks to close every running instance — **don't quit it while an instance is in use**; ask Nick, or tell
   him it applies at his next restart. If the launcher overwrote the file on quit, run the script again before reopening.
