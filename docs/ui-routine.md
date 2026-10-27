# UI routines

All coordinates are in the **MuMu Android Device** game window's full-resolution frame
(704×1289), as used by `computer_app_click` on that window (ADB uses device coords — see below). Instance window ids change after
every restart — get a fresh one with `computer_app_list_windows`.

## Daily run order (Nick, 2026-10-26)

Run the missions in this order on each account:

0. **Pet Arena** — **Mon/Tue/Wed only** (skip other days): join + Auto Deploy (see "Pet Arena" below);
   runs on its own.
0b. **Storm Battlefield** — right after Pet Arena (see "Storm Battlefield" below). Skip on Mondays — closed
   until 17:00; run `/catch-up` after 17:00.
1. **Match** — exhaust tickets.
2. **Fishing** — orders to threshold, Benefit (only if red dot), start Auto. Don't collect order rewards here.
3. **Patrol** — Speed Patrol until the price is 100 gems (don't buy that one) + Claim All.
4. **Shop** freebies.
5. **Play Pass** claims.
6. **Adventure** — everything in it: Tower of the Throne, Secret Sanctuary, Gate of Darkness, Beast Realm, Land of Trials
   (+ any other mapped Adventure mode).
7. **Recruit** free summons.
8. **Hero** upgrade (after the potion-giving steps above).
9. **Tribe** — sign-in, Trial, chat Request + Assist, **Canyon Clash** (skip on Mondays — it's closed until 17:00;
   run `/catch-up` after 17:00).
10. **Divine Weapon** — Benefit, Excelsior Veins, Forge.
11. **Adventure stage** run (skull bubble).
12. **Patrol** — Claim All only.
13. **Rune** synthesis.
14. **Match** — exhaust tickets again before wrapping up.
15. **Grocery** free chests, then the account's `grocery_buy` tiles (if any).
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
- Taps with no visible effect return after ~1.5 s (`NO_CHANGE`), not the full `MAX_WAIT`.
- Waiting for something (battle end, button back): `scripts/tap.py [taps] --until x,y,r,g,b[,tol] --timeout s`
  polls every ~0.3 s and returns the moment that device pixel matches — no fixed sleeps, no 10–15 s polls.
- Storm matches: `D=<serial> scripts/storm.py` (plays until tickets run out incl. one free-ticket claim, ~0.5 s polling;
  exit 1 = unexpected screen, screenshot and report — don't re-run it in a loop).
  Grocery: `scripts/grocery.py` (no fixed sleeps).

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

- **`tap.py` screenshots are 540×960 — double every coord read off them** before tapping (device = 1080×1920).
  Workers keep mis-tapping by passing screenshot coords directly.
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

Goal: spend every free ticket crashing the **topmost attackable** opponent (not in our tribe) — Nick, 2026-10-27.

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
4. Pick the **topmost** attackable row (scan from row 1 down): blue **Crash** and name not on the roster → tap it.
   **The last row is always a bot — always attackable** (no tribe/server check needed); use it when no
   row above it qualifies, so tickets never go unused.
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

## Secret Sanctuary (sweep if offered, else climb 10 floors) — Nick, 2026-10-27

Sweep only exists for a while after a full clear (Nick: ~7 days); when the map rotates (2026-10-27:
Ice Citadel → **Lava Cave**) there's no Sweep and you **attack from floor 1**. Mapped on Cmajor, ADB device coords.

1. Main screen → **Adventure** `(100,1460)` → Secret Sanctuary **GO** `(787,962)` → map.
2. If a plain **Sweep** `(540,1778)` shows: Sweep → *Tip* **Confirm** `(533,1197)` → dismiss `(540,120)`. Done.
3. Else climb. Floor nodes (yellow marker = next), Lava Cave: 1 `(664,1440)`, 2 `(526,1210)`,
   3 `(786,1040)`, 4 `(552,956)`, 5 `(264,860)`, 6 `(502,786)`, 7 `(746,724)`, 8 `(630,574)`,
   9 `(414,506)`, 10 boss `(590,340)` (other maps: read the node off the screenshot).
   - Floor popup: yellow **Crash** `(540,1380)` = instant win (we out-power it) → *Congratulations* → dismiss `(540,120)`.
   - Green **Battle** `(540,1380)` → lineup (HP **carries over** between floors) → if fewer than 5 ticked,
     **Quick Deploy** `(984,1800)` → **Start** `(540,1808)` → ~25 s → *Victory* → **Confirm** `(540,1404)`.
     A loss: stop and report (don't use Recovery Potion).
4. After each floor: **Select Bonus Effect** (3 cards at `(192|540|884, 950)` → **Confirm Selection** `(540,1426)`).
   Pick, in order:
   1. A **preferred** buff: ATK Drill, DMG Increase Drill, Infinite Energy, Concentrated Fire, Iron Shield,
      Mental Fear, Battle Cry — if several, the rarer one (Mythic > Legend > Elite > Rare).
   2. Else the rarest card (Mythic > Legend > Elite > Rare).
5. Once 5/5 owned: **Replace Bonus Effect** — top row = offered `(192|540|884, 660)`, bottom row = owned
   (`(150|460|740|1000, 1300)`, 4th is half off-screen). Replace only if it's an upgrade: a preferred
   buff over a non-preferred one, or a higher rarity over a non-preferred one → **Replace Bonus** `(780,1676)`.
   Otherwise **Skip** `(302,1676)`.
6. After floor 10 all nodes show flags. Back `(92,1810)` → main screen.

2026-10-27 Cmajor (6673K CP): floors 1–2 Crash, 3–10 Battle, all won (HP never below 56%).
Final buffs: Mental Fear, ATK Drill, Stun Curse, Infinite Energy, Iron Shield.

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

## Beast Realm (1 challenge/day) — Nick, 2026-10-27

Coords scaled from Nick's screenshots (unverified — screenshot first, fix here after the first run).

1. Main screen → **Adventure** `(100,1460)` → wait for the list to settle → Beast Realm **GO** `(790,1790)` (verified on Cmajor)
   (6th card, below Ancient Ruins; scroll down if not visible).
2. Beast Realm screen: middle beast card (e.g. Mountain Demon, "Endless"). **Challenge** `(540,1810)`
   shows "Chances: N" under it.
3. Lineup screen (5 pre-selected, green ticks) — keep it; if none ticked, **Quick Deploy** `(1014,1814)`.
   **Start** `(540,1810)` → battle → dismiss the result screen (not mapped yet; never "Challenge again").
4. **One challenge only** (Nick, 2026-10-27) — verify Chances dropped by 1, then back out. Never pay
   for chances, never open **Shop** (bottom right).

## Recruit (free summons only)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Daily: **2 Common, 1 Ancestor, 1 Artifact**, all free.

1. Main screen → **Recruit** `(96,1810)` (opens on Advanced Recruitment — skip it, it uses tickets).
2. **Common Recruitment** tab `(188,1610)` → "Chances: N" + **Free** `(540,1355)`. Tap → result cards →
   dismiss `(540,1700)` (wait ~2 s for the card flip). Do it twice (some accounts — Aminor, Dminor, Chien Than, xFaktor — only get 1 chance; Kong and Bino get 2; "Lượt còn lại không đủ" / "Chances: 0" = done). A cooldown (~5 min) shows
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
   Automate with `D=<serial> scripts/fish_orders.py ROW MAX MIN` (MIN = `min_order_diamonds`, default 4; pixel check on the diamonds; row y = 567/921/1275,
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
   Crystals only, never gems. Forge anvil ("Forge"/"Rèn") on Arsenal: `(540,1484)` (verified on xFaktor 2026-10-26); 500 crystals per slot, ~4 h timer;
   a running forge shows a timer → skip. Screenshot and verify the cost is crystals.

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
   Prices per day: **Free, Free, 50, 100, …** (escalates). Keep claiming until the button shows
   **100 gems** — don't buy that one, stop (Nick, 2026-10-26). Read the price on the button every time.
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
4. **`grocery_buy`** (per account, optional): for each shop tab listed (Sanctuary / Tribe / Ruins / Realm /
   Tundra — swipe the tab bar left to reach the later ones), buy each listed tile **once**. Tiles are
   numbered 1–12 left→right, top→bottom; price buttons at x = `163 / 413 / 663 / 913`,
   y ≈ `893 / 1249 / 1605` (rows 2–3 estimated from screenshots — verify and update).
   - Skip tiles already **Sold Out**, and tiles whose price is more than the shop's balance (top left).
   - The price icon must be that shop's own currency (the one next to the balance) — never gems or $.
   - Buy popup not mapped yet: screenshot, confirm the price, tap Buy, screenshot again to see Sold Out.
5. Close ✕ `(966,222)`.

## Daily Mission (claim all + activity chests) — Nick, 2026-10-27

Last step of `/catch-up`. Coordinates not mapped yet — locate by screenshot and record them here.
1. Open **Daily Mission** from the main screen → **Daily** tab.
2. Tap every yellow **Claim** button (rows with a red dot), scrolling the list until none are left.
   Never tap **GO** (it navigates to the mission, e.g. Grocery diamond purchase / Statue upgrade).
3. Top bar *Daily Activity Levels*: chests at **40 / 80 / 120 / 160** points. Tap each chest whose
   threshold ≤ the points shown on the left scroll icon; dismiss the reward.
4. Report each chest still unclaimable and the current points. The **Weekly** tab is out of scope.

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

- Land of Trials paid sweep: the screenshot right after Confirm can look stale even though the purchase went
  through — re-check "Challenge Attempts: 1" before tapping again, or you can **double-buy**.
- Hero strip: Bone Archer position varies slightly (`(764,1580)` on Aminor vs `(787,1580)`) — verify the name.
- Events: Pet Arena achievements — one **Claim/Nhận** claims all; 7777 Draws daily claim plays 30 free draws
  → Confirm `(540,1756)`; don't tap the "claim one more time" (Nhận thêm một lần) button (likely paid).
- Back tap after Tribe Chat can land on Recruit — back out again.
- Safe dismiss for Grocery / Patrol / Fishing reward popups: `(540,1880)` (very bottom).
- Event screens: bottom tabs at y=`1850`, x ≈ `140 / 480 / 650 / 818 / 986`. Banners rotate between screenshots.
- Tribe Chat Request button may need a second tap at `(174,1636)`.

## Gotchas from Dminor run (2026-10-26)

- Forge: "Forge/Rèn N/M" anvil ≈ `(540,1460)` with a timer above while running; Queue ≈ `(60,1250)`.
- Grocery popup Free button position varies: chest 1 `(540,1204)`, chests 2–4 `(540,1344)` — use `scripts/grocery.py`.
- Land of Trials: wait ~1.5 s after the dialog opens / after buying, or the Sweep tap is lost. Sweep → wait 7–8 s → dismiss `(540,700)`.
- "Match attempts full" popup Confirm `(740,1162)` only closes it — go to Match yourself.
- Match: a crashed row turns into a shield timer (tapping it does nothing); re-read rows every round.
  Weekly win chests (10/20/35/50 wins) along the top bar, e.g. 10 ≈ `(376,210)`, 20 ≈ `(536,210)` — free once reached.
- Hero strip: on less-developed rosters no scroll is needed; find Bone Archer by screenshot (strip y=`1580`).
- Opening Tribe Chat auto-claims assist rewards.
- Events seen: Wish Festival (check-in, gifts), Pet Arena (achievements, packs), 7777 Draws (daily 30 free),
  weekly event merchant (free 200), Tribe Battle banner → Packs `(976,1630)` (free 20 gems daily).
  Skip draws that spend event coins and "Join" buttons without a red dot.
- Accounts without the fishing pass get no daily bread → Auto stops when bread runs out; that's expected.

## Gotchas from Cino / Dino / Tiger run (2026-10-26)

- **Accounts without a pass (Dino) get video ads where others get Free**: Storm free tickets ("Watch Video –
  Claim"), Common Recruitment ("Recruit 1" with ad), Grocery chests (grey button + camera icon), Wish Festival
  Gift Free Pack. Ads are ~37 s, Android Back does nothing, skip/close appears top right ≈ `(990,90)`.
  Not mapped as a routine — skip these and report.
- **Startup:** 2nd Anniversary promo after Start; ✕ ≈ `(988–1006, 322–348)`.
- **Pet Arena** (device): 1st banner → Pet Arena tab `(480,1850)` → Join `(540,1528)` → last-season *Champion*
  popup ✕ `(972,548)` → Auto Deploy `(956,1640)` → Start `(540,1570)`. "Free attempts used up" toast = already
  ran today; dialog ✕ `(938,282)`.
- **Storm card:** pixel `(760,450)` gold ≈ `(230,150,66)` = Storm showing, blue = other event; tap `(880,480)`.
  At y=460 the gold reads darker ≈ `(132,85,49)` — use y=450 for `--until` (2026-10-27). Tapping `(880,480)`
  while another card shows usually still opens the event screen on the Storm tab.
- **Play Pass, Monthly Card not owned:** still has a free track of yellow Claim buttons (x≈830–896, scroll the
  list; dismiss `(300,200)`). Never the green "Continue to claim" (paid track).
- **Match Event → Heroic Trial** sub-tab `(400,190)`: free Land of Trials point rewards, Claim ≈ `(896,1024)`.
- **Tribe Trial:** Challenge still starts a fight after the daily one ("No Rewards"). No red dot on the card = done, skip.
- **Back from Tribe Chat** goes straight to the main screen.
- **Main-screen "Tribe Clash" banner** countdown is not Canyon's: check Canyon inside the Tribe screen.
- **Coords seen elsewhere:** Common Recruit result Confirm `(540,1756)`; Tiger gear slot 1 `(117,400)`,
  Enhance `(540,1384)`; hero strip swipe at y=1590.
- **Forge (Dino):** stopped responding at 4/8 even with 3 s gaps — cause unknown, skip after 2 tries.
- Unmapped, left alone: Adventure → Ancient Ruins (red dot), main-screen "Mars's Gift".

## Gotchas from Bino run (2026-10-26)

- No Play Pass → many "Free" rewards are **video ads** (camera icon / "Purchase Play Pass to skip ad"): Common
  Recruitment, Grocery chests 2–4, Storm "+" Watch Video, Wish Festival Gift Free Pack. Skip them.
- Monthly Card (not owned): the left free-track item of each "Points reached" row has its own yellow **Claim**
  (red dot) — free; "Continue to claim" (green) wants the purchase, skip. Rows `y` shift as you scroll.
- `tap.py` taps can register late with NO_CHANGE: Level Up tapped twice gave +2 levels. Re-screenshot after ~1.5 s
  before retrying a tap that "did nothing".
- Match Challenge list: after scrolling to row 6, rows shift ~+100 px — re-read the screenshot before tapping.
- Pet Arena / Tower / Sanctuary / Gate / Recruit / Patrol were already done earlier that day — trust the counters, not the plan.

## Gotchas from catch-up run, all accounts (2026-10-27)

- Startup popups: "Stargems Running Out!" → Cancel `(337,1281)`; 2nd Anniversary popup (Vietnamese text) → ✕ `(990,346)`.
- The first tap on the main screen right after loading is often ignored — retry once, then screenshot (a late
  second tap can open a ranking profile; close by tapping outside, e.g. `(900,1500)`).
- Match: the Challenge list can have only 1–2 rows; the Match icon keeps a red dot at 0 tickets (Day Ranking
  gift) — read the ticket badge, not the dot. Opponent profile "War Zone: AreaNNN" = their server.
  Dminor's list is all its own server (Area205) — still crash the last row: it's a bot (Nick, 2026-10-27).
- Common Recruitment: the Free button stays green at "Chances: 0" — read the counter. Result Confirm `(540,1756)`.
- Excelsior Veins: pickaxes found in the mine are added back; repeat One-Click Mining until 0 (1–6 taps).
- Forge: "Forge N/M" = filled slots; 0/M = idle. Each anvil tap `(540,1484)` fills one slot (500 crystals).
- Events: Match Event → **Canyon Warrior** tab has free Canyon point milestones, Claim `(896,1024)`.
  Wish Festival → Gift → Free Pack Claim `(866,912)` (plain claim on Dino today), close ✕ `(966,190)`.
  7777 Draws: never tap "Again" (its red dot stays when all daily claims are ticked).
- Aminor and Dminor showed English today despite `language: vi` in their configs.

## Gotchas from dailies run, 7 accounts (2026-10-27)

- `fish_orders.py` returns `None` when the first-time *Order Refresh* confirm shows: tick `(390,1380)` →
  Confirm `(757,1211)`, re-run. Auto Fishing stops when bread runs out (~4/100) on most accounts — restart
  Auto at the end of the run.
- `grocery.py` sometimes stops early (chests still green Free) or its last dismiss closes Grocery: reopen
  Grocery and re-run until all 4 show Sold Out. Needs ~4.5 s between the Free tap and dismiss `(540,1850)`.
- Grocery buy: tabs Sanctuary `(452,546)`, Tribe `(732,546)`, Ruins `(980,546)`; swipe the tab bar
  `900→200` at y=546 → Realm `(604,546)`. Row-1 price `(913,893)`, row-3 `(913,1605)`. Purchase
  popup `(540,1203)`, dismiss `(540,1850)`. Balance below the price → skip + report.
- Land of Trials, list at top: GO Ancient Battlefield `(870,925)`.
- Pet Arena: Champion popup reopens a few s after ✕ `(972,548)` — open Auto Deploy right after closing.
  Backing out asks "Exit?" → Confirm `(760,1162)`. Already done today = 0 tickets top-left.
- Match: when the top rows are all tribemates, the target is row 6 after swipe `540,1500→540,900`,
  Crash ≈ `(866,1652)` (rows shift after a crash — screenshot every time). 35-win chest ≈ `(696,210)`.
  Dminor: only same-server opponents listed → Match was skipped; now crash the last-row bot instead.
- Gate of Darkness: Pause may need a 2nd tap; Sweep confirm ≈ `(770,1390)`. A network-error popup sends
  the game to the loading screen — that run uses no chance, re-run.
- Excelsior Veins at 0 pickaxes: One-Click Mining opens a gem purchase popup → ✕ `(938,636)`.
- Recruit: Aminor/Dminor/Bino/xFaktor showed 2–4 Common chances — still do only the configured 2.
- Bino now has a Play Pass: free claims (Recruit, Grocery, Gift pack, Storm tickets) are plain, no ads.
  Dino's were plain too today.
- Hero strip: Bone Archer is the **last** card on xFaktor/Dino/Tiger (≈ `(940-976,1600)`), ≈ `(774,1580)`
  on Bino/Aminor, `(216,1580)` on Dminor — find it by screenshot.
- Aminor and Dminor showed English despite `language: vi`.
- Events (free only):
  - Pet Arena → Pack `(88,370)` → Free `(866,834)`; Achievement `(88,690)` → Claim `(866,606)`.
  - Wish Festival → Sign-In ≈ `(876,1500-1560)` → today's Claim `(862,1498)`; Gift `(270,1600-1660)` → Free
    Pack `(866,912)` ×2 (Limited: 2). Treasure Vault = event-coin draws → skip.
  - 7777 Draws: Claim `(540,1606)` → Open All `(856,1764)` → Confirm `(540,1756)`.
  - Weekly Event / Hero Recruit: Pet Shop / Recruit Store sub-tab `(410,240)` → Free Benefits `(896,1024)`.
  - Tribe Clash banner `(880,624)` → Pack → Free `(866,934)`.

## Pet Arena (join + Auto Deploy)

**Only open Mon, Tue, Wed** — skip on other days. Run it first in the dailies.
Added by Nick 2026-10-26. Strategy is per account (`missions.pet_arena` in the config); for now all accounts
use **Stamina order High to Low, 4 sprites**.

1. Main screen → **1st event banner** (top right) → bottom tab **Pet Arena** ("Đấu Trường Tinh Linh") →
   **Join** ("Tham gia").
2. **Auto Deploy** (bottom right of the arena screen) → *Auto Deploy* dialog:
   - **Deployed Sprite per Battle** = config `sprites` (4).
   - Strategy `stamina_order`: tick **Deploy by Stamina Order** (right checkbox) and set its dropdown to
     config `order` (**High to Low**; options High to Low / Low to High / Random Selection). The per-pet
     rows (Pet 1–4 rarity + stamina) stay unticked.
   - Strategy `per_pet`: untick the stamina row, tick the Pet 1–4 block, and set each Pet row's rarity +
     stamina dropdowns from config `pets` (only the first `sprites` rows are used). E.g. Cmajor: 2 sprites,
     Pet 1 = Eternal + Highest Stamina, Pet 2 = Eternal + Lowest Stamina.
   - Keep **Auto-Stop when free attempts are used up** ✓ and **If available slots < set amount…** ✓.
3. **Start**. Leave it running. Coords not mapped yet — screenshot every step on the first run.
   Never buy attempts.

## Canyon Clash (Tribe group)

Added by Nick 2026-10-26; mapped on Cmajor via ADB (device coords).

**Season: opens Monday 17:00, closes the next Monday 06:00.** So Tue–Sun it's part of the normal dailies; on
**Monday** it's closed until 17:00 — do it in a separate run after 17:00 instead
(e.g. `/catch-up`, which does Storm + Canyon). xFaktor's tribe showed "Tribe Clash: Unlocks in 19h45m" at
Mon 21:00 (2026-10-26) while the others were open — if it's locked on screen, skip.

Entry: main screen → **Tribe** `(448,1780)` → **Canyon Clash** card `(540,1090)` → vertical map (scroll with
`input swipe 540 1500 540 600 600`). Header shows your current spot ("Unoccupied" or e.g. "Silver Battlefield",
Occ. Time, Occ. Gains) and **Attempts N** (5 on Cmajor; never tap `+`, buys more).

Map, top → bottom: player-held spots (green dome = shield), then **Gold Sentinel** spots (white/gold platforms,
~60K CP NPCs), then **Silver Sentinel** spots (purple platforms = the "purple 9/m" spots: 9/min + 1 medal/h,
~41–44K CP NPCs). Glory spots are presumably above/among the top ones. Truly **empty** platforms (no occupant at all) also
appear — prefer those first; otherwise a Sentinel-held spot (no player) counts as free — beat it to take it. Occupant names: **blue** name background = tribe member,
**purple** = not in our tribe; your own spot shows a **green** name.

**Scan the whole map first** (scroll top → bottom, screenshot each screen) and choose by priority — empty
platform > Sentinel-held > non-tribe player — before tapping anything.
Silver (purple-platform) spots: consider **only the first 10** from the top (Nick, 2026-10-26) — ignore
silver spots further down. Spots change while you scroll.

Empty platform: tap it (wait for map scroll inertia to stop first, or the tap misses) → popup "About to occupy
the empty <Type> Battlefield — costs no challenge attempts" → **Occupy** `(744,1340)` → wait ~3–5 s: if you already held a spot, a *Resource* popup ("you left the old
Battlefield", gains from it) appears → **Confirm** `(540,1460)`. Moving to an empty spot is free, so it's fine to
move later — but pick the empty spot first anyway (saves an attempt).
The map opens scrolled to your current area, and empty platforms were found just below the Gold rows.

Taking a spot: tap the spot → popup "<Type> Battlefield", Occ. Gains, "Use 1 challenge attempt" → **Challenge**
`(742,1334)` (Cancel `(336,1334)`) → lineup (top 5 pre-selected, keep) → **Start** `(540,1808)` → battle ~10–45 s
(poll; it may return straight to the map with no Victory screen — check the header) → *Victory* → tap anywhere `(540,1500)`.

**Take a new spot every run, even if you already hold one** (Nick, 2026-10-27) — a held spot doesn't count as
done. Pick by the rules below; done once the header shows the newly taken spot. Never spend gems on attempts.

- **Mon–Fri:** take a **purple (9/m) spot**. Prefer an **empty** one. If none is empty, attack a purple
  spot held by someone **not** in our tribe (purple name background; cross-check `accounts/tribe_peakaboo.txt`).
  Never attack a blue-name (tribe) player.
- **Sat–Sun:** take **Glory** and **Gold** spots **only if they're free/empty** — never attack for them.
  If no Glory/Gold spot is free: go for a **purple/silver** spot — prefer a **free** one; if none is free,
  attack one held by a **non-tribemate** (purple name background). Never attack a blue-name (tribe) player.
- Never spend gems.

**Occupation lasts 8h** ("Collect Time 08:00:00"), then ends on its own: on the next visit a *Resource* popup
shows the gains → **Confirm** `(540,1460)` → dismiss `(540,1210)`; header shows "Unoccupied" → take a spot again.
Spots fill within seconds when several workers run at once — re-screenshot before tapping.
Swipe slowly (`540 700 → 540 1500`, 1500 ms) to come back up; fast swipes fling far.

**Points Reward:** left-side **Rewards** `(88,745)` with a red dot → **Claim Reward** `(540,1618)` (free) →
dismiss `(540,1880)` → close ✕ `(972,240)`.

Tribe chat pinned notice (Peakaboo, 2026-10-27): "Canyon: Move to 8/m if you reached 80k early. Dont attack
people not 80k yet." — not yet reflected in the rules above; ask Nick.

## Poseidon's Ruins (Tribe, 3 attacks)

Added by Nick 2026-10-26; mapped on xFaktor via ADB (device coords). Skill: `miniheroes-poseidon`.

1. Main screen → **Tribe** `(448,1780)` → **Poseidon's Ruins** card `(540,1440)` (red dot = attempts left;
   "In Battle: hh:mm:ss") → Loading ~3 s → battle map, **Enemies** tab selected (Allies/Enemies at the bottom).
2. Header: **Attack Attempts N** top-left (3/day on xFaktor). Ignore Report / Rewards / Contribute.
3. Enemy ships in rows of 3, sorted by CP high → low (big ships first, rowboats at the bottom). Each shows
   name + CP and 3 hearts: **red** = alive, **grey + fire** = sunk. Scroll with `input swipe 540 1500 540 700 800`
   (~3 swipes reach the bottom). Sunk ships move down the list after a fight.
4. Pick the **lowest-CP ship with a red heart** → tap the ship → *Plunder* popup ("Consume 1 attempt") →
   **Attack** `(742,1336)` (Cancel `(336,1336)`) → lineup pre-selected (top 5, keep) → **Start** `(540,1808)`
   → fight ~8 s → *Victory* → tap `(540,1700)`. Back on the map: attempts −1, target −1 heart.
5. Repeat on the same target until attempts = 0; if it sinks or is being attacked, take the next-lowest
   ship with red hearts. Tribemates attack live — hearts change between screenshot and tap; the Plunder popup
   shows the current hearts, so re-check there.
6. Back `(92,1810)` → Tribe screen. Red dot on the card gone = attempts used.

**Being attacked** (Aminor/Dminor/Chien Than, 2026-10-26): **crossed swords** over the ship in the list; tapping it
shows a toast "This player is being challenged" (vi: "Người chơi này đang bị khiêu chiến") instead of Plunder.
If the target sinks while you're on the lineup, **Start does nothing** — back `(84,1810)`, no attempt is lost,
pick the next ship. Lineup cards can render black for a moment; Start still works.

Start-up: loading screen Start `(540,1510)`; close event banners/promos (✕ `(806,742)`, "Stargems Running Out!"
Cancel `(337,1281)`). First Tribe tap right after the main screen appears may be ignored — retry once.

2026-10-26: xFaktor 3 wins vs Vimax (494k); Dminor/Aminor/Chien Than 3 wins each on the lowest ships (Mero.,
убиватор, Noble); Cmajor had 0 attempts. 20000 + 500 + 1 badge per win.

## Storm Battlefield (right after Pet Arena)

Added by Nick 2026-10-26; mapped on Cmajor via ADB (device coords). Free tickets only.

**Season: opens Monday 17:00, closes the next Monday 05:00** (like Canyon Clash). Tue–Sun: part of the normal
dailies. Monday: closed until 17:00 — run `/catch-up` after that.

1. Main screen → **2nd event card** (top right, y≈480). It rotates every few seconds (Storm Battlefield /
   Dragon Temple…); swiping it doesn't work — wait until it shows **Storm Battlefield** (gold card), then tap
   `(880,480)`. Event screen tabs at the bottom (Storm Battlefield / Dragon Temple).
   **Monday ≥ 17:00 with the game already running since before 17:00: restart the game first**
   (`am force-stop com.and.brawlen.web` + relaunch) — otherwise the Storm card never shows (Nick, 2026-10-26).
2. **Always start with a full lineup** — the previous run left only 1 hero (step 6). First time (CP 0):
   **Deploy** `(540,1220)`; later runs: **Lineup** `(960,1600)` on the arena screen. Then **Quick Deploy**
   `(984,1800)` (top 5) → **Save** `(540,1808)` → back `(88,1812)` (→ **Start** `(540,1220)` if on the
   welcome screen). Verify the CP is the top-5 value before the first Start Match.
3. Arena screen: tickets `N/5` at `(540,1428)`. **Start Match** `(540,1610)` → matches vary: some are instant (~5–8 s), close ones are
   real fights (~60–80 s) — poll until the arena screen is back → *Victory/Defeat* → tap `(540,120)`. Repeat until 0/5.
4. **Free tickets — one visit of the + popup per run** (Nick, 2026-10-26). `scripts/storm.py` does steps 3–4: plays
   until 0, then (popup opens itself on Start Match at 0, or via **+**) taps the **left green button** until it's grey.
   Three looks, any language: **Free / Miễn phí** (pass accounts, instant), **Claim / Nhận** with a camera icon
   (no pass → real video ad, Mintegral `MBRewardVideoActivity`), or grey "Chances: 0" = done. Never
   **Diamonds Redeem** (price varies per account: 30 / 50 / 150 gems). Ads: wait for the video to end (~35 s), then Android **Back** (`keyevent 4`) closes the end
   card and grants +1 — Back mid-video aborts with no reward (chance not used). Never tap the ad body/Install.
   Then close `(100,1150)`, play the new tickets; next time tickets hit 0 → close the popup and stop.
   Button state: sample `(260,1250)` — green (123,206,49) / grey (181,178,181). `(260,1274)` hits the "Free" text or
   the camera icon: that made storm.py miss the ad popup, "dismiss" it as a Victory and count fake 5 s matches.
5. **Rewards** `(96,880)` (left side) — if it has a red dot: *Rank Reward* tab lists King/Glory/Gold/Silver/Bronze
   rows; tap a reached rank's highlighted item (Bronze `(372,1404)`, Silver `(372,1180)`) → claims the whole row (checkmarks) →
   dismiss `(540,1900)`. *Ranking Rewards* tab = end-of-season table, nothing to claim. Close ✕ `(972,228)`;
   the red dot should be gone.
6. **Lineup** `(960,1600)` → quick-remove ↺ `(1006,1084)` (clears all) → tap only the **first** hero card
   `(140,1250)` (highest) → **Save** `(540,1808)` ("Successfully saved"). Done.

2026-10-26 Cmajor: 5 + 2 free = 7 matches, Bronze V → III.

Tickets regen 1 per 2h (timer under the counter) — one can arrive right after storm.py stops.

**Open question (2026-10-27):** Aminor's Canyon spot showed 1043k CP = the 1-hero Storm lineup, while
tribemates' spots show 2.7–4.9M. If Canyon defence uses the Storm lineup, step 6 weakens it — ask Nick.

## Gotchas from Cmajor dailies (2026-10-27, 2nd run of the day)

- Fishing *Order Refresh* confirm: chaining the "Do not remind me today" tick `(390,1380)` with Confirm didn't
  stick (confirm kept reappearing). Tap the tick alone, screenshot, then Confirm `(757,1211)`.
- Fishing order rewards (step 17) verified: Order Info → yellow **Claim** at `(849,704|1058|1412)` → dismiss
  `(540,1880)` → +50/60 hammers each.
- Cmajor hero: gear slot 1 `(117,400)`, Enhance `(540,1384)` (not 360/1395); costs gold only.
- Grocery `grocery_buy`: Sanctuary tile 12 = 10000 coins, more than a day's balance (~6000) → usually skipped.
- Event claim lists (Heroic Trial / Canyon Warrior): the top Claim `(896,1024)` rolls to the next row after each
  claim; repeat while pixel `(820,1024)` is yellow (255,182,16), dismiss `(300,200)` between taps.
