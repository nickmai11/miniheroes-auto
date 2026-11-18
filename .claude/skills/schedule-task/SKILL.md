---
name: schedule-task
description: Schedule a Mini Heroes task to run unattended, like the fr all job - once (in N min, at a time, on a date), every day, or on given weekdays - "schedule boot in 5 mins", "schedule catch-up daily 17:00", "schedule <task> mon,wed 05:00", "list schedules", "unschedule <name>" (launchd via scripts/schedule.py).
---

# Schedule a task

All of it is `scripts/schedule.py` (launchd job `com.nickm.miniheroes-<name>`, under `caffeinate -i -s`, run from the repo
root, output → `logs/launchd-<name>.log`):

- `scripts/schedule.py add <name> <when> <command> [arg ...]` — adding an existing name replaces it. `<when>`:
  `+5m` / `+2h` / `+1d` (once, from now), `21:45` (once, next 21:45), `2026-11-20@05:00` (once, that date),
  `daily@17:00`, `mon,wed,fri@05:00`. A one-time job removes itself after it ran.
- `scripts/schedule.py list` — every scheduled job (`fr` included), `(NOT LOADED)` = plist there but launchd doesn't run it.
- `scripts/schedule.py rm <name>`

1. **Command** = a script that boots its own instances and needs no LLM:
   - catch-up → `scripts/catchup_all.sh` (name `catchup`)
   - boot → `scripts/boot.sh <indices of scripts/accounts.py boot>` (or the named accounts' indices, boot skill step 1)
   - fr / tc → `scripts/fr_all.sh` (name `fr`; already scheduled Wed/Thu/Fri 04:30 — exits on its own outside a round)
   - anything else (dailies, relics alone, poseidon, …) has no self-booting runner: say so in one line and ask Nick
     whether to write one (copy `catchup_all.sh`'s boot part) — never schedule `claude -p` without his OK (token cost).
2. **Time** is Mac local (UTC+7). Game times are UTC (game day starts 05:00 UTC = 12:00 local) — convert, and say both.
3. **Sleep:** a Mac asleep at that time runs the job when it next wakes. A real wake needs
   `sudo pmset repeat wakeorpoweron <days> <HH:MM:SS>`, but pmset has ONE repeat slot, used by fr (04:29 Wed/Thu/Fri) —
   setting another replaces it. Tell Nick instead of changing it. Lid closed = no run.
4. Confirm with `scripts/schedule.py list`, log the action (CLAUDE.md "Action log"), add a `passive:` row to
   `docs/untested.md` for the first scheduled run.

Report: name, local + UTC time, days, command, log file.
