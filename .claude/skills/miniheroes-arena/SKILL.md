---
name: miniheroes-arena
description: Run the Mini Heroes: Magic Throne Arena daily (main-screen "Match" icon) - claim Ranking Rewards gift boxes, then crash the topmost attackable opponent not in Nick's tribe (last row = bot, always attackable) until all free tickets are used, on his MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Arena dailies

Use when Nick asks for "arena", "match", or "crash" on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `scripts/doc.sh Arena` (Arena section
   of `docs/ui-routine.md`), and `accounts/<account>.yaml` (`missions.arena`).
2. Connect (ADB route: see "ADB alternative" in `docs/ui-routine.md`).
3. **Use the saved tribe roster** (`accounts/tribe_<name>.txt`; members are fixed). Read it in-game only if the file is missing, then save it.
4. **Run `D=<serial> scripts/daily.py <account> arena`** (opens Arena, claims Ranking Rewards gift boxes, runs `scripts/arena.py`, back to main). Exit/FAIL →
   do the loop by hand from its screenshot: Loop until tickets = 0: open Challenge, pick the **topmost** **Crash** row not on the roster
   (the **last row is a bot — always attackable**, use it when nothing above qualifies),
   crash, dismiss, verify the ticket count dropped.
5. Claim any reached (glowing) weekly win chest: `daily.py <account> arena_claims` (Arena doc step 6).
6. Report: claims, opponents crashed (name, CP) and any tribemates skipped.

Also triggered mid-dailies by a "Match attempts full" popup: Confirm, exhaust tickets, then resume the interrupted daily.

## Hard rules

- Never attack a tribe member (the last-row bot is never one). If unsure, tap the avatar and read `Tribe:` on the profile.
- Only free tickets: never tap `+` (buy tickets) or Refresh. No gems.
- Only blue **Crash** rows; no yellow **Challenge** fights unless Nick asks.
- Screenshot before each target pick and counter check; chain only fixed navigation taps with `--until` (CLAUDE.md). Unexpected screen → stop and report.
