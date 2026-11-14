# Struggles — catch-up 06:31 + climb stage (game day 2026-11-13, Saturday)

Source: `/tmp/miniheroes-2026-11-14-06/*.log`, `logs/{kratos,boudior,tiger}/2026-11-13.log` `[climb_stage]` lines.
Status: ✅ fixed · 🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-14.

| #   | Task                   | What went wrong                                                                                                                                                      | Status                                                                                         |
| --- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | climb_stage swap cap   | `swaps` was in memory per call and keyed by stage only → cap never hit across 8-min calls; Boudior swapped 4x on 4-15                                                | ✅ `/tmp/climb_stage_swaps.json`, key `<account> <stage>`; fired live (Boudior exit 2 at 4-15) |
| 2   | climb_stage swap (Kr)  | swap at 6-26 died after the fresh setup: `TIMEOUT waiting for 'Start'` after tab tap 540,1088; yaml not rewritten, tab state unknown → Kratos left on setup for Nick | ❌                                                                                             |
| 3   | tribe_chat (Dino, Dm)  | `NOT SENT (cooldown 05:59:59: sent < 6 h ago)` — a timer that fresh = the request just went out; the label is wrong (also feeds a MANUAL in daily.py)                | ❌ treat a timer ≥ 05:59:00 as sent                                                            |
| 4   | tribe_chat (Kratos)    | `NOT SENT (no cooldown timer after 2 taps; rows 2/4, 6/8)` — Request grey not checked by screenshot (untested.md row 2026-11-13)                                     | ❓                                                                                             |
| 5   | boot.sh (Kong, Kratos) | no "ready" line printed for 2 of 11 instances; both were fine (stabilize.py with NAME: right account, 0 popups)                                                      | ❌                                                                                             |
