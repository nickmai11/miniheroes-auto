#!/bin/bash
# Scheduled job = Claude runs the task (Nick 2026-11-28: every schedule), so a failure gets handled, not just logged.
# usage (via schedule.py): scripts/claude_job.sh "<task, as Nick would type it>"   one-shot: exits when done.
# Output (Claude's final report) -> logs/launchd-<name>.log.
exec claude -p "Scheduled run, unattended: nobody can answer or approve. Follow CLAUDE.md and the task's skill, handle failures yourself, finish, then report. Task: $*" --dangerously-skip-permissions
