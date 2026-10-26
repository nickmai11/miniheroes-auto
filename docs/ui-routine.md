# UI routines

All coordinates are in the **MuMu Android Device** game window's full-resolution frame
(704×1289), as used by `computer_app_click` on that window (ADB uses device coords — see below). Instance window ids change after
every restart — get a fresh one with `computer_app_list_windows`.

## ADB alternative (no computer use)

Works without computer-use tools. Device frame is **1080×1920**; the rest of this doc uses
window coords (704×1289) — with ADB use the device coords below (verified 2026-10-26). Get the instance's current ADB port from
`"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all` (ports change).

```
adb connect 127.0.0.1:<port>
adb -s $D exec-out screencap -p > s.png   # read it before every tap
adb -s $D shell input tap X Y
```

Device coords (Land of Trials): safe dismiss `(540,120)`; sweep dialog ✕ `(972,572)`;
Sweep `(540,1372)`; Tip Confirm `(540,1162)`. List scrolled to bottom (swipe `540,1600→540,400`):
GO Battlefield `(870,630)`, Forest `(870,1016)`, Temple `(870,1402)`, Gem Mine `(870,1786)`.
List at top (swipe `540,500→540,1500`): GO Abandoned Mine `(870,540)`, Forest `(870,1310)`,
Temple `(870,1696)`.

## General gotchas

- **Taps during animations are ignored.** Popups slide in; after opening one, take a screenshot,
  then tap. Always confirm the result with a screenshot — never chain taps blindly.
- **Each free sweep = two taps** (a paid one = four: Sweep → Confirm → Sweep → dismiss): `Sweep`, then dismiss the *Congratulations* reward popup (it also
  auto-closes after ~3 s). The tap that looks "ignored" right after a sweep is usually the one
  that dismissed the popup.
- **Safe dismiss tap:** `(352, 140)` — the screen title area; does nothing if no popup is open.
  Don't dismiss by tapping near the bottom: it can hit a list item behind the popup.
- Gem balance appears top-left while a sweep dialog is open (e.g. `5995`). Record it before
  and after.

## Starting the game

1. In **MuMuPlayer**, press ▶ on the instance row (if not running). Wait for the Android home
   screen.
2. Tap the **Mini Heroes** icon `(352, 190)`. Loading screen → tap **Start** `(352, 1022)`.
3. Event popups may appear on the main screen — close with their ✕ (e.g. Pet Arena close at
   `(524, 520)`), then screenshot to confirm the main screen (Adventure button bottom-left).

## Land of Trials

Path: main screen → **Adventure** `(66, 984)` → **Land of Trials** card, `GO` `(516, 306)`.

Screen header: "Free attempts refresh in: HH:MM:SS" (daily reset).

Dungeon list (scroll position = top; scroll by dragging `(352,1100)→(352,300)` to reveal Gem Mine):

| Dungeon | `GO` tap (top of list) | `GO` tap (scrolled to bottom) |
|---|---|---|
| Abandoned Mine | `(568, 390)` | – |
| Ancient Battlefield | `(570, 640)` | `(570, 448)` |
| Mysterious Forest | `(570, 892)` | `(570, 698)` |
| Moonlight Temple | `(570, 1142)` | `(570, 950)` |
| Gem Mine | – | `(570, 1200)` |

The card shows `Attempts: N` (free left) or `Remaining purchases: N` (free exhausted).

### Sweep dialog

- Shows Difficulty (keep as-is — highest unlocked, currently 35 on Cmajor), Stage Reward,
  and one of:
  - **"Challenge Attempts: N"** + plain yellow **Sweep** button → free sweep.
  - **"Remaining Purchase Attempts: N"** + **Sweep** button with a gem icon and price
    → **paid** sweep. Price escalates per dungeon per day: 80, 160, 240, … (one purchase each).
  - Tapping a paid **Sweep** opens a *Tip* popup "Spend N diamonds to purchase 1 challenge
    attempt?" → **Confirm** (window coords unverified, ≈ `(352, 790)`; device `(540,1162)`)
    only *buys* the attempt; the dialog then shows "Challenge Attempts: 1" and you tap
    **Sweep** again to actually sweep.
  - Gem Mine's reward popup animates for a few seconds; wait before dismissing.
- **Sweep** button: `(352, 932)` once the dialog has settled.
- Close dialog ✕: `(632, 408)`.

### Algorithm per dungeon

```
target = config total sweeps (free + paid)
open dungeon dialog; screenshot
done = 0
while done < target:
    screenshot dialog
    if "Challenge Attempts: N" (N>0): free sweep
    elif "Remaining Purchase Attempts":
        read gem price on button; if price > max_gem_price_per_sweep → stop, report
        tap Sweep → Tip popup (verify price) → Confirm → now "Challenge Attempts: 1"
    else: stop, report unexpected state
    tap Sweep (352,932); screenshot → expect Congratulations; tap (352,140) to dismiss
    screenshot → verify counter decreased (or switched to purchase mode); done += 1
close dialog (632,408)
```

If the config count is lower than the free attempts available, do only the configured number.
Keep track of sweeps already done today (e.g. from a previous run) — the on-screen counters are
the source of truth: free used = 2 − remaining free; paid used = 5 − remaining purchases
(Cmajor, 2026-10-26: 2 free, 5 purchasable per dungeon).

## Match (Arena)

Mapped 2026-10-26 on Cmajor via ADB. **Device coords (1080×1920)**; window coords not mapped yet.

Goal: spend every free ticket crashing the highest-CP opponent who is **not in our tribe**.

1. **Get the tribe roster first, every run** (members change). Main screen → **Tribe** `(448,1780)`
   → **Member** `(192,474)` → read all names (29/30 on Peakaboo; scroll with
   `input swipe 540 1550 540 750 1500`). Close ✕ `(972,238)`, back arrow `(98,1808)`.
   Tribemates also show up in Arena (e.g. Morrígan, Zues, Aminor on 2026-10-26), so don't skip this.
   To check a single opponent: tap their avatar in the Challenge list → profile shows `Tribe: …`.
2. Main screen → **Match** `(100,1280)` (badge = tickets left) → Arena → **Challenge** `(540,1594)`.
3. Challenge dialog: tickets `N/8` top-left. Rows, each with CP and a button at x=`866`,
   y ≈ `559, 796, 1033, 1267, 1504` (row 1–5). A 6th row can be cut off; scroll to read its CP.
   - Blue **Crash** = instant win vs. a weaker opponent (1 ticket). Use these.
   - Yellow **Challenge** = real fight vs. a stronger one. Not used.
   - Don't touch `+` (buys tickets) or **Refresh** (cost unknown).
4. Pick the highest-CP **Crash** row whose name is not on the roster → tap its Crash.
   The dialog closes and shows *Congratulations* (+40 match points, 11000 gold).
   Dismiss with `(540,120)`, confirm the ticket count dropped by 1 on the Challenge button.
5. Repeat from step 2 until tickets = 0. The opponent list changes after every crash.

Gotcha: a `swipe` once failed with `INJECT_EVENTS permission` and the game was then back on
the main screen. Screenshot and re-navigate when that happens.

## Shop freebies (red dots)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Nick explicitly allows this one Shop task:
claim the **free** red-dot items only. Every other button in the Shop costs real money ($) — never tap them.

1. Main screen → **Shop** `(100,330)` (opens on Value Pack tab).
2. **Value Pack** → *Free Benefits* row → **Claim** `(894,787)` (10 gems + 1000 gold; button
   becomes "Sold Out"). Dismiss with `(540,120)`.
3. **Hero Pack** tab `(480,1846)` → **Select Hero** `(895,420)` (red dot): just opening the dialog
   grants **20 gems**. Dismiss `(540,120)`, then close the dialog ✕ `(972,300)` **without picking a hero**.
4. Check every tab for a remaining red dot; back arrow `(92,1810)`. Shop icon's dot is gone when done.

Daily total on Cmajor: +30 gems.

## Play Pass claims (red dots)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free daily claims from cards Nick already
owns. Never tap a $ / purchase button.

1. Main screen → **Play Pass** `(100,500)`. Tabs along the bottom: Play Pass `(480,1846)`,
   Weekly Card `(648,1846)`, Monthly Card `(818,1846)`, Lifetime Card `(988,1846)`. Visit each tab with a red dot.
2. **Play Pass** tab: passive privileges, nothing to claim.
3. **Weekly Card** (bought, "Purchase to get" items ticked): tap today's highlighted **Day N** tile
   (Day 1 = `(203,1099)`; grid of 3 columns x≈203/540/877, rows y≈1099/1486) → 20 stars, tile shows "Claimed".
4. **Lifetime Card** → **Claim Reward** `(540,1658)` → 288 gems + 3 arena tickets, button turns "Claimed".
5. Dismiss every reward popup with `(540,120)`; back arrow `(92,1810)`.

Note: on 2026-10-26 opening Play Pass already showed gems 5645 → 5875 and the second currency
80 → 560 before any claim, cause unknown (an auto-credit on opening?). Record gems before opening.

## Tower of the Throne (1 daily challenge)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Goal: one challenge for the daily task,
using **only the weakest hero** (it's meant to lose; floors are ~17000K CP vs our ~6600K).

1. Main screen → **Adventure** `(100,1460)` → Tower of the Throne **GO** `(787,687)`.
   Ticket count top-left (10/day on Cmajor).
2. **Challenge** `(540,1805)` → lineup screen (5 strongest heroes pre-selected).
3. Clear the picks with the **reset ↺ button** `(1003,1084)` (top-right of the roster) — CP shows 0.
4. Scroll the roster to the very bottom (`input swipe 540 1500 540 1100 400`, repeat ~15×).
   The roster is sorted strongest → weakest: the **last hero in the list** is the weakest.
   Tap it (one hero only) and check the CP top-left (686K on 2026-10-26, a Lv.160 purple hero).
5. **Start** `(540,1808)` → *Defeat* screen. Dismiss by tapping `(540,1700)` (below the
   "Challenge again" button — never tap that). Verify tickets dropped by 1.

## Secret Sanctuary (daily sweep, free)

Mapped 2026-10-26 on Cmajor via ADB (device coords).

1. Main screen → **Adventure** `(100,1460)` → Secret Sanctuary **GO** `(787,962)` → map (e.g. "Ice Citadel").
2. **Sweep** `(540,1778)` (plain button, no gem icon) → *Tip*: "Sweep grants rewards based on last
   cleared stage (Stage 10). Cannot challenge again today." → **Confirm** `(533,1197)`.
3. *Congratulations* (gold, potions, shards…) → dismiss `(540,120)`. All stages now show flags and
   the Sweep button is replaced by "Bonus Effects Owned". Done for the day.
4. Back arrow `(92,1810)` returns straight to the main screen.

Gotcha (all modes): the back arrow `(92,1810)` sits on top of the main screen's **Recruit** button.
A back tap that lands after the screen has already changed opens Recruit. Screenshot after every
back tap; if you're on Recruit, just tap back again (never Recruit 1/10).

## Gate of Darkness (2 chances/day)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Endless-wave mode; progress carries over.

1. Main screen → **Adventure** `(100,1460)` → wait for the list to finish sliding in (a tap during
   the animation opens an item-info popup; close it by tapping `(540,1400)`) → Gate of Darkness **GO** `(787,1238)`.
2. Screen shows "Chances left today: N" under **Start Challenge** `(540,960)`.
3. **First chance — run it:** Start Challenge `(540,960)` → lineup (default top 10, keep it) →
   **Start Challenge** `(540,1806)` → *Tip* "Start challenge from Wave N?" → **Confirm** `(760,1164)`.
   **Never tap Restart** (resets wave progress).
   - **Time cap 1m30s** from Confirm. If still fighting: tap **Pause** `(866,1227)` → quit the
     battle (quit button coords not yet mapped; screenshot and pick the quit/exit option, never "restart").
   - If it ends earlier: *Victory* (kill count + rewards) → **Confirm** `(540,1406)`.
4. **Second chance — Sweep:** after a run, a green **Sweep** button appears `(938,1056)` next to
   Start Challenge. Use it instead of running again (coords from screenshot, unverified).
5. Verify "Chances left today" dropped each time.

2026-10-26: run 1 = Victory, 2287 kills, Rank 1 (114K gold, 457 silver). The second chance's state
is unknown — the screen jumped to Beast Realm mid-run (Nick may have been using the instance).

## Recruit (free summons only)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Daily: **2 Common, 1 Ancestor, 1 Artifact**, all free.

1. Main screen → **Recruit** `(96,1810)` (opens on Advanced Recruitment — skip it, it uses tickets).
2. **Common Recruitment** tab `(188,1610)` → "Chances: N" + **Free** `(540,1355)`. Tap → result cards →
   dismiss `(540,1700)` (wait ~2 s for the card flip). Do it twice. A cooldown (~5 min) shows
   between free chances; if it's on, wait it out — never pay.
3. **Ancestor Summon** tab `(896,1610)` → **Free** `(310,1355)` (red dot) → result → **Confirm**
   `(300,1755)`. **Never "Recruit 1"** on the result screen (spends a ticket). Button then shows
   "Free after HH:MM:SS".
4. **Artifact** bottom tab `(618,1840)`. Check the **Auto** toggle `(882,1658)` is **off** (grey).
   Tap **Free** `(540,1638)` once → fragment shown; the button turns into **Wish (500 stars)** — stop, that's paid.
   Tiers with a gem price (Brilliance 280) are paid summons; ignore.
5. Gems must be unchanged at the end.

## Hero upgrade (Bone Archer +1 level, 1st gear +1)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Costs potions/gold/stones only, never gems.

1. Main screen → **Hero** `(274,1810)`. Hero strip at y≈1536: swipe left to the end
   (`input swipe 950 1536 150 1536 300`, ~15×).
2. **Bone Archer** (Lv.57-ish skeleton, 3 purple stars, Mythic) is second to last: `(787,1580)`.
   Verify the name top-left.
3. **Level Up** `(540,1178)` **once** → level +1 (cost ~23000 potions). Its position shifts after
   the first tap ("↑ Lv.90" quick-level button appears above it at `(540,1060)`) — never tap that.
4. 1st gear (bow, top-left slot) `(117,360)` → popup "Swift Longbow LV.N » N+1", cost gold + stones.
   **Enhance** `(540,1395)` **once**. Never the "↑ Lv.69" quick button or Reset.
5. Close popup `(540,120)`; verify the gear badge shows N+1.
