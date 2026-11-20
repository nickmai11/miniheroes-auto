---
name: fps
description: Set the frame-rate cap of Nick's MuMuPlayer instances - "fps 30" / "fps 60" (all instances), "fps 60 kong tiger" (only those). 60 outside tasks; every task runs at 30 (boot.sh sets it, incl. Kong/Cmajor) and puts 60 back when done (Nick 2026-11-13).
---

# MuMu frame-rate cap

1. Instances: the names given (account → `mumu_instance` in `accounts/<account>.yaml`, index from
   `mumu-cli info all`), else `all`. When to use which cap: CLAUDE.md "FPS".
2. `"$(scripts/accounts.py mumu)" config <all|i,j,…> --setting '{"maxFpsLimit":<N>}'`
   (`-1` = uncapped), then read it back per instance: `mumu-cli config <i>` → `return.callback.maxFpsLimit`.
3. It applies live, running instances included (docs/setup.md "Frame rate").
4. If the default changes, update CLAUDE.md "FPS".

Report: the cap and which instances got it (read back).
