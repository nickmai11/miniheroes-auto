# Instructions for Claude

You are automating daily missions in **Mini Heroes: Magic Throne** for Nick, across several
game accounts. Each account lives in its own **MuMuPlayer** Android instance on Nick's Mac.

## Before doing anything

1. Read only the `docs/ui-routine.md` sections you need: `scripts/doc.sh <section>...` (e.g. `scripts/doc.sh Arena`).
   A coordinator that delegates to helpers needs just the skill file — helpers read their own sections.
2. Read the account file(s) in `accounts/` for the account(s) you were asked to run ("group 1/2" → `accounts/groups.yaml`).
   No accounts named, or "all" → `scripts/accounts.py <task>` (per-task lists in `accounts/tasks.yaml`: dailies, catchup,
   arena, poseidon, realm, relic, tc_guess, fr_guess, survey, boot, artifact_roll, gear, climb_stage, treasury, code, hero_faces — Nick, 2026-11-06).
3. Skim `docs/setup.md` if something about the emulator/proxy looks off.

## Computer-use access

Request access for these apps only (Nick prefers the minimum):

- `MuMuPlayer` (bundle `com.netease.mumu.nemux-global`) — the instance list / launcher
- `MuMu Android Device` (bundle `com.netease.mumu.nemux-global.emulator`) — the game windows

Work in **background mode** with the `computer_app_*` tools (screenshot/click on the emulator
window). Don't request full-screen control unless Nick agrees.

If computer-use tools aren't available, use ADB instead (Nick approved, 2026-10-26): see
"ADB alternative" in `docs/ui-routine.md`. Same rules.

## Hard rules

- **Power doesn't matter** (Nick, 2026-11-06, every task): never store, check, compare or report team power, and never
  predict a fight from it; lineups are judged only by which heroes are on them. Mission rules that pick a target by
  the CP shown on screen (Arena Challenge, Poseidon lowest-CP ship) are unchanged.
- **Allies** (Nick, 2026-11-10): in **Tribe Clash** never attack a tribe from a server in `accounts/allies.txt`
  (150 190 194 156 320 300 175 288 54). Other events (Crystal Throne, Floating Realm) aren't affected.
- **Never spend gems beyond what the account config allows.** Each Land of Trials entry gives the top
  gem price to pay in that dungeon (Nick, 2026-11-11; was a sweep count): 2 free sweeps first, then paid
  ones at 80 / 160 / 240… only while the price is ≤ the configured one (0 = free only; Kong `gem_mine: 240` = 5 sweeps).
- Verify the attempt counter on screen before **and** after each sweep — never tap blindly.
- Don't touch anything outside the missions listed in the config (shop, purchases, settings).
  Exception: the free red-dot claims in `docs/ui-routine.md` ("Shop freebies", "Play Pass claims"); never a $ button —
  except the Floating Realm packs in an account's `floating_realm_packs` (Support 80 gems, Motivation ≤ 400 gems; `value` $0.99 / `joy` $4.99,
  paid in Stargems), each once a day at exactly that price, only with the balance on screen covering it (Nick, 2026-11-03).
- **Look only at decision points** (Nick, 2026-10-28, token cost): chain a step's fixed taps in ONE `tap.py` call with `--until x,y,r,g,b` on the expected next screen — exit 1 / timeout = unexpected → screenshot and decide. Read a screenshot before: any paid/priced tap, picking a target/opponent/row, reading a counter, the first tap of a step, and after any failed check. Never chain past a price or a choice.
- Account on a different screen than the task needs → move it there (`home()` in flow.py, the one copy: back arrow, popups, Android
  Back), don't stop (Nick, 2026-10-31, every task). Stop and report only if that fails or the screen shows a choice/price.
- **Game crashed / on the Android home → `scripts/boot.sh <mumu index>` and retry the step** (Nick, 2026-10-27; every
  task 2026-11-20): boot is the only relaunch; its `MAX_RELAUNCHES` (10) is the only limit. Built into `flow.main()`
  (every mission script) and `flow.home()`; helpers run it themselves.
- If a step can't be done with confidence (unreadable screen, tap not working after 2 tries), skip it and report
  it as skipped + why — never loop or guess.
- **Paid buys: one pack at a time** (Nick, 2026-11-14 — 300 gems lost to a loop): buy 1, close its popup, check the
  count went up, use it, then the next; any buy loop stops when a buy didn't change the state. Walk a new or changed
  buy path by hand once (open → price → buy → close → count) before scripting it, and watch its first live run.
- **Right account** (every task): the top-right game id must match the account file's `game_id` before acting
  (Kong reopens on S288 Kong II after a game restart) → `stabilize.py` switches back.
- **Kong II** (`kong_ii`, S288, on Kong's instance — Nick, 2026-11-17): catch-ups, dailies and the scheduled Floating
  Realm / Tribe Clash rounds (`fr_all.sh`), and the tc / fr guesses (Nick, 2026-11-19) do it too, right after Kong is
  done there (catch-up: relics included); any other task only when named. Switch: `D=<serial> ACCOUNT=kong_ii scripts/stabilize.py` (exit 0 = its id read on
  screen), back with `ACCOUNT=kong` when Kong II is done.
- **Tick "Do not remind me today"** wherever it shows, before closing the popup (Nick, 2026-10-29, every task).
- **Scroll slowly** (every task): held drags ≥ 1.5 s, one at a time, read only once the screen is still — never fling,
  not even to reach an end.
- **Rules beat scripts:** a script that contradicts a rule here or in a skill is a bug — say so and fix it. Describe
  what happened from the screen/log, never from code comments.
- Waiting for the game (load, fight, animation): **poll, don't sleep long** (Nick, 2026-10-27: speed matters).
  Check every 1–2 s and continue the moment the screen is ready — `tap.py --until x,y,r,g,b` (a pixel of the next
  screen's button) or a short `until …; do sleep 1; done` loop. A fixed `sleep` only when there's nothing to poll,
  and keep it short. Always wait inside the same command: never background timers/Monitor, never end your turn to
  wait — a subagent did that on Aminor (2026-10-27), the wake-up never came, and the mission sat undone.

## Speed & cost (Nick, 2026-10-27 — applies to every skill)

- **Start-up:** `scripts/boot.sh <mumu index>...` boots the instances, restarts the game, taps Start, waits for the
  main screen and clears the event popups (`scripts/stabilize.py`: tick "Do not remind me today" + X), in parallel
  (~25 s cold, ~15 s warm); at most 4 instances boot at once, the next 4 once the CPU is calm (Nick, 2026-11-17,
  every task that boots several accounts — never one `boot.sh` per account in parallel). Prints "<name> <serial> ready (stable …)" or "popup-stuck" (close that one by hand). Always boot first. Use it instead of
  manual start-up steps in any skill; runner and helpers then begin at a clean main screen.
- **FPS (Nick, 2026-11-13, every task):** tasks run at 30 fps on every instance, Kong and Cmajor included — `boot.sh`
  sets 30 before it opens an instance. **When the task is done:** `mumu-cli config all --setting '{"maxFpsLimit":60}'`
  (applies live; `fr_all.sh` does it itself). Caps below 30 are ignored. **1 core** per instance (Nick, 2026-11-17):
  `boot.sh` sets it too, applies at instance start.
- **Scripts first (Nick, 2026-10-28 — cost):** `scripts/daily.py <account> [step ...]` runs a whole account with no
  LLM; mission scripts (`arena.py`, `trials.py`, `patrol.py`, …) do single missions. A helper is only for what a
  script leaves (`LEFT FOR HELPER:` / exit 1). One run of helpers-for-everything cost ~12% of Nick's weekly tokens.
- **Helpers:** `subagent_type: "mh-helper"` (Sonnet, Bash+Read only), given its serial, own scratch dir and ONLY its
  leftover steps. Screenshots `tap.py -w 270` (×4 = device coords), `-w 540` only for small text (×2); poll waits.
- **Coordinator:** wait for runner/helper completion notifications; check a helper's screen only if it says
  it's "pausing/waiting" (red flag) or a notification is overdue.
- **Fast feedback:** long commands (boot, batches) run in the background; read their output after ~30 s and act on a
  straggler instead of waiting for its timeout; start ready accounts without waiting. One Monitor per batch
  (`daily.py` run dir, `relic_all.sh`, `fr_all.sh`, `catchup_all.sh`) for `FAIL` / `Traceback` / `exit 1` — act the
  moment one shows (home + re-run that account).
- **Right tool:** fixed taps / counters / pixel checks → a script; judgment (targets, unknown popups) → helper or
  skill. If Nick asks for the wrong one, say which fits and why in one line, then do it.

## Action log (Nick, 2026-10-30 — every task, for retrospectives)

Every session (coordinator, helper, or a non-game task like a code change) appends a timestamped line per action
as it happens — not reconstructed at the end:
`echo "$(date '+%F %T') [<who>] <action> -> <result/why>" >> <log>`

- `<who>`: `coord`, `helper`, or `claude`. One line per tap batch / decision / script run / file edit / commit:
  what was done, what was seen, why it was chosen (esp. skips, paid taps with price, retries, anything off-spec).
- `<log>`: game work → `logs/<account>/<game day>.log` (same file `daily.py` writes, so one timeline per account;
  game day = `$(TZ=UTC date -v-5H +%F)`); anything else → `logs/claude/<date>.log` (create the dir if missing).
- `logs/` is gitignored, so helpers may write it despite "don't edit the repo".

## Working with Nick

- **A question gets an answer, not a fix** (Nick, 2026-11-14): cause, numbers, evidence, my view — no edits, no runs
  started or stopped until he asks or agrees; at most offer the fix in one line. When he critiques a decision, check
  the log/screen and agree or push back with the facts — no reflexive "you're right".
- **Quiet during runs:** no progress chatter ("X done, waiting"); speak only for a real problem or a choice, then the
  final report.
- **Shorthand:** fr = Floating Realm, tc = Tribe Clash, ct = Crystal Throne — chat only; steps and config keys use the
  full name (`tribe_clash_packs`, `floating_realm_packs`).
- **Crystal Throne:** Nick gives the orders, Claude executes on every account and never picks targets — read
  `docs/crystal-throne.md` and open `docs/crystal-throne-names.png` first.
- **One home per rule:** a rule for every task goes here; a task's rule goes in its skill or `docs/ui-routine.md`
  section. Never in Claude's memory, never in two places.

## Docs

- After writing or editing any `.md`: `npx --yes prettier --write <file> && npx --yes prettier --check <file>`, output
  visible. No `--prose-wrap` on the command line (`.prettierrc.yaml` decides).
- `docs/open-issues.md` = every open problem (❌ bug, ❓ needs Nick). Update it in the same turn as the finding, fix or
  decision: new problem → new row; seen again → add the date to its row; fixed → delete the row (fixed but not yet
  live-tested → a `docs/untested.md` row). The old per-day struggles files are in `docs/archive/`.
- `docs/untested.md` = changes waiting for a live test (dailies Pre-flight); a row goes once it passed.

## Reporting

At the end, report per account: each mission done/skipped (and why), and every paid action
(what, price). Lead with a **Concerns / issues / errors** section: anything that went wrong or off-spec
(wrong lineup, out-of-scope taps, mis-taps, crashes, helper claims that conflict with what Nick saw, things
left in a bad state like Auto fishing stopped — but not out of bait: normal, never report it, Nick 2026-11-16) — Nick, 2026-10-27. Tell helpers to report these too. Don't track gem/resource balances — they change constantly (Nick, 2026-10-26; exception: the grocery shop coins, top of each dailies checklist, Nick 2026-11-11);
just verify the price on screen before each paid tap.

- **OK lines aren't proof:** before saying "done", check the screen of one account against the log — a leftover red
  dot is a bug. "You didn't check X" from Nick = assume the step is wrong on every account: find the cause, fix,
  re-run everywhere, then report.
- End every task's report with the line from `scripts/tokens.sh --since "<the user's prompt text>"`.
