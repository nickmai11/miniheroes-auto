---
name: miniheroes-dailies
description: Run Mini Heroes: Magic Throne daily missions (Land of Trials, Arena, Shop/Play Pass freebies, Tower of the Throne, Secret Sanctuary, Gate of Darkness, Beast Realm, free Recruit summons, hero upgrade, Tribe, Fishing, Divine Weapon, Stage, Patrol, rune synthesis, Grocery) on Nick's MuMuPlayer accounts via ADB, following per-account configs in the miniheroes-auto repo.
---

# Mini Heroes dailies

Use when Nick asks to run Mini Heroes dailies / a specific mission (e.g. "sweep Land of Trials on Cmajor", "do dailies for all accounts").

The repo `~/projects/chidojiro/miniheroes-auto` is the source of truth. CLAUDE.md holds the rules for every task;
this skill only adds the dailies-specific ones. Mission details, coords and account configs live in the repo.

## Steps

1. **Read**, in order:
   - `CLAUDE.md`
   - Only the `docs/ui-routine.md` sections for the missions you'll run: `scripts/doc.sh <section>...`
     (coordinator: just "Daily run order"; each helper: its missions)
   - `accounts/<account>.yaml` for each requested account (`scripts/accounts.py dailies` if he says "all" or names none)
   - `docs/setup.md` only if the emulator/network looks wrong
2. **Pre-flight (Nick, 2026-11-03):** after boot, before the real run, test every `docs/untested.md` row whose Test
   isn't `passive:` on ONE account (the step named there, watched live). Pass → remove the row, run all accounts.
   Fail → fix or report, and leave that step to helpers on the other accounts. After the run, grep the logs for each
   `passive:` row's Pass line and remove the rows that passed. Changes made during a run that can't be tested that
   day → add a row (what, how to test, what passing looks like). Mon–Wed: the Pet Arena rows ARE that account's first step.
   **Definition of Done (Nick, 2026-11-03): check the step's DoD in `docs/dod.md` before moving to the next task** — the on-screen evidence, not just an OK line; not met → its "Not done →" action, never move on silently.
3. **Run** — see "Cost" below: boot, `daily.py` per account in parallel, then one helper per account for its leftovers.
   The runner follows the **Daily run order** in `docs/ui-routine.md` and skips missions not in the account config.
   **Sundays:** the runner's `weekly` step (after `daily_mission`) does the weekly-missions pass — `accounts/weekly.yaml` top-down,
   ui-routine "Weekly Missions (Sunday pass)"; report its line (180 ✓ or what's short) per account (Nick, 2026-11-08).
4. **Checklist (Nick, 2026-11-11):** every `daily.py` run rewrites `checklists/<game day>/<account>.md` from the account's
   game-day log (`scripts/checklist.py`; full catch-up runs left out): grocery coins on top, then **Not done**, then Done.
   `checklists/<game day>/_highlights.md` = every account's undone boxes + coins above sanctuary 10k / ruins 3k /
   tundra 12k — start the report from it. Anything short of its DoD that is missing there = a `checklist.py` bug: fix
   its rule (+ a `--test` assert), regenerate, then report (Nick, 2026-11-13).
   Pet Arena = +40 deployments that day (catch-up `pet_check` count), or the missing ones deployed since (by hand / Auto Deploy restart), Sanctuary = floors 10/10, Events = no red dot left
   (Tribe Clash / Crystal Throne excepted), short counts (4/5, forge 4/7) = not done. Read them before reporting;
   a re-run of one step updates its box. Helper-done steps aren't in the log: re-run the step's script or note them.
   **Report** per account (CLAUDE.md "Reporting"); the runner prints every paid action with its price.
   **Every account must reach the 160 Daily Mission chest** (Nick, 2026-11-03): 16 of the 18 rows are scripted (not
   Upgrade Statue, Purchase with Diamonds). Below 160 → open that account's Daily Mission, match the open rows to
   their steps (`scripts/doc.sh "Daily Mission"`, "The 18 daily rows"), run / helper the missed step, then report.

**Cost — runner first, helpers only for leftovers (Nick, 2026-10-28 — urgent).** One helper per account for the whole
run cost ~850 turns × ~140k context (~112M cache-read per account, ~12% weekly for 8 accounts). Now:

1. `scripts/boot.sh <idx>...`, close event popups (one screenshot per account).
2. Run every account's runner in ONE background Bash command (CLAUDE.md "Fast feedback"):
   `for a in <acct>:<serial> ...; do (D=${a#*:} OUT=/tmp/miniheroes-$(date +%F)/${a%%:*} scripts/daily.py ${a%%:*} > /tmp/miniheroes-$(date +%F)/${a%%:*}.log 2>&1) & done; wait`
   Each log has one `OK|SKIP|FAIL|MANUAL <step>` line per step and ends with `LEFT FOR HELPER: …`
   (MANUAL lines: Sanctuary climb lost a floor,
   Canyon with no empty spot, event tabs with an unmapped red dot — plus any FAIL, each with `v_<step>.png`).
   Storm Rewards, Arena chests, Canyon empty spot, Canyon Points Reward and event milestones are runner steps
   since 2026-10-28. The runner retries each FAIL once right away, in order (2026-11-01) — don't re-run
   FAILed steps by hand; only what it still lists. Exit 1 = lost the main screen; exit 2 = a runner already holds that account.
   Watch failures live: Monitor `tail -F <dir>/*.log | grep --line-buffered -E '^(FAIL|Traceback)'`.
3. Per account with leftovers: ONE `mh-helper` whose prompt lists only those steps + their doc sections
   (`scripts/doc.sh …`) and the log's FAIL lines. Its final answer ≤15 lines (concerns, done/skipped, paid + price).
4. Report from `scripts/summary.sh <run dir>` (one call: FAIL/MANUAL/paid lines + LEFT per account — don't grep the logs
   one by one; cost, Nick 2026-10-29) + helper answers. Script bugs found mid-run: note them, fix after the run. A step's script is the doc's fallback text otherwise — see ui-routine "Speed".
   Helpers that run a single mission by hand use the scripts too (`arena.py`, `trials.py`, `patrol.py`, `hero.py`,
   `tribe.py`, `adventure.py`, `storm.py`, `veins.py`, `grocery.py`, `fish_orders.py`) and handle exit 1.

Instances must be 1080×1920 (`adb shell wm size 1080x1920 && adb shell wm density 480`, then restart the game) so the
documented coords apply. Helpers never edit the repo; the coordinator records what it learns (new coords, a popup, a
newly mapped mission) in that mission's `docs/ui-routine.md` section and commits it.

## Missions

Each mission's rules, coords and gotchas are its section in `docs/ui-routine.md` — helpers read them with
`scripts/doc.sh <mission>...` (only the missions in their account config). Don't paste mission details into helper
prompts; the doc is the single source.

## Language

The game UI is **English** on every account (Nick, 2026-10-28); the scripts match English button text.

**Log (Nick, 2026-10-28):** `daily.py` appends everything to `logs/<account>/<game day>.log` (game day starts 12:00 local).
Append each helper's final answer to the same file (`=== helper` header) — it's the record of what each account did.

## Hard rules (dailies only — the rest are CLAUDE.md's)

- If a "Match attempts full" popup appears mid-dailies: Confirm, use all Match tickets (Match routine, tribe rules), then resume where you left off.
- If a mission isn't documented in `docs/ui-routine.md` yet, don't improvise it on a gem-spending path — map it with Nick first, then document it.
