# Struggles — dailies 12:06 (game day 2026-11-15, Sunday)

Source: `/tmp/miniheroes-2026-11-15/*.log`, `logs/*/2026-11-15.log`. Status: ✅ fixed · 🧪 fixed, waiting for a live test (`docs/untested.md`) · ❌ open · ❓ needs Nick. Last updated: 2026-11-15.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 1 | boot (Kong) | `popup-stuck (popup not closable)`; screen = the game's Start screen (Kong was already running before boot). `boot.sh 5` again → ready, 1 popup closed | ❓ one-off |
| 2 | fishing (Kratos) | 0 scrolls → bought 1 pack (50 gems, 0 → 5 behind the popup), the (540,240) close tap was ignored → `FAIL pack popup still open`; the retry refreshed with the bought scrolls (5 → 4), orders 4/4/3 | 🧪 up to 2 close taps |
| 3 | arena2 (Bino) | `tickets did not drop (2 -> 2)`: a Crash tap didn't register; the runner's retry crashed 2, tickets 0 | ❓ one-off, retry covered it |
| 4 | gate (Tiger) | fight ended on the Victory popup, Confirm tapped while it slid in → `waited 10s for 'Chances left today'`, then `lost the main screen` → runner stopped. I tapped Confirm (1 chance left), re-ran `daily.py tiger gate …` → sweep, rest OK | 🧪 Confirm ×3 until the counter reads |
| 5 | recruit (Boudior, Tiger) | no-pass Common Recruitment ad force-closed at 47–48 s ("Close it" / Back) → no reward → `waited 15s for '^Confirm$'`; retries ran 71–78 s and paid | 🧪 `watch_ad` force-close from 60 s |
| 6 | events (Cmajor, fGotten) | `hub_tabs()` missed the Limited Recruitment tab once (Dino, Kratos, Boudior read it) → Hero Trial unclaimed, `MANUAL banner Limited Recruitment` | ✅ tabs re-read after the tab switch; re-run claimed Hero Trial on both |
| 7 | events (fGotten) | Weekly Event = Artifact Wish: "Earn 6000 Points" (6019/6000) unclaimed — the runner only does Wish Merchant. Claimed by hand (round 1/5 → 2/5), dot gone | ❌ not scripted (doc'd in ui-routine Events) |
| 8 | events (6 accounts) | Dragon Temple banner dot left (unmapped PvP ladder, tickets). Timer-named entries (`banner 1d23h`, `23h 8m`, `16h 27m`) = its dot matched to a rotating card's label | ❓ Nick: should the dailies do Dragon Temple? |
| 9 | weekly honor (xFaktor) | OCR read the medal cost `177 \|210` (pipe for slash) → `costs unreadable` FAIL ×2 | ✅ `[/\|]`; re-run: `honor: stop: … medals 177/210`, 140 pts |
| 10 | weekly statue (Bino, Dminor) | Vision garbles the Power Required bar (`1143737/\|82384`) → FAIL ×2, the Lucky Star swap + claims after it never ran | ✅ unreadable bar = short, the pass goes on; re-run 170 pts both |
| 11 | weekly statue (Dino, Boudior, Kratos) | `Level Up did not raise the level` with the bar read as full — the read is unreliable (see 10) | ❌ statue = one of the 2 unscripted daily rows |
| 12 | tribe request (all 11) | `request NOT SENT (cooldown ~1:15: sent < 6 h ago)` — last night's catch-up sent them ~07:45; re-sent with `tribe_chat` once the timers ran out (13:57) | ❓ catch-up timing |
