# Instructions for Claude

You are automating daily missions in **Mini Heroes: Magic Throne** for Nick, across several
game accounts. Each account lives in its own **MuMuPlayer** Android instance on Nick's Mac.

## Before doing anything

1. Read `docs/ui-routine.md` (how to perform each mission, coordinates, gotchas).
2. Read the account file(s) in `accounts/` for the account(s) you were asked to run.
3. Skim `docs/setup.md` if something about the emulator/proxy looks off.

## Computer-use access

Request access for these apps only (Nick prefers the minimum):
- `MuMuPlayer` (bundle `com.netease.mumu.nemux-global`) — the instance list / launcher
- `MuMu Android Device` (bundle `com.netease.mumu.nemux-global.emulator`) — the game windows
- `Proxyman` (`com.proxyman.NSProxy`) — only if inspecting traffic

Work in **background mode** with the `computer_app_*` tools (screenshot/click on the emulator
window). Don't request full-screen control unless Nick agrees.

## Hard rules

- **Never spend gems beyond what the account config allows.** Each mission entry gives a
  total sweep count *including* free attempts. Free attempts are used first; paid sweeps
  (button shows a gem icon + price) only up to the configured total.
- If a paid sweep's gem price is higher than `max_gem_price_per_sweep` in the config, stop
  that mission and report instead of paying.
- Verify the attempt counter on screen before **and** after each sweep — never tap blindly.
- Don't touch anything outside the missions listed in the config (shop, purchases, settings).
- If the screen is in an unexpected state, stop and report with a screenshot description.

## Reporting

At the end, report per account: each mission, free/paid sweeps done vs. configured, gems
before/after, and anything skipped and why.
