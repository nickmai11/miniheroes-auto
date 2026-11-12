---
name: fps
description: Set the frame-rate cap of Nick's MuMuPlayer instances - "fps 30" / "fps 60" (all instances), "fps 60 kong tiger" (only those). Default since 2026-11-12 = 30 (idle CPU 28% -> 21%, nothing slower).
---

# MuMu frame-rate cap

1. Instances: the names given (account → `mumu_instance` in `accounts/<account>.yaml`, index from
   `mumu-cli info all`), else `all`.
2. `"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" config <all|i,j,…> --setting '{"maxFpsLimit":<N>}'`
   (`-1` = uncapped), then read it back per instance: `mumu-cli config <i>` → `return.callback.maxFpsLimit`.
3. It applies on the instance's next start. Running instances keep the old cap until restarted — say which ones; restart
   them (`scripts/boot.sh <idx>…`) only if Nick asks or nothing is running a task on them.
4. If the default changes, update the "Frame rate" line in `docs/setup.md`.

Report: the cap, which instances got it, which are still running on the old one.
