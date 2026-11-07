# Struggles — catch-up 2026-11-07 06:45 (game day 2026-11-06, 9 accounts)

Source: runner logs `/tmp/miniheroes-2026-11-07-06/*.log`, Kong `v_storm.png`. Status: ✅ fixed · 🧪 fixed, waiting for a live
test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-07.

| #   | Task                       | What went wrong                                                                                                                                                                                                             | Status                                                                                                         |
| --- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| 1   | Storm (Kong, Cmajor)       | Badge level "3" (King +3) never read by the 2× crop OCR → `rank unreadable with a max rank set` (cap King +10): Kong FAIL after +2 then 0 matches on retry (2/5 tickets left), Cmajor 0 matches (5/5 left) — both logged OK | ✅ `cur_rank` falls back to a tight crop at 3×/4×; re-runs read +3, Kong +3→+5, Cmajor +3→+8, all tickets used |
| 2   | Arena ranking (Aminor)     | Ranking-reward popup OCR'd as "CongratulationSudss" → wait for `Congratulations` timed out → FAIL; retry OK (reward was already claimed on the 1st try)                                                                     | 🧪 regex `Congratulation` (`docs/untested.md`)                                                                 |
| 3   | Boot (Kong)                | Instance on another account again (stabilize `account switched`, 2nd day running)                                                                                                                                           | ❓ who switches it? stabilize fixes it each time                                                               |
| 4   | Fishing (Bino, Chien Than) | `AUTO STOPPED, bread 0–1/100` at the end                                                                                                                                                                                    | ❓ same as 11-06 #3                                                                                            |

Open detail: a storm "OK" with `rank unreadable … no matches` hides unused tickets — the runner should count it as a FAIL. Not changed (needs Nick's OK).

Everything else: 9 × 13 OK + pet_check SKIP (Mon–Wed only), no helper, no paid action, 0 popups stuck at boot.
