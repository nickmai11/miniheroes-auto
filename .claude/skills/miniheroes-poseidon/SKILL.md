---
name: miniheroes-poseidon
description: Run Mini Heroes: Magic Throne Tribe → Poseidon's Ruins - spend all 3 attack attempts on the lowest-CP enemy ship still afloat (switch target if that player is already being attacked), on Nick's MuMuPlayer accounts via ADB or computer use.
---

# Mini Heroes Poseidon's Ruins

Use when Nick asks for "poseidon", "Poseidon's Ruins" or "plunder" on a Mini Heroes account.

1. In `~/projects/chidojiro/miniheroes-auto`, read `CLAUDE.md`, `scripts/doc.sh Poseidon` (that section
   of `docs/ui-routine.md`), and `accounts/<account>.yaml`.
2. **Script first (no LLM):** `scripts/boot.sh <idx>...` (if not running; close event popups), then
   `scripts/poseidon.py <serial> <serial> ...` — all accounts in parallel; same-tribe accounts never hit the same
   ship at once (per-ship locks). One line per fight, last line per account `attempts 0: W wins, L losses`.
   Exit 1 → that account's `/tmp/miniheroes-poseidon-out/<serial>/v_poseidon.png`; finish it by hand (steps 3–4 below).
   UNTESTED on a device (written 2026-10-28) — watch the first run.
   By hand: connect (ADB route: see "ADB alternative" in `docs/ui-routine.md`), then Tribe → Poseidon's Ruins → **Enemies** tab.
3. Scan the whole enemy list (scroll to the bottom). Target = lowest-CP ship with at least one **red** heart.
4. Attack until **Attack Attempts** = 0: tap the ship → *Plunder* → Attack → Start → Victory → dismiss.
   Verify the attempts counter dropped after each fight. Keep hitting the same target while it has red hearts;
   once it's sunk (or being attacked by someone else), pick the next-lowest-CP ship with red hearts.
5. Report: target(s) (name, CP), wins/losses, attempts used.

## Hard rules

- Only the free attempts shown on screen. Never buy attempts, never Contribute, no gems.
- Player being attacked (crossed swords on the ship, a "being challenged" toast, or Start does nothing on the lineup): back out and pick the next-lowest ship with red hearts.
- Screenshot before each target pick and counter check; chain only fixed navigation taps with `--until` (CLAUDE.md). Unexpected screen → stop and report.
