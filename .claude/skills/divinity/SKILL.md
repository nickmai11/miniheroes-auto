---
name: divinity
description: Mini Heroes: Magic Throne divinity upgrade - every hero after the first N (hero list order), Hero → Artifact, upgrade each of the 6 divinity badges (2 purple, 2 gold, 2 red) to the level in accounts/divinities.yaml (1 unit = 50 levels), only listed names, on Nick's MuMuPlayer accounts via ADB (scripts/divinity.py). Crystals + gold only. Use for "upgrade divinities <account> from the Nth hero".
---

# Divinity upgrade

Use when Nick says "upgrade divinities for <account> (from the Nth hero)". First done on Kratos 2026-11-12 (heroes
7–68, 142 upgrades until red and gold crystals ran out).

1. Targets: `accounts/divinities.yaml`, sections `red` / `purple` / `gold`, `<name>: <units>`, **1 unit = 50 levels**
   (Nick). Blank or missing = **not upgraded** (Nick: "shouldn't upgrade what not listed" — Basic / Intermediate /
   Advanced HP/ATK aren't listed). Red names = the catalog (`../nextjs-fullstack/scripts/upsert-divinities.sql`).
2. Boot the account (`scripts/boot.sh <idx>`); main or Hero screen.
3. `cd <scratch>; D=<serial> scripts/divinity.py --keep <N-1>` (default 6) in the background, Monitor its log for
   `out of|row end|stop|Traceback`. Per hero: all 6 badges to target, then the next card, **on the Artifact tab only**
   (no Attribute round trips — Nick). ~30 s per hero with upgrades.
   - Stopped? Fix, then **`--here`** = resume at the selected hero (closes a left-open popup/dialog) — never walk
     from card 1 again (Nick).
   - A colour out of crystals (cost row `have/need` short) → that colour is skipped for the rest of the run
     (`out of red crystals -> no more red upgrades`); gold out → stop. Locked badges (padlock / "Lv.100") are skipped.
   - **Bone Archer is excluded** (dailies hero, Nick).
4. Done = `row end: K heroes done`. Upgrading moves a hero left in the row, so some heroes show twice (read-only
   second pass, nothing skipped).
5. Report per account: badges upgraded (hero, colour, name, from → to), anything short of its target (crystals out:
   which colour, where it stopped), locked badges.

Rules: never Reset (free but undoes upgrades); never upgrade an unlisted badge; confirm a Quick Level Up only when
its "Lv.b" ≤ the target. Mechanics: `scripts/doc.sh Divinities`.
