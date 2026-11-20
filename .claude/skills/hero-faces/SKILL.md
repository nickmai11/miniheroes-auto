---
name: hero-faces
description: Mini Heroes: Magic Throne hero faces - learn new heroes and new skins into the face library (scripts/heroes/) and name hero cards by their face, on Nick's MuMuPlayer accounts via ADB (scripts/hero_faces.py). Use for "learn faces", "new hero", "new skin", "game update", a climb_stage "unrecognised faces" / "not found by face" line, a `who` "?" card, or any hero card a script or helper can't name.
---

# Hero faces

Nick, 2026-11-14: heroes are recognised by their face, never by grid position, and new heroes / new skins come from
time to time — a face nobody knows is learnt, never guessed. Library: `scripts/heroes/<id>.png` (id = the name in
lower_snake case, skins `<id>_2`, `_3`…; 114 faces / 69 heroes on 11-14). How it works + numbers:
`scripts/doc.sh "Hero faces"`.

## When a face isn't known

- **Stage climb** learns by itself: `unrecognised faces … -> learn the hero list (new skin?)` or `heroes not found by
face … -> learn` → it runs `learn` on that account and reads again. Still unknown after that (`--record` exit 1 "not 5
  recognised heroes", swap / `--apply` exit 2) → the steps below on that account, then the climb command again.
- **A helper or a screenshot** shows a hero card you can't name → don't guess from its looks: steps below, then `who`.
- **Nick says new hero / new skin / game update** → steps below with `--all` on every account.

## Steps

1. Accounts: the one where the face showed up; "all" → `scripts/accounts.py hero_faces`. Boot them:
   `scripts/boot.sh <idx>...` (main screen, 30 fps).
2. Per account, in parallel, only from the main screen: `D=<serial> python3 -c "import flow; print(flow.home())"`
   must print `True`, else skip that account and report it (Cmajor 11-14: learn started off the main screen and its
   taps fused a relic). Then `D=<serial> scripts/hero_faces.py learn` — `learn --all` after a game update or any change
   to the matching code. View-only (hero cards + the All filter, never a button); ~4–5 min per account (mostly waiting for the list to stop
   gliding after each scroll), `--all` ~7 min.
   `learn` taps only the cards it isn't sure of (score < 0.75) and checks them against the name on screen.
3. Read its lines:
   - `<Name>: saved <id>.png` = a new hero; `(new skin / closer variant; …)` = another look of a known hero. Both wanted.
   - `MISREAD <Name> as <id>` = a face was read as another hero; it was saved under the right name. Run `learn --all`
     on that account again: 0 misread = fixed; misreads again → stop and report the ids (the matcher needs work).
   - `name unchanged … skipped` / `lost my place in the list` → run `learn` on that account once more.
   - Last line `N cards, M misread, K faces`: N ≈ that account's hero count.
4. Check a screen: hero list open → `D=<serial> scripts/hero_faces.py who` prints `x y name score best-other` per card;
   an empty name = still unknown.
5. Log every run (CLAUDE.md "Action log"); report new ids, misreads, skips. The faces are repo files: say which are new,
   commit only when Nick asks.
6. Done: `mumu-cli config all --setting '{"maxFpsLimit":60}'`.

## In code

`hero_faces.ident(hero_faces.face(im, x, top))` → `(id or '', score, best other)` for the card at column centre `x`
whose top edge is `top` — hero list or battle setup (the green check / padlock are masked out). Use it instead of grid
positions or one-hero templates in new scripts; on `''` learn once and retry, like `climb_stage.relearn()`.
