---
name: fps
description: Set the frame-rate cap of Nick's MuMuPlayer instances - "fps 30" / "fps 60" (all instances), "fps 60 kong tiger" (only those). 60 outside tasks; every task runs at 30 (boot.sh sets it, incl. Kong/Cmajor) and puts 60 back when done (Nick 2026-11-13).
---

# MuMu frame-rate cap

1. Instances: the names given (account → `mumu_instance` in `accounts/<account>.yaml`, index from
   `mumu-cli info all`), else `all`. Standing rule (Nick 2026-11-13, replaces "Kong and Cmajor always 60"): 60 outside
   tasks; a task runs at 30 on every instance incl. Kong and Cmajor (`boot.sh` sets it per instance it opens) and sets
   `all` back to 60 when done (CLAUDE.md "FPS").
2. `"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" config <all|i,j,…> --setting '{"maxFpsLimit":<N>}'`
   (`-1` = uncapped), then read it back per instance: `mumu-cli config <i>` → `return.callback.maxFpsLimit`.
3. It applies on the instance's next start. Running instances keep the old cap until restarted — say which ones; restart
   them (`scripts/boot.sh <idx>…`) only if Nick asks or nothing is running a task on them.
4. If the default changes, update the "Frame rate" line in `docs/setup.md`.

Report: the cap, which instances got it, which are still running on the old one.
