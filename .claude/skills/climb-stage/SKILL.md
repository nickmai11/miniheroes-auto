---
name: climb-stage
description: Mini Heroes: Magic Throne climb stage - push the Adventure stages on the game's auto stage with Nick's 3 lineup tabs, Challenge again on Defeat, swap lineups after 3 losses in a row, next chapter after X-40, on his MuMuPlayer accounts via ADB (scripts/climb_stage.py). Use for "climb stage / do stage / stage <account>".
---

# Climb stage

Use when Nick says "climb stage" / "do stage" / "stage <account>". Not the dailies Stage step (3 fights, Bone Archer
alone — `daily.py <account> stage`, only when he says "daily stage"); not Tower/Sanctuary/Realm floors. Accounts: the
ones named, else `scripts/accounts.py climb_stage`. Details: `scripts/doc.sh "Climb stage"`.

1. Boot: `scripts/boot.sh <idx>` (index from `mumu-cli info all`). Check `adb -s $D shell wm size` is **1080x1920**
   (PuPu was 600x1080 → see the gear skill step 1 to fix).
2. **Swap-ready or don't run** (Nick, 2026-11-02): `stage_lineups` in `accounts/<account>.yaml` must match the
   screen. Missing, Nick changed a lineup, or a daily Stage ran since the last record (it sets tab 1 = Bone Archer
   alone) → `scripts/climb_stage.py <account> --record --no-start` (opens a fresh setup, reads the green checks of
   tabs 1–3, rows 1–5, writes the yaml; exit 1 "not 5 cells" = a hero further down / empty tab → tell Nick, don't run).
3. **Recheck the lineups before Start** (Nick, 2026-11-02): on the setup, per tab
   `scripts/tap.py <380|540|700>,1088 -o tab<N>.png -w 540` and read the heroes (never judge by power). Wrong or
   unsure → show Nick, stop. First time on an account → show him the 3 tabs and wait for his OK.
4. Start `scripts/tap.py 540,1806 --until-text 'x2|Victory|Defeat' --timeout 30`, then
   `scripts/climb_stage.py <account>` in the **foreground** (Bash timeout 600000; ~9 min per call, several accounts
   in one call). It watches all named accounts: Defeat → Challenge again; 3 losses in a row on one stage → swaps the
   losing wave's team with the next tab (max 3 swaps per stage); X-40 cleared → Next chapter → Start.
5. Exit codes — act at once:
   - **0** "still climbing: {…}" → run it again (keep chaining calls; no pause to ask). Stop when Nick's limit
     (stage, chapter, time) is reached or he says stop.
   - **2** (swap failed / still lost after 3 swaps) → stop and report the log lines. Never `--apply` + Start, never
     run without swaps.
   - **1** (a screen didn't show, stuck 4 min) → read `/tmp/climb_stage_<account>.png`; off the stage screen → the
     next call moves it back (`home()`); else report.
6. Nick changes a lineup mid-run → stop, `--record`, recheck (step 3), resume.

Report per account: start → end stage, defeats/swaps (log lines `[climb_stage]` in `logs/<account>/<game day>.log`),
every exit 1/2 and what was done about it. No gems are ever spent here.
