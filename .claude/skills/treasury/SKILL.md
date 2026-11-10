---
name: treasury
description: Mini Heroes: Magic Throne Golden Woods → King's Treasury - spend the Treasury Keys flipping cards until each level's Grand Prize, level after level, picking the Level 3/5/7 prize as it unlocks (scripts/treasury.py). Use for "treasure event" / "king's treasury" / "flip the cards".
---

# King's Treasury (Golden Woods event)

Use when Nick says "treasure event" / "king's treasury" / "flip the treasury cards". The dailies run it too: `daily.py`
step `treasury`, right after `events` (Nick 2026-11-10).

1. Accounts: the ones named ("group 1/2" → `accounts/groups.yaml`), else `scripts/accounts.py treasury`.
   Boot first: `scripts/boot.sh <idx>...`.
2. Per account, in parallel, each in its own cwd: `D=<serial> scripts/treasury.py <account>` from the main screen. It opens the
   event hub → Golden Woods → King's Treasury and loops until the keys are 0:
   - new level: prize pick (only on entering Level 3, 5 and 7: that level's newly unlocked prize; the pick sticks, so
     from Level 7 on the Level 7 prize stays the target — Level 10/15/20 prizes are ignored), then the free
     **Shuffle Cards**;
   - flip cards (1 key each) until the Grand Prize card → GO → "proceed to the next level?" Tip (ticks "Do not remind
     me today", Confirm). Leftover cards on the old level are lost — Nick's rule: move on at the Grand Prize;
   - at 0 keys: claims the point milestones with a red dot (50/100/…, free).
     Last line `DONE level N, keys 0, flips F`. Exit 1 → read `v_treasury.png` and report.
3. Cards are flipped in random order (Nick 2026-11-09). Out of keys = the "Insufficient Required Items" toast →
   `DONE … (flip refused)`.
4. `--max-keys N` caps the flips (testing). Keys come from Golden Woods → Exploration Quest (collected by the
   dailies' `events` step), so run this after the dailies.
5. Report per account: level reached, flips, prizes picked, anything skipped.
