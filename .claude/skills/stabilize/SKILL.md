---
name: stabilize
description: Bring Nick's Mini Heroes MuMuPlayer instances to a clean main screen - start the instances, restart the game, tap Start, close every event popup (ticking "Do not remind me today" first) and tile the windows. Use for "stabilize <names>/all [except X]".
---

# Stabilize

All of it is `scripts/boot.sh` (start instance → restart game → Start → `stabilize.py` tick + X → `layout.js`).
`stabilize.py` also checks the account (Nick, 2026-10-31): top-right ID must be the account file's `game_id`; if not and
the file has `server:` it switches via ☰ → Settings → Server → `S<server>` row → Confirm (Kong: S220, not S288 MRKONG II).
"wrong account … stop" = no `server:` set / row not visible → report, never run tasks on the wrong account.

1. Pick MuMu indices: `"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all` lists index/name/state.
   "all" = the accounts in `accounts/*.yaml` (`mumu_instance:`), never every MuMu instance; names → their index;
   drop any "except" names. Skip ones already on a clean main screen, then run `layout.js` once (no ONLY) over all.
2. In `~/projects/chidojiro/miniheroes-auto`: `scripts/boot.sh <index>...` (timeout ~3 min).
   It restarts the game, so anything open (fight, menu) is dropped — that's what makes it reach the main screen.
3. Per line: `ready (stable …)` = done. `popup-stuck` / `*-timeout` → screenshot that serial
   (`D=<serial> python3 scripts/tap.py -w 270 -o /tmp/st.png`), close the popup by hand (tick "Do not remind me today"
   first, then X — some popups have a white X outside the frame, e.g. Tiger's "Stargems Running Out!"), report it.
4. Layout only runs for >1 instance and skips `accounts/layout.yaml` `exclude`; with one instance run
   `osascript -l JavaScript scripts/layout.js` if Nick asked for layout.
