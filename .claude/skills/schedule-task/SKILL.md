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

1. **Command** = Claude runs the task (Nick 2026-11-28: every schedule, so a failure gets handled, not just logged):
   `scripts/claude_job.sh "<the task as Nick typed it, + its options>"` — one-shot headless `claude -p`, exits when
   done, its report → the job's log. Name the script in the task when there is one, e.g.
   - catch-up → `"catch-up all: run scripts/catchup_all.sh; handle leftovers"` (name `catchup`)
   - fr / tc → `"fr all: run scripts/fr_all.sh …"` (name `fr`, Wed/Thu/Fri 04:30)
   - boot, dailies (`scripts/dailies_all.sh`), anything else → the same form.
     Not for non-game jobs (`web`).
2. **Time** is Mac local (UTC+7). Game times are UTC (game day starts 05:00 UTC = 12:00 local) — convert, and say both.
3. **Sleep:** a Mac asleep at that time runs the job when it next wakes. A real wake needs
   `sudo pmset repeat wakeorpoweron <days> <HH:MM:SS>`, but pmset has ONE repeat slot, used by fr (04:29 Wed/Thu/Fri) —
   setting another replaces it. Tell Nick instead of changing it. Lid closed = no run.
4. Confirm with `scripts/schedule.py list`, log the action (CLAUDE.md "Action log"), add a `passive:` row to
   `docs/untested.md` for the first scheduled run.

Report: name, local + UTC time, days, command, log file.
