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
