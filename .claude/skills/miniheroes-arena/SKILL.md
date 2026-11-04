---
name: miniheroes-arena
description: Run the Mini Heroes: Magic Throne Arena daily (main-screen "Match" icon) - claim Ranking Rewards gift boxes, then attack the topmost attackable opponent (Crash, or Challenge with a lower CP than ours) not in Nick's tribe (last row = bot, always attackable) until all free tickets are used, on his MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Arena dailies

Use when Nick asks for "arena", "match", or "crash" on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `scripts/doc.sh Arena` (Arena section
   of `docs/ui-routine.md`), and `accounts/<account>.yaml` (`missions.arena`).
2. Connect (ADB route: see "ADB alternative" in `docs/ui-routine.md`).
3. **Use the saved tribe roster** (`accounts/tribe_<name>.txt`; members are fixed). Read it in-game only if the file is missing, then save it.
4. **Run `D=<serial> scripts/daily.py <account> arena`** (opens Arena, claims Ranking Rewards gift boxes, runs `scripts/arena.py`, back to main). Exit/FAIL →
   do the loop by hand from its screenshot: Loop until tickets = 0: open Challenge, pick the **topmost** row not on the roster (blue **Crash**, or yellow **Challenge** only when its CP is **below ours** — Nick 2026-11-04; ours = the pinned own row at the bottom of the Arena list; a Challenge is a real fight: Start → result → dismiss)
   (the **last row is a bot — always attackable**, use it when nothing above qualifies),
   attack, dismiss, verify the ticket count dropped.
5. Claim any reached (glowing) weekly win chest: done by `daily.py <account> arena` at the end of the same visit (Arena doc step 6).
6. Report: claims, opponents attacked (name, CP, crash/challenge, Victory/Defeat) and any tribemates skipped.

Also triggered mid-dailies by a "Match attempts full" popup: Confirm, exhaust tickets, then resume the interrupted daily.

## Hard rules

- Never attack a tribe member (the last-row bot is never one). If unsure, tap the avatar and read `Tribe:` on the profile.
  Exception: accounts with `arena.attack_tribemates: true` (Dino, Bino, Dminor — Nick, 2026-11-04) may crash tribemates, but never Nick's own accounts (`accounts/own_accounts.txt`).
- A yellow **Challenge** only against a lower CP than ours; never a stronger opponent.
- Only free tickets: never tap `+` (buy tickets) or Refresh. No gems.
- Screenshot before each target pick and counter check; chain only fixed navigation taps with `--until` (CLAUDE.md). Unexpected screen → stop and report.
