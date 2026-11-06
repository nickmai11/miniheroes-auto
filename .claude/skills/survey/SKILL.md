---
name: survey
description: Mini Heroes: Magic Throne in-game survey mails (Google Form asking for the character ID) - submit it once per account with neutral answers from the Mac (scripts/survey.py), no per-account tapping. Use for "do the survey (mail)".
---

# Survey mail

Use when Nick says "do the survey" / "fill out the survey" for an E-mail like "2nd Anniversary Survey".

1. Stabilize the accounts (`scripts/boot.sh <idx>...`), then on ONE account: ☰ `994,1625` → E-mail `820,820` →
   the survey row → "Click here to fill out the survey" link. It opens the Android browser.
2. `scripts/survey.py <that serial> --dry-run` reads the URL from the browser intent and prints the planned answers
   (text → `n/a`, scale → middle, choices → the "fine / no change" option, else the first, ID → `game_id`). Show Nick
   the plan if the questions look unlike a plain feedback form. Then `scripts/survey.py <serial or url> [account ...]`
   submits for every `accounts/*.yaml` with a `game_id`; `<name> <id>: submitted` per account, `NOT confirmed` →
   read `v_survey_<name>.html`.
3. Android Back ×2 on that instance returns it to the game. Report per account; note the mail stays unread
   in-game on the others (no reward is tied to it as far as seen, 2026-11-06).
