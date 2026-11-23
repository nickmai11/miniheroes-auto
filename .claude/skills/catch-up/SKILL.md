---
name: catch-up
description: Mini Heroes: Magic Throne catch-up run - Arena (incl. Ranking Rewards), Storm, Canyon, Fishing, Divine Weapon, Patrol, Tribe request/assist, free Common Recruitment, event red dots, Daily Mission claims + chests on every account, via ADB.
---

# Mini Heroes catch-up

Use when Nick asks for "catch up" / "top-up" on Mini Heroes. Default: `scripts/accounts.py catchup` (`accounts/tasks.yaml`), unless Nick names accounts.

1. In `~/projects/chidojiro/miniheroes-auto`, read the account files (not `docs/ui-routine.md` — helpers read their sections).
2. `scripts/boot.sh <mumu index>...` — boots, **restarts** the game, clears event popups (must print "ready (stable …)").
3. **Runner first (Nick, 2026-10-28 — cost):** all accounts in ONE background Bash command, wait for its notification:
   `for a in <acct>:<serial> ...; do (D=${a#*:} OUT=/tmp/miniheroes-$(date +%F-%H)/${a%%:*} scripts/daily.py ${a%%:*} --catch-up > /tmp/miniheroes-$(date +%F-%H)/${a%%:*}.log 2>&1) & done; wait`
   It does ALL steps below (claims, Canyon empty spot and event milestones too since 2026-10-28) and ends with
   `LEFT FOR HELPER:` = only MANUAL lines (no empty Canyon spot → attack choice: a Sentinel, else a non-tribe player; event tabs with an unmapped red dot)
   and FAILs with `v_<step>.png`. Empty list → no helper for that account. Otherwise ONE `mh-helper` per account for
   only those, prompt below trimmed to them — **started the moment that account's `LEFT FOR HELPER:` line shows, never
   after the whole run** (Nick, 2026-11-24: "don't wait, act promptly" — Tiger sat idle with a Canyon leftover while
   others ran). One Monitor surfaces failures and per-account ends live (Dino 2026-10-28 sat 8 min on a FAIL start
   nobody saw): `tail -F <run dir>/*.log | grep --line-buffered -E '^(FAIL|Traceback|LEFT FOR HELPER)'`.
   `scripts/summary.sh <run dir>` once at the end for the report.
   The runner retries each FAIL once right away (in order, 2026-11-01); re-run by hand only after exit 1 (lost the main screen),
   with only the steps after its last OK: `daily.py <acct> --catch-up <step>...` (zsh: pass the steps as
   separate words — `${=steps}` — a quoted list runs nothing, 2026-10-29).
   **Canyon MANUAL → re-run `daily.py <acct> --catch-up canyon` once first** (2026-10-29: canyon.py found nothing on 7
   accounts, minutes later 7 helpers each found an empty spot — ~40 tool calls apiece for a free Occupy). Helper only
   if the re-run still says MANUAL; check its `canyon<N>.png` per-screen shots in the run dir to see why.
   Steps (the spec the runner follows; see `docs/ui-routine.md`). **Order = `CATCHUP` in `scripts/daily.py`** — the list
   below is in that order, each with its runner step name; change the order there, then here.
   **Red dots only (Nick, 2026-10-27):** for claims (events, Tribe Clash Pack, Daily Mission, rewards icons) open/tap
   only what shows a red dot — no red dot = nothing to collect, don't open it to check. 0. `weekly_review` — **Sundays first** (Nick 2026-11-08): reads the Weekly Mission tab, decides whether the
   50-Lucky-Stars row is needed for 180 and writes the day's plan; the fishing steps then use the Lucky Star bait only if
   it is, else the account's default bait (ui-routine "Weekly Missions (Sunday pass)").
   1. `fishing_auto` — Fishing **first** (Nick, 2026-10-29 — Auto then runs during everything else): only start Auto
      (fishing) and claim completed order rewards — no order refreshing, no Benefit
   2. `arena` — Ranking Rewards gift boxes first (Nick, 2026-10-29), then exhaust free tickets (`scripts/arena.py <account>`),
      then the win-chest claims — same visit, every runner arena step
   3. `storm` — Storm Battlefield (skip if its season is closed — times: ui-routine Storm): run `scripts/storm.py` from the
      arena screen — it sets the full lineup first and resets to 1 hero after (ui-routine Storm steps 2–4, 6); report its
      output. Never two accounts of one server block (s201–210, s211–220) in Storm at once — the runner's step locks per
      block. Then **Rewards** (left side) if it has a red dot — same visit
   4. `veins_forge` — Divine Weapon: Excelsior Veins via `scripts/veins.py` (stops at 0 pickaxes), then Forge: fill every
      free slot (N/M) while crystals ≥ cost, even if a forge is already running (Nick, 2026-10-28), then Benefit's Claim
      Rewards (pass accounts; after the forging — Nick 2026-11-04); skip Forge if the account has `divine_forge: false`
      (Kong, 2026-10-30)
   5. `patrol_claim` — Patrol: Claim All only (`scripts/patrol.py <account> --claim-only`) — no Speed Patrol
   6. `arena2` — Arena again: Claim All often gives Arena tickets → spend them (same as step 2)
   7. `tribe_chat` — Tribe chat Request + Assist, every run incl. mornings (Nick, 2026-11-08: on cooldown the tap does
      nothing) (Tribe section, step 4 only; `tribe.py --chat-only`)
   8. `common_recruit` — Common Recruitment (Recruit section, step 2 only): draw every **Free** chance available (no Play
      Pass: each one is a video ad, `recruit()` watches it — Nick 2026-11-08); if it's on cooldown or out of chances,
      skip — don't wait, never pay
   9. `canyon` — Canyon Clash (skip if its season is closed — times: ui-routine Canyon): **take a new spot even if one is
      already held** (`scripts/canyon.py`: empty spots only, popup text checked; no empty one → helper); Points Rewards
      claimed **after** the spot (occupying earns the points — Nick 2026-11-04), same visit
   10. `events` — event banners with a red dot (ui-routine Events): claim only free Claim/Free rewards; never a $ or gem
       price. **Collect only** (Nick, 2026-10-28): never Open All / draw / spin / use any event token, ticket or coin,
       even free ones (7777 Draws: daily Claim only, no Open All). Never Tribe Clash's Treasures or "Enter" (Nick,
       2026-10-27); its free Pack claim is fine
   11. `fishing_rewards` — Fishing orders again: claim any order reward that completed during the run (Auto fishing keeps
       filling them) — claim only, no refresh, don't touch Auto (Nick, 2026-10-27)
   12. `daily_mission` — Daily Mission (missions always last, Nick 2026-10-29), only if its menu icon has a red dot: on the
       **Daily and Weekly** tabs (each with a red dot) tap ONE yellow **Claim** row (claims all rows) and ONE reachable
       chest (claims all reachable chests) — never scroll, top row not claimable = done (Nick, 2026-10-27/28); report
       chests still locked + activity points
   13. `play_pass2` — Play Pass again (after the missions — Nick, 2026-11-03): claim any Play Pass red dot the run's
       activity unlocked; never a $ button.
   14. `pet_check` — Pet Arena check (Mon–Wed): Achievement cumulative deployments +40 since yesterday = all 40 free
       attempts used; short → Auto Deploy restarted, reported.
       **As soon as an account's helper finishes** (that account alone, not after all helpers), one more runner pass on **only the accounts that had a helper** (orders keep completing
       during the helpers; Nick, 2026-10-28): `daily.py <acct> --catch-up common_recruit fishing_rewards` — drop
       `fishing_rewards` if that account's earlier line said `AUTO STOPPED, bread N` (no bread = no new orders; Nick
       2026-10-29: the order claim ran 3-4x per account). Never re-run a step just to read something off the screen.
   15. `relic` — Relics, the runner's last step, on every catch-up account incl. Kong II (Nick 2026-11-10 / 2026-11-16:
       "relic is part of catchup"; never filter by the relic list; a runner step since 2026-11-20, was `relic_all.sh`
       after the run): `relic.py <account>`. **No auto-retry:** its FAIL = relic.py stopped mid-board → handle per the
       miniheroes-relic skill step 2 (never re-run it blindly); its `done:` line (digs, items, shovels left) goes in the report.
       `relic_skip_until: <date>` in an account file = `SKIP relic off until …` before that game day (Kong until 2026-11-30, Nick 2026-11-21).
4. Workers don't edit the repo; afterwards add new findings to the docs and commit.
5. Report: lead with **Concerns / issues / errors** (see CLAUDE.md "Reporting"), then per account: each step
   done/skipped (and why), every paid action with its price, and which Daily Mission chests are still
   unclaimable (with the activity points shown).

## Helper prompt (use as-is; fill in <…>; add any rule Nick gives mid-run to this file too)

```
Mini Heroes catch-up leftovers on ONE account: <Name>, ADB serial <serial>, MuMu index <index>, scratch dir <dir> (save screenshots there as
s1.png, s2.png…). Repo ~/projects/chidojiro/miniheroes-auto: do ONLY these steps from .claude/skills/catch-up/SKILL.md
step 3: <leftover steps + the runner's FAIL lines>, the output of
`scripts/doc.sh Arena Storm Canyon Fishing Divine Patrol Tribe Recruit Events "Daily Mission"` (don't read the
whole docs/ui-routine.md) and accounts/<file>.yaml. Don't edit the repo.
Game is at the main screen; close popups with X / Cancel (never GO); tick "Do not remind me today" first if the popup has it. Today: <weekday date time> (<Storm/Canyon open?>).
Tools: D=<serial> python3 scripts/tap.py [x,y…] -w 270 -o <dir>/sN.png [--until x,y,r,g,b | --until-text REGEX] [--timeout s]
(every navigation tap waits on the next screen: doc "Speed" table; --until-text prints the screen text); -w 270 for
navigation (×4 = device coords), -w 540 only for small text (×2). Storm: scripts/storm.py (handles lineup). Veins: scripts/veins.py. Arena: scripts/arena.py <account>.
Rules: look only at decision points — chain a step's fixed taps in one tap.py call with --until on the next
screen's pixel; read a screenshot before prices, target picks, counters, a step's first tap, and after a failed check; no gems/money beyond the config; poll waits inside the command (1–2 s), never
background timers or "pausing"; game crash / Android home → `scripts/boot.sh <index>` (CLAUDE.md);
own loops must re-check the stop condition (counter/popup) every pass — never a fixed-count blind loop;
can't do a step after 2 tries → skip + note why. Before the next step, check this step's DoD (docs/dod.md). Nick may tap the screen himself.
Last command before your final answer: `touch <dir>/DONE` (the coordinator's idle watch skips finished helpers).
Final answer: CONCERNS/ISSUES/ERRORS first (mis-taps, out-of-scope screens opened, wrong lineup, crashes, anything
left in a bad state), then per step done/skipped (+why), every paid action + price, Daily Mission chests still
locked + points, new findings (coords/behaviour not in the docs).
```

**Log (Nick, 2026-10-28):** `daily.py` appends everything to `logs/<account>/<game day>.log` (game day starts 12:00 local).
Append each helper's final answer to the same file (`=== helper` header) — it's the record of what each account did.

## Hard rules

- **Definition of Done (Nick, 2026-11-03): check the step's DoD in `docs/dod.md` before moving to the next task** — the on-screen evidence, not just an OK line; not met → its "Not done →" action, never move on silently.
- Everything else: CLAUDE.md "Hard rules" (paid only within the config, wrong screen → `home()`, look only at decision points).
