---
name: miniheroes-match
description: Run the Mini Heroes: Magic Throne Match (Arena) daily - crash the highest-CP opponent not in Nick's tribe until all free tickets are used, on his MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Match dailies

Use when Nick asks for "match dailies", "arena", or "crash" on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, the **Match (Arena)** section of
   `docs/ui-routine.md`, and `accounts/<account>.yaml` (`missions.match`).
2. Connect (ADB route: see "ADB alternative" in `docs/ui-routine.md`).
3. **Read the full tribe member list first.** Tribemates appear as opponents.
4. Loop until tickets = 0: open Challenge, pick the highest-CP **Crash** row not on the roster,
   crash, dismiss, verify the ticket count dropped.
5. Report: tickets before/after, each opponent crashed (name, CP), match points before/after,
   and any tribemates skipped.

## Hard rules

- Never attack a tribe member. If unsure, tap the avatar and read `Tribe:` on the profile.
- Only free tickets: never tap `+` (buy tickets) or Refresh. No gems.
- Only blue **Crash** rows; no yellow **Challenge** fights unless Nick asks.
- Screenshot before every tap; never chain taps. Unexpected screen → stop and report.
