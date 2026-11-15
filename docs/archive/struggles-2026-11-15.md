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
| 12 | tribe request (all 11) | `request NOT SENT (cooldown ~1:15: sent < 6 h ago)` — last night's catch-up sent them ~07:45; `tribe_chat` at 13:58: sent on Cmajor, Chloe, Kong (`request sent (cooldown 05:59:59)`); the other 8 instances had been stopped by then (#15) | ❓ catch-up timing |
| 13 | arena (Cmajor) | attacked **Gambl3r** = Chloe (renamed from 🔥Zues🔥, roster still had the old name): today 12:28, and 5× on 11-14 | ✅ `tribe_peakaboo.txt` + `own_accounts.txt` (Chloe was missing there) say Gambl3r (Nick) |
| 14 | gate (Kong II) | after the run, `no button 'Sweep' on screen`; the runner's retry swept (`['sweep']`) | ❓ one-off, retry covered it |
| 15 | tribe_chat (8 accounts) | Bino, fGotten, Dino, Dminor, Tiger, xFaktor, Kratos, Boudior instances were stopped before 13:58 (`device unreachable`) → their requests not sent; not re-booted for it | ❓ Nick closed them? |

## Catch-up 18:52 (game day 2026-11-15, Sunday)

Source: `/tmp/miniheroes-2026-11-15-18/*.log` (Chloe's first part: `chloe.part1.txt`), `/tmp/miniheroes-relic/*`. 11 accounts, all `exit 0`, no helper, no paid action; relics 11× `exit 0`, shovels 0. Storm `Coming Soon` → skipped on all.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 16 | arena, veins_forge (Chloe) | After `fishing_auto` every tap was ignored (Match, Divine Weapon; ×2 each), screen = plain main screen, banners still rotating. My own Match tap via `tap.py` also did nothing. `boot.sh 6` (game restart) → taps work; resumed from `arena`, all OK | ❓ one-off, not understood (input dead, render alive) |
| 17 | tribe_chat (fGotten) | `request NOT SENT (cooldown 06:00:00: sent < 6 h ago)`: a 6:00:00 timer at the first read = sent a second earlier (its last send was the 07:45 catch-up, > 6 h); `checklist.py` already counted it as sent | 🧪 `tribe.py`: ≥ 05:59:00 at the first read → `sent` |
| 8 | events (Boudior, Dino) | Dragon Temple dot again (`banner Dragon Temple`, `1d16h`, `16h 56m`, `11h 57m`, `Unlocks in 16h 57m` = its dot read on rotating cards) → MANUAL, no helper sent | ❓ (see above) |

## Poseidon 20:47 (game day 2026-11-15, Sunday)

Source: `/tmp/miniheroes-poseidon-out/*`, poseidon.py output in the session.

| # | Task | What went wrong | Status |
| --- | --- | --- | --- |
| 18 | poseidon (Tiger, Kratos, Boudior) | Their tribe's Ruins was in the **registration phase** ("Registrating 15:10:32", Match Found, Deploy): no map, no attempts → `waited 15s for 'Attack Attempts'` stop ×3, left on that screen | ✅ `poseidon.py`: "Registrat" → back to main, exit 0; live-tested on all 3 |
