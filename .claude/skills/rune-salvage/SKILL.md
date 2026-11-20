---
name: rune-salvage
description: Mini Heroes: Magic Throne Rune Salvage event (event hub tab) - disassemble Mythic runes with Select All up to the event's 60 cap and claim the milestone chests, on Nick's MuMuPlayer accounts via ADB (scripts/rune_salvage.py). Use for "rune salvage" / "rune savage" / "disassemble runes".
---

# Rune Salvage

Use when Nick says "rune salvage" (or "rune savage"). Doc section: `scripts/doc.sh "Rune Salvage"`.

1. Accounts: the ones named ("group 1/2" → `accounts/groups.yaml`), else `scripts/accounts.py rune_salvage`. Kong II
   only when named. Boot first: `scripts/boot.sh <idx>...`.
2. Per account, in parallel, each in its own cwd: `D=<serial> scripts/rune_salvage.py <account>` from the main screen.
   It opens the event hub → Rune Salvage, then Select All → Disassemble → Confirm (Tip count = selection) in batches
   of up to 20 until "Selected: 0/0" (60 per event, or no Mythic rune left), claims the red-dot milestones
   (10/20/30/45/60, free) and goes back to the main screen. Rune choice is Select All, always (Nick 2026-11-20).
   Last line `DONE disassembled N/60, milestones claimed [...]`; `SKIP no Rune Salvage event` = event not on.
   Exit 1 → read `v_rune_salvage.png` and report; never disassemble by picking tiles.
3. When the task is done: `mumu-cli config all --setting '{"maxFpsLimit":60}'`.
4. Report per account: disassembled count (before → after), milestones claimed, anything skipped.
