# Instructions for Claude

You are automating daily missions in **Mini Heroes: Magic Throne** for Nick, across several
game accounts. Each account lives in its own **MuMuPlayer** Android instance on Nick's Mac.

## Before doing anything

1. Read only the `docs/ui-routine.md` sections you need: `scripts/doc.sh <section>...` (e.g. `scripts/doc.sh Arena`).
   A coordinator that delegates to helpers needs just the skill file — helpers read their own sections.
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
"ADB alternative" in `docs/ui-routine.md`. Same rules.

## Hard rules

- **Never spend gems beyond what the account config allows.** Each mission entry gives a
  total sweep count _including_ free attempts. Free attempts are used first; paid sweeps
  (button shows a gem icon + price) only up to the configured total.
- If a paid sweep's gem price is higher than `max_gem_price_per_sweep` in the config, stop
  that mission and report instead of paying.
- Verify the attempt counter on screen before **and** after each sweep — never tap blindly.
- Don't touch anything outside the missions listed in the config (shop, purchases, settings).
  Exception: the free red-dot claims in `docs/ui-routine.md` ("Shop freebies", "Play Pass claims"); never a $ button —
  except the Floating Realm packs in an account's `floating_realm_packs` (Support 80 gems, Motivation ≤ 400 gems; `value` $0.99 / `joy` $4.99,
  paid in Stargems), each once a day at exactly that price, only with the balance on screen covering it (Nick, 2026-11-03).
- **Look only at decision points** (Nick, 2026-10-28, token cost): chain a step's fixed taps in ONE `tap.py` call with `--until x,y,r,g,b` on the expected next screen — exit 1 / timeout = unexpected → screenshot and decide. Read a screenshot before: any paid/priced tap, picking a target/opponent/row, reading a counter, the first tap of a step, and after any failed check. Never chain past a price or a choice.
- Account on a different screen than the task needs → move it there (`home()` in daily.py: back arrow, popups, Android
  Back), don't stop (Nick, 2026-10-31, every task). Stop and report only if that fails or the screen shows a choice/price.
- If a step can't be done with confidence (unreadable screen, tap not working after 2 tries), skip it and report
  it as skipped + why — never loop or guess.
- Waiting for the game (load, fight, animation): **poll, don't sleep long** (Nick, 2026-10-27: speed matters).
  Check every 1–2 s and continue the moment the screen is ready — `tap.py --until x,y,r,g,b` (a pixel of the next
  screen's button) or a short `until …; do sleep 1; done` loop. A fixed `sleep` only when there's nothing to poll,
  and keep it short. Always wait inside the same command: never background timers/Monitor, never end your turn to
  wait — a subagent did that on Aminor (2026-10-27), the wake-up never came, and the mission sat undone.

## Speed & cost (Nick, 2026-10-27 — applies to every skill)

- **Start-up:** `scripts/boot.sh <mumu index>...` boots the instances, restarts the game, taps Start, waits for the
  main screen and clears the event popups (`scripts/stabilize.py`: tick "Do not remind me today" + X), all in parallel
  (~25 s cold, ~15 s warm). Prints "<name> <serial> ready (stable …)" or "popup-stuck" (close that one by hand). Always boot first. Use it instead of
  manual start-up steps in any skill; runner and helpers then begin at a clean main screen.
- **Scripts first (Nick, 2026-10-28 — cost):** `scripts/daily.py <account> [step ...]` runs a whole account with no
  LLM; mission scripts (`arena.py`, `trials.py`, `patrol.py`, …) do single missions. A helper is only for what a
  script leaves (`LEFT FOR HELPER:` / exit 1). One run of helpers-for-everything cost ~12% of Nick's weekly tokens.
- **Helpers:** `subagent_type: "mh-helper"` (Sonnet, Bash+Read only), given its serial, own scratch dir and ONLY its
  leftover steps. Screenshots `tap.py -w 270` (×4 = device coords), `-w 540` only for small text (×2); poll waits.
- **Coordinator:** wait for runner/helper completion notifications; check a helper's screen only if it says
  it's "pausing/waiting" (red flag) or a notification is overdue.

## Action log (Nick, 2026-10-30 — every task, for retrospectives)

Every session (coordinator, helper, or a non-game task like a code change) appends a timestamped line per action
as it happens — not reconstructed at the end:
`echo "$(date '+%F %T') [<who>] <action> -> <result/why>" >> <log>`

- `<who>`: `coord`, `helper`, or `claude`. One line per tap batch / decision / script run / file edit / commit:
  what was done, what was seen, why it was chosen (esp. skips, paid taps with price, retries, anything off-spec).
- `<log>`: game work → `logs/<account>/<game day>.log` (same file `daily.py` writes, so one timeline per account;
  game day = `$(TZ=UTC date -v-5H +%F)`); anything else → `logs/claude/<date>.log` (create the dir if missing).
- `logs/` is gitignored, so helpers may write it despite "don't edit the repo".

## Reporting

At the end, report per account: each mission done/skipped (and why), and every paid action
(what, price). Lead with a **Concerns / issues / errors** section: anything that went wrong or off-spec
(wrong lineup, out-of-scope taps, mis-taps, crashes, helper claims that conflict with what Nick saw, things
left in a bad state like Auto fishing stopped) — Nick, 2026-10-27. Tell helpers to report these too. Don't track gem/resource balances — they change constantly (Nick, 2026-10-26);
just verify the price on screen before each paid tap.
