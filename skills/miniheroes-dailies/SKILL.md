---
name: miniheroes-dailies
description: Run Mini Heroes: Magic Throne daily missions (e.g. Land of Trials sweeps) on Nick's MuMuPlayer accounts via computer use, following per-account configs in the miniheroes-auto repo.
---

# Mini Heroes dailies

Use when Nick asks to run Mini Heroes dailies / a specific mission (e.g. "sweep Land of Trials on Cmajor", "do dailies for all accounts").

The source of truth is the repo on Nick's Mac: `~/projects/chidojiro/miniheroes-auto`. This skill only says how to get there and the rules that never change; mission details, tap coordinates and account configs live in the repo.

## Steps

1. **Get the repo.** Request folder access to `~/projects/chidojiro` (or `~/projects/chidojiro/miniheroes-auto`) on Nick's computer. Read, in order:
   - `CLAUDE.md`
   - `docs/ui-routine.md` (and the section for each mission you'll run)
   - `accounts/<account>.yaml` for each requested account (all `enabled: true` accounts if he says "all")
   - `docs/setup.md` only if the emulator/network looks wrong
2. **Get app access (minimum set).** Via computer use: resolve and request access to `MuMuPlayer` and `MuMu Android Device` only. Work in background mode with the `computer_app_*` tools. Don't request full-screen control or other apps unless Nick agrees.
3. **Run each account** in its MuMu instance: start the instance if needed, open the game, then for each mission in the account config follow the routine in `docs/ui-routine.md`.
4. **Report** per account: each mission, free/paid done vs. configured, gems before/after, anything skipped and why.
5. **Keep the repo current.** If you learn something new (new coordinates, a popup, a new mission mapped), update the relevant doc and commit it.

## Hard rules

- Configured counts are totals per day **including** free attempts. Use free first; pay with gems only up to the configured total.
- Never pay more than `max_gem_price_per_sweep` (from the account config) for one sweep — stop that mission and report instead.
- Read the attempt counter on screen before and after every sweep; never chain taps blindly. Taps during popup animations are ignored, so screenshot first.
- On-screen counters are the source of truth for what was already done today.
- Touch nothing outside the configured missions (no shop, purchases, settings, events).
- If the screen is in an unexpected state, stop and report what you see.
- If a mission isn't documented in `docs/ui-routine.md` yet, don't improvise it on a gem-spending path — map it with Nick first, then document it.
