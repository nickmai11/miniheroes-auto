# Instructions for Claude

You are automating daily missions in **Mini Heroes: Magic Throne** for Nick, across several
game accounts. Each account lives in its own **MuMuPlayer** Android instance on Nick's Mac.

## Before doing anything

1. Read `docs/ui-routine.md` (how to perform each mission, coordinates, gotchas).
2. Read the account file(s) in `accounts/` for the account(s) you were asked to run ("group 1/2" → `accounts/groups.yaml`).
3. Skim `docs/setup.md` if something about the emulator/proxy looks off.

## Computer-use access

Request access for these apps only (Nick prefers the minimum):
- `MuMuPlayer` (bundle `com.netease.mumu.nemux-global`) — the instance list / launcher
- `MuMu Android Device` (bundle `com.netease.mumu.nemux-global.emulator`) — the game windows
- `Proxyman` (`com.proxyman.NSProxy`) — only if inspecting traffic

Work in **background mode** with the `computer_app_*` tools (screenshot/click on the emulator
window). Don't request full-screen control unless Nick agrees.

If computer-use tools aren't available, use ADB instead (Nick approved, 2026-10-26): see
"ADB alternative" in `docs/ui-routine.md`. Same rules — screenshot before every tap.

## Hard rules

- **Never spend gems beyond what the account config allows.** Each mission entry gives a
  total sweep count *including* free attempts. Free attempts are used first; paid sweeps
  (button shows a gem icon + price) only up to the configured total.
- If a paid sweep's gem price is higher than `max_gem_price_per_sweep` in the config, stop
  that mission and report instead of paying.
- Verify the attempt counter on screen before **and** after each sweep — never tap blindly.
- Don't touch anything outside the missions listed in the config (shop, purchases, settings).
  Exception: the free red-dot claims in `docs/ui-routine.md` ("Shop freebies", "Play Pass claims"); never a $ button.
- If the screen is in an unexpected state, stop and report with a screenshot description.
- If a step can't be done with confidence (unreadable screen, tap not working after 2 tries), skip it and report
  it as skipped + why — never loop or guess.
- Waiting for the game (load, animation): wait inside the same command, e.g. `sleep 40 && scripts/tap.py ...` or
  `tap.py --until`. Never use background timers/Monitor and never end your turn to wait — a subagent did that
  on Aminor (2026-10-27), the wake-up never came, and it sat idle with the mission undone.

## Reporting

At the end, report per account: each mission done/skipped (and why), and every paid action
(what, price). Don't track gem/resource balances — they change constantly (Nick, 2026-10-26);
just verify the price on screen before each paid tap.
