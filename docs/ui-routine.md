# UI routines

All coordinates are in the **MuMu Android Device** game window's full-resolution frame
(704×1289), as used by `computer_app_click` on that window (ADB uses device coords — see below). Instance window ids change after
every restart — get a fresh one with `computer_app_list_windows`.

## Daily run order (Nick, 2026-10-26)

Run the missions in this order on each account:

1. **Match** — exhaust tickets.
2. **Fishing** — orders to threshold, Benefit (only if red dot), start Auto. Don't collect order rewards here.
3. **Patrol** — Speed Patrol ×3 + Claim All.
4. **Shop** freebies.
5. **Play Pass** claims.
6. **Adventure** — everything in it: Tower of the Throne, Secret Sanctuary, Gate of Darkness, Land of Trials
   (+ any other mapped Adventure mode).
7. **Recruit** free summons.
8. **Hero** upgrade (after the potion-giving steps above).
9. **Tribe** — sign-in, Trial, chat Request + Assist.
10. **Divine Weapon** — Benefit, Excelsior Veins, Forge.
11. **Adventure stage** run (skull bubble).
12. **Patrol** — Claim All only.
13. **Rune** synthesis.
14. **Match** — exhaust tickets again before wrapping up.
15. **Grocery** free chests.
16. **Events** — the 2–3 event banners at the top right of the main screen (they rotate and change;
    e.g. Wish Festival, 7777 Draws, Match Event, Weekly Event, Pet Arena). Open any with a **red dot**;
    inside, also check the bottom event tabs for red dots. Claim only **free** red-dot rewards
    (Claim / Free buttons). Never tap a $ or gem price, never draw/spin with paid currency. Back out
    (`(88,1812)`) when no red dots are left.
17. **Fishing** — the only place order rewards are collected: Order Info → a completed order shows a yellow
    **Claim/Nhận** button where Refresh normally is (`(849, 704/1058/1412)`) → tap → dismiss `(540,1880)`.
    Before that: go back and collect them (exact claim step not mapped yet: screenshot the
    Daily Order panel / Order Info and claim any completed order).

A "Match attempts full" popup can interrupt any step: Confirm, exhaust Match, resume.

Focus on the steps, not on resources: don't track gem/resource balances (they change all the time).
The only money check is reading the price on screen before any paid tap and respecting the config caps.

**Multiple accounts at once:** one worker (subagent) per MuMu instance, each with its own ADB serial and
its own scratch dir for screenshots; workers don't edit the repo — they report, and the coordinator
updates the docs. Set each instance to 1080×1920 first (see "Gotchas from xFaktor run").

## Speed: `scripts/tap.py`

Use `D=<adb serial> scripts/tap.py x,y [x,y ...] [-o out.png]` for every tap (device coords):
it waits only until the screen changes and settles (~1 s per tap, max 4 s) instead of a fixed sleep,
and saves a 540×960 screenshot (multiply its coords ×2 for device coords). No args = screenshot only (~0.4 s).
- Chain known taps of a flow in one call; screenshot-check only at decision points (prices, counters,
  unexpected popups). Always check the current screen before the first tap of a flow.
- Long waits (battles): poll with `scripts/tap.py` every ~10–15 s, never blind sleeps.

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

- **Game language differs per account** (`account.language` in the config; Dminor = Vietnamese:
  "Miễn phí" = Free, "Xác nhận" = Confirm, "Nhận" = Claim). Layout/coords are the same; judge buttons by
  colour/position + counters, not English text.

- **Taps during animations are ignored.** Popups slide in; after opening one, take a screenshot,
  then tap. Always confirm the result with a screenshot — never chain taps blindly.
- **Each free sweep = two taps** (a paid one = four: Sweep → Confirm → Sweep → dismiss): `Sweep`, then dismiss the *Congratulations* reward popup (it also
  auto-closes after ~3 s). The tap that looks "ignored" right after a sweep is usually the one
  that dismissed the popup.
- **Safe dismiss tap:** `(352, 140)` — the screen title area; does nothing if no popup is open.
  Don't dismiss by tapping near the bottom: it can hit a list item behind the popup.

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

1. **Tribe roster:** members are fixed (Nick, 2026-10-26). Use the saved list in `accounts/tribe_<name>.txt`;
   only read it in-game if that file doesn't exist yet (then save it). Main screen → **Tribe** `(448,1780)`
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
   If the account has `match.skip_same_server: true`, also skip opponents on the account's own server
   ("S###" tag, e.g. S201 — on the leaderboard / opponent profile). Server unknown → skip.
   The dialog closes and shows *Congratulations* (+40 match points, 11000 gold).
   Dismiss with `(540,120)`, confirm the ticket count dropped by 1 on the Challenge button.
5. Repeat from step 2 until tickets = 0. The opponent list changes after every crash.

**Interrupt: tickets full.** During any daily, a popup can appear saying Match attempts are full.
Tap its **Confirm**, run the Match routine above until tickets = 0 (same tribe rules), then go back
and continue the daily you were on. (Popup text/coords not captured yet; screenshot it next time.)

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

## Tower of the Throne (1 daily challenge)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Goal: one challenge for the daily task.
Keep the pre-selected lineup (Nick, 2026-10-26: don't bother picking the weakest hero).

1. Main screen → **Adventure** `(100,1460)` → Tower of the Throne **GO** `(787,687)`.
   Ticket count top-left (10/day on Cmajor).
2. **Challenge** `(540,1805)` → lineup screen (5 strongest heroes pre-selected) — leave as-is.
3. **Start** `(540,1808)` → result screen. Dismiss by tapping `(540,1700)` (below the
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

## Tribe (sign-in, Tribe Trial, chat request/assist)

Mapped 2026-10-26 on Cmajor via ADB (device coords). All free.

1. Main screen → **Tribe** `(448,1780)`.
2. **Sign-in** `(538,476)` (same row as Member `(192,474)`) → **Sign-in Reward** `(538,1546)` →
   dismiss `(540,120)` → close the dialog by tapping `(540,1680)`.
3. **Tribe Trial** card `(540,735)` → Flame Lord boss → **Challenge** `(540,1806)` → lineup screen.
   The 5 heroes on the field are this mode's preset lineup; keep it → **Start** `(540,1806)`.
   Timed boss fight (~1 min, runs on its own). Poll with a screenshot every ~15 s and Confirm `(540,1483)`
   as soon as *Challenge Complete* shows — never wait blind longer than ~80 s.
   One run per day (2026-10-26: 247.5M damage, ×30 chests).
4. Back `(92,1810)` → Tribe screen → **Chat** `(800,1806)` → **Request** `(174,1631)` (red dot) →
   *Help Request Info* dialog:
   - **Request** `(334,1660)`: send our own help request (greyed with a cooldown timer if already sent).
   - **Assist** `(740,1660)`: helps every listed request at once; list empties.
   - Close ✕ `(968,228)`.
5. Never type or send chat messages.

Coordinate tip: screenshots are scaled ×0.469 (1080→506). Convert with device = view / 0.469 on
**both** axes — a y-only miscalc made Sign-in taps miss silently.

## Fishing (orders, benefit, auto fish)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Done = auto fishing started; leave it running.

1. Main screen → **Fishing** `(624,1780)`.
2. **Order Info** `(190,786)` → *Daily Order* dialog: 3 orders, refresh-ticket count top-left.
   Tier = filled diamonds (5 max): 1 common, 2 rare, 3 legend, 4 mythic, 5 eternal (name turns red at 4+).
   Target per account: `missions.fishing.min_order_diamonds` (Cmajor: 4 = Mythic+).
3. Refresh buttons x=`849`, y = `704 / 1058 / 1412` (orders 1–3). Costs **1 refresh ticket**; first
   time a *Order Refresh* confirm appears → tick "Do not remind me today" `(390,1380)` → **Confirm** `(757,1211)`.
   Automate with `scripts/fish_orders.py ROW MAX` (pixel check on the diamonds; row y = 567/921/1275,
   diamond x = 633/706/778/851/921; filled = R>200, empty = (58,85,115)).
4. Out of tickets: buy with **50 gems** via `+` next to the ticket count (Nick: "buy 1 you'll have
   5 tickets, buy more when out") — not yet exercised; screenshot the purchase popup and verify 50 gems.
5. Close ✕ `(973,270)`. **Benefit** `(330,1800)` **only if it has a red dot** — no red dot = don't open it → **Claim Reward** `(540,1662)`
   (60 bread, 5 refresh tickets, baits) → dismiss `(540,120)` → close ✕ `(970,238)`.
6. **Auto** `(982,1222)` → *Auto Fish* settings (keep as-is: Auto-submit Orders ✓) → **Start** `(540,1485)`.
   Button becomes "Auto Fishing". Leave it.

2026-10-26: 4 refreshes (81 → 77 tickets) for 3 Mythic orders; no gems spent.

## Divine Weapon (benefit + Excelsior Veins)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free.

1. Main screen → **Divine Weapon** `(798,1780)` → Arsenal.
2. **Benefit** `(309,1810)` (red dot) → **Claim Reward** `(540,1662)` (1500 crystals, 2 potions,
   2 embers) → dismiss `(540,120)` → close ✕ `(970,238)`.
3. **Excelsior Veins** `(980,1810)` → mining grid. Attempts = pickaxes `N/80` (bottom centre;
   regenerates over time). Keep the "Automatically advance to next floor" tick as-is.
4. **One-Click Mining** `(896,1612)` → *Congratulations* → dismiss `(540,120)`. Repeat until pickaxes = 0.
   Don't use the dynamite / drill items or the `+` on the pickaxe (buys more).
5. **Forge** (Arsenal screen, anvil button "Forge N/M", crystal cost below e.g. `6755/500` = owned/cost):
   M = forge slots, varies per account (7, 8, 13…). If no forge is in progress, fill **every available
   slot** — stop when slots are full or crystals < cost. Skip if a forge is already running.
   Crystals only, never gems. Forge anvil button ≈ `(540,1580)` on Arsenal (shows a timer while a forge runs)
   — tap not yet verified; screenshot and verify the cost is crystals.

2026-10-26: 22 → 10 → 0 pickaxes in 2 clicks.

## Adventure stage (1 run)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Daily task: challenge the current stage once.

1. Main screen → blue **skull bubble** next to the hero `(994,964)` (not the stage map top-right).
2. Battle setup "Stage: X-Y" (Illusionary mode locks most heroes; keep the lineup) → **Start** `(540,1806)`.
3. Result (Defeat on 2-1, 715K vs 11857K) → close by tapping `(540,120)`; never "Challenge again".

## Patrol (speed patrol ×3 + claim all)

Mapped 2026-10-26 on Cmajor via ADB (device coords).

0. **First exhaust Match tickets** (Match routine) — Nick, 2026-10-26. Run Match again afterwards if
   patrol rewards added tickets.
1. Main screen → patrol **bag** with timer, right side `(983,1463)` → *Loot* dialog.
2. **Speed Patrol** `(337,1590)` → *Tip* "Obtain 4 hours of Patrol Gains" → price button `(540,1164)` →
   *Congratulations* → dismiss `(540,1700)` → the Tip reopens with the next price.
   Prices per day: **Free, Free, 50, 100, …** (escalates). Daily target = **3 claims total**
   (2 free + 1 at 50 gems). Read the price on the button every time; stop if it's not what's expected.
3. Close the Tip ✕ `(936,638)` → **Claim All** `(742,1590)` → *Congratulations* (auto-closes) →
   dismiss `(540,120)`. Patrol timer resets to 00:00.

## Rune synthesis (1/day)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free.

1. Main screen → menu ☰ bottom-right `(994,1625)` → **Backpack** `(900,1775)` → **Rune** tab `(868,1680)`.
2. Scroll down (`input swipe 540 1300 540 700 800`) to the red (Mythic) runes. Tap one **without a
   lock** — the grid's tiny lock icons are easy to misread; the popup is the truth: a locked rune
   says "Locked Runes can't be synthesized", an unlocked one shows **Synthesize** `(540,1200)`.
   Never tap the lock toggle in the popup.
3. *Synthesize Runes* dialog → **Quick Equip** `(417,1668)` (fills 4 same-quality runes — it picks the
   lowest tier, e.g. 4 blue → 1 purple; that's fine) → **Synthesize** `(824,1668)` with ×1.
4. Result → **Confirm** `(540,1190)` → close ✕ `(972,560)` → close Backpack ✕ `(972,238)`.

## Grocery (free Daily Specials chests)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free only.

1. Main screen → menu ☰ `(994,1625)` → **Grocery** `(900,1230)` → *Daily Specials* tab.
2. Top row = 4 free chests, **Free** buttons at y=`893`, x = `163 / 413 / 663 / 913`.
   Rows below have gem prices — never tap them.
   - Chest 1 Gold Coin Pack: 1 claim.
   - Chests 2–4 (Hero, Resource, Growth): **3 claims each**, ~3 s cooldown between claims.
3. Loop: tap any chest whose button says **Free** → popup must say Free `(540,1344)` (never a gem
   price) → claim → dismiss `(540,120)`. If no chest says Free but some show a cooldown, wait it out
   and keep going. Done only when all 4 show **Sold Out**. Growth Chest gives +80 gems per claim.
   Automated: `D=<serial> scripts/grocery.py` (colour-based, works in any language; the popup's Free
   button moves per item, so it scans for the green button). Claimed all 9 in one run on Aminor.
4. Close ✕ `(966,222)`.

## Gotchas from xFaktor run (2026-10-26)

- Instances with a 600×1080 display: `adb shell wm size 1080x1920 && adb shell wm density 480`, restart the
  game → all device coords here apply. Undo with `wm size reset` / `wm density reset`.
- Secret Sanctuary first time: "Bonus Effects" intro → Confirm `(540,1616)`.
- Gate of Darkness: Pause → **Quit Battle** `(376,920)` (still counts as Victory) → Confirm `(540,1406)`
  → **Sweep** `(942,1058)` → Confirm `(760,1370)`.
- Land of Trials: dismissing the reward with `(540,120)` can close the whole dialog; `(540,700)` is safer.
  Dialog ✕ `(970,570)` may need a second tap.
- Fishing ticket purchase: `+` `(272,425)` → Purchase `(540,1203)`; popup stays open, close by tapping `(540,1600)`.
- Grocery: Free button pixel `(480,1344)` green (123,206,49) = claimable, grey (173,178,189) = cooldown;
  chests 2–4 cooldown ~5–8 s.
- Excelsior Veins back arrow returns to Arsenal, not main screen — back again.
- Match tickets can exceed the cap ("Full", e.g. 7/6) after rewards.

## Gotchas from Chien Than run (2026-10-26)

- After Start, a promo popup may appear: **Cancel** `(337,1281)`.
- **Match attempts full** popup (can appear mid-dailies, e.g. during Land of Trials): Confirm `(696,1162)`.
- Artifact Auto toggle `(935,1658)` was ON on this account — check it's grey before summoning.
- Grocery: dismiss rewards at `(540,1850)`; `(540,120)` once closed the whole Grocery screen. Resource Chest can roll +50 gems.
- Land of Trials: if the reward popup already auto-closed, a dismiss tap hits the list behind (opened the next dungeon once).
  Sweep → wait 7–8 s → dismiss once.
- Fishing auto can stop on its own ("Stop at new Archive"); re-check the Auto Fishing state before leaving.
- Accounts without the Divine Weapon forging pass ($8.99) have no Benefit claim; Weekly/Monthly Play Pass cards may be unowned.

## Gotchas from Aminor run (2026-10-26)

- Land of Trials paid sweep: the screenshot right after Confirm can look stale; wait ~3 s and re-check before retrying.
- Hero strip: Bone Archer position varies slightly (`(764,1580)` on Aminor vs `(787,1580)`) — verify the name.
- Events: Pet Arena achievements — one **Claim/Nhận** claims all; 7777 Draws daily claim plays 30 free draws
  → Confirm `(540,1756)`; don't tap the "claim one more time" (Nhận thêm một lần) button (likely paid).
- Back tap after Tribe Chat can land on Recruit — back out again.
