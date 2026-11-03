---
name: miniheroes-realm
description: Run Mini Heroes: Magic Throne Tribe → Floating Realm (cross-server event, every 2 weeks, battle Tue/Wed/Thu 10:00–22:00 UTC) - spend all stamina exploring (claim treasures, crush/attack monsters, Monster Lair core stakes, climb floors by kills or Treasure Maps per Nick's map strategy), on his MuMuPlayer accounts via ADB.
---

# Mini Heroes Floating Realm

Use when Nick asks for "floating realm", "realm" or "use up the stamina" on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `scripts/doc.sh "Floating Realm"` and
   `accounts/<account>.yaml`.
2. **Script first (no LLM):** `scripts/boot.sh <idx>` (main screen), then `D=<serial> scripts/realm.py <account>`.
   It explores until stamina < the explore cost, claims the reached **Target** stamina milestones, then goes back to the main screen. One log line per fight, Lair, or
   floor decision, plus `done: N explores, F<floor>, points A -> B`. It logs to `logs/<account>/<game day>.log` itself.
   Outside a battle round it prints `no battle round now` and does nothing.
   All accounts: `scripts/fr_all.sh` (boot + realm.py on each, parallel); launchd runs it Wed/Thu/Fri 04:30 local
   (`com.nickm.miniheroes-fr`, log `logs/launchd-fr.log`).
3. Exit 1 → read `v_realm.png` and the `STOP:` line, then finish by hand with the doc's rules. Typical stops:
   - an unknown event (map it in the doc first);
   - Defeat;
   - Explore ignored 3×. This means the connection to the account was lost: report it and don't keep tapping.
4. Report: points before → after, floor reached, fights (won/lost), Lair stakes, maps used, and anything stopped.

## Hard rules

- Never tap the stamina **+** or buy a Pack (gems/$).
- Treasure Maps: follow the doc's map strategy (5 kept for Thursday's F2→F3). Never spend one outside it.
- Fights: always Attack, whatever the CP (Nick, 2026-11-03). After a Defeat, always **Mark** it for tribe assist (Nick).
  realm.py looks for a `Mark…` button (screen not seen yet) and stops if there isn't one.
