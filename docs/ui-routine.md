# UI routines

All coordinates are in the **MuMu Android Device** game window's full-resolution frame
(704×1289), as used by `computer_app_click` on that window (ADB uses device coords — see below). Instance window ids change after
every restart — get a fresh one with `computer_app_list_windows`.

**Read only what you need:** `scripts/doc.sh <section> ...` prints the core sections (Speed, ADB, General gotchas)
plus the named ones, e.g. `scripts/doc.sh Arena Fishing "Divine Weapon"` (case-insensitive heading prefix match).
Each mission's gotchas live in its own section — add new findings there, never as a dated log at the end.

## Daily run order (Nick, 2026-10-26)

Run the missions in this order on each account:

Reviewed with Nick 2026-10-31 (`scripts/daily.py` ORDER is the source):

0. **Pet Arena** — **Mon/Tue/Wed only** (game days): join + Auto Deploy (see "Pet Arena"); first thing (Nick, 2026-11-02).
   `daily.py` step `pet_arena` since 2026-11-02.
1. **Fishing** — orders to threshold, Benefit (only if red dot), start Auto — first, so Auto runs during the rest.
   Don't collect order rewards here.
2. **Arena** — Ranking Rewards gift boxes, then use all tickets.
3. **Patrol** — **Claim All first**, then Speed Patrol until the price is 100 gems (don't buy that one).
4. **Arena** again — patrol loot refills the tickets.
5. **Storm Battlefield** (see "Storm Battlefield"), then its rank rewards. Skip on Mondays until 17:00 (`/catch-up` after).
6. **Shop** freebies.
7. **Play Pass** claims.
8. **Adventure**, top to bottom: Land of Trials → Tower of the Throne → Secret Sanctuary → Gate of Darkness → Beast Realm.
   Ancient Ruins is not part of the dailies (Nick).
9. **Arena** again, then the weekly win chests.
10. **Recruit** free summons.
11. **Hero** upgrade (after the potion-giving steps above).
12. **Tribe** — sign-in, Trial, chat Request + Assist, then **Canyon Clash** (empty spot + Points Reward; closed Mondays
    until 17:00). Poseidon's Ruins has its own skill; Crystal Throne isn't mapped.
13. **Divine Weapon** — Excelsior Veins, Forge, then Benefit (its milestones count the forging just done — Nick, 2026-11-04).
14. **Stage** run ×3 (skull bubble).
15. **Patrol** — Claim All only.
16. **Rune** synthesis.
17. **Grocery** — free chests, then the account's `grocery_buy` tiles (if any).
18. **Events** — see "Events (red dots)".
19. **Fishing** — the only place order rewards are collected (see Fishing step 7).
20. **Daily Mission** — the last mission (Nick, 2026-10-29); any new mission step goes before it. A rerun of earlier
    steps (`daily.py <acct> <step>...`) should include `daily_mission` so their progress gets claimed.
21. **Play Pass again** (`play_pass2`) — after the missions, only if the Play Pass icon has a red dot (≈`(156,443)`): the run's activity unlocks
    new claims (Nick, 2026-11-03). Same in the catch-up.
22. **Pet Arena check** (`pet_check`, Mon–Wed) — **catch-up only** since 2026-11-04 (Nick: removed from the dailies' last step,
    Auto Deploy is still running then) — Pet Arena → Achievement
    "Cumulative pet deployments completed: N" must be **+40 since yesterday** (= all 40 free attempts used; Mon: 40,
    Tue: 80, Wed: 120 when no day was missed). Short → Auto Deploy (re)started + MANUAL, the catch-up re-checks. While the
    Achievement is open it also claims every yellow Claim (milestones reached after the `events` step; Nick, 2026-11-03).

A "Match attempts full" popup can interrupt any step: **Confirm** (opens the Arena), spend every ticket (`arena.py`),
back to main, then redo the interrupted step — `flow.tickets_full()` + the runner do this (Nick, 2026-10-31).

Focus on the steps, not on resources: don't track gem/resource balances (they change all the time).
The only money check is reading the price on screen before any paid tap and respecting the config caps.

**Multiple accounts at once:** one worker (subagent) per MuMu instance, each with its own ADB serial and
its own scratch dir for screenshots; workers don't edit the repo — they report, and the coordinator
updates the docs. Set each instance to 1080×1920 first (see "Starting the game").

## Speed: `scripts/tap.py`

**Whole run: `D=<serial> scripts/daily.py <account> [step ...]`** — runs the Daily run order end to end from the
main screen, one OK/SKIP/FAIL/MANUAL line per step, ending with `LEFT FOR HELPER: …` (see the dailies skill).
Steps: pet_arena (Mon–Wed) fishing arena patrol arena2 storm shop play_pass trials tower sanctuary gate beast arena3 recruit hero tribe divine
stage patrol_claim rune grocery events fishing_rewards daily_mission play_pass2 (`pet_check` = catch-up only).
**Run overview: `scripts/summary.sh <run dir>`** — per account OK/SKIP counts, FAIL/MANUAL/paid lines, LEFT FOR HELPER (one call instead of grepping logs).

Use `D=<adb serial> scripts/tap.py x,y [x,y ...] [-o out.png] [-w 270|540]` for every tap (device coords):
it waits only until the screen changes and settles (~1 s per tap, max 4 s) instead of a fixed sleep,
and saves a screenshot `-w` px wide (default 540: coords ×2 for device; 270: ×4). No args = screenshot only (~0.4 s).

- `-w 270` for navigation, `-w 540` to read small text or place taps on small/bottom-row icons (270 math misses there).
- Chain known taps of a flow in one call; screenshot-check only at decision points (prices, counters,
  unexpected popups). Always check the current screen before the first tap of a flow.
- Taps with no visible effect return after ~1.5 s (`NO_CHANGE`), not the full `MAX_WAIT` — but they can still
  register late (Bino: Level Up tapped twice = +2 levels). Re-screenshot after ~1.5 s before retrying a tap that "did nothing".
- Waiting for something (battle end, button back): `scripts/tap.py [taps] --until x,y,r,g,b[,tol] --timeout s`
  polls every ~0.3 s and returns the moment that device pixel matches — no fixed sleeps, no 10–15 s polls.
- **Wait on the next screen's text: `--until-text REGEX`** (OCR, default timeout 10 s; 2026-10-29). It prints the
  screen's text, which is often enough to decide without reading the png. Every navigation tap gets an `--until`
  or `--until-text`; a bare screenshot only at a real decision. Known hops (texts the runner itself waits on):

  - back `92,1810` (full screens) → main: `--until 92,1788,0,158,230`
  - Adventure is a side panel: close ✕ `944,1800` → main (`92,1810` there is the Beast Realm card)
  - main → Adventure `100,1460`: `--until-text 'Tower of the Throne'`
  - Adventure → Sanctuary GO `787,962`: `--until-text 'Sweep|Recovery'`
  - main → Match/Arena `100,1280`: `--until-text 'Ranking|^Lineup$'`
  - main → Tribe `448,1780` → Canyon `540,1090`: `--until-text 'Attempts'`
  - main → Fishing `624,1780`: `--until-text 'Order Info'`
  - main → event hub `896,340`: `--until-text 'Match|Weekly'`
  - main → ☰ `994,1625` → Grocery `900,1230`: `--until-text 'Daily Specials'`
  - main → ☰ `994,1625` → Backpack `900,1775`: `--until-text 'Backpack'`
  - reward / claim tap: `--until-text 'Tap anywhere|Congratulations'`
  - battle Start: `--until-text 'Victory|Defeat|Tap anywhere' --timeout 180`

- Storm matches: `D=<serial> scripts/storm.py` (plays until tickets run out incl. one free-ticket claim, ~0.5 s polling;
  exit 1 = unexpected screen, screenshot and report — don't re-run it in a loop).
  Grocery: `scripts/grocery.py`; Fishing orders: `scripts/fish_orders.py`.
- **Arena: `D=<serial> scripts/arena.py <account>`** from the Arena screen (crashes until tickets 0, closes the dialog);
  **Land of Trials: `D=<serial> scripts/trials.py <account>`** from the Land of Trials list (all dungeons, free then paid
  within the cap). Both read the screen with OCR (`scripts/ocr`, macOS Vision) and print one line per
  action; exit 1 = unexpected screen → read `v_arena.png` / `v_trials.png` and finish that mission by hand.
  Use them instead of the manual steps below (Nick, 2026-10-28: Arena ~117 + Trials ~75 helper turns/account).
- Same pattern, all from the **main screen** (`scripts/flow.py` = shared OCR helpers): `patrol.py <account> [--claim-only]`,
  `hero.py <account>`, `tribe.py` (sign-in, Trial if red dot, Request + Assist; ends on Tribe chat),
  `adventure.py <account> tower|beast` (ends on the mode screen). Exit 1 → `v_<script>.png`, do it by hand.

## ADB alternative (no computer use)

Works without computer-use tools. Device frame is **1080×1920**; the rest of this doc uses
window coords (704×1289) only for Land of Trials — with ADB use the device coords below (verified 2026-10-26). Get the instance's current ADB port from
`"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all` (ports change).

```
adb connect 127.0.0.1:<port>
adb -s $D exec-out screencap -p > s.png   # read it before every tap
adb -s $D shell input tap X Y
```

Device coords (Land of Trials): safe dismiss `(540,120)`; sweep dialog ✕ `(972,572)`;
Sweep `(540,1372)`; Tip Confirm `(540,1162)`. List scrolled to bottom (swipe `540,1600→540,400`):
GO Battlefield `(870,630)`, Forest `(870,1016)`, Temple `(870,1402)`, Gem Mine `(870,1786)`.
List at top (swipe `540,500→540,1500`): GO Abandoned Mine `(870,540)`, Ancient Battlefield `(870,925)`,
Forest `(870,1310)`, Temple `(870,1696)`.

## General gotchas

- **Scroll lists slowly, never fling** (Nick, 2026-11-03: "you keep swiping past the packs"). The game's lists keep
  gliding after a swipe (a 680 px swipe moved ~1300 px) and OCR of a moving list puts taps at stale spots. Use a
  held drag (`drag()` in daily.py: DOWN, MOVE, pause, UP — moves ~60 px less than asked), then wait for it to settle.

- **The game UI is English on every account** (Nick, 2026-10-28). The scripts match English button text.
- **Screenshot coords ≠ device coords** — scale both axes (×2 from 540 wide, ×4 from 270). Workers keep
  mis-tapping by passing screenshot coords directly; a y-only miscalc makes taps miss silently.
- **Taps during animations are ignored.** Popups slide in; after opening one, take a screenshot,
  then tap. Confirm the result with a screenshot or a `--until` pixel check — never chain taps blindly.
- **Safe dismiss tap:** `(540,120)` device (window `(352,140)`) — the title area; does nothing if no popup is open.
  On Grocery / Patrol / Fishing reward popups use `(540,1880)` (very bottom) instead — `(540,120)` can close the screen.
- **Back arrow `(92,1810)` sits on top of the main screen's Recruit button.** A back tap that lands after the
  screen changed opens Recruit — screenshot after every back tap; on Recruit just tap back again (never Recruit 1/10).
- **On-screen counters are the truth**, not red dots or the plan: Tower / Sanctuary had no red dot but weren't done
  (Cmajor); some modes were already done earlier that day (Bino). Always open and read the counter.
- **Accounts without a Play Pass get video ads where others get Free** (camera icon / "Purchase Play Pass to skip
  ad"): Storm free tickets, Common Recruitment, Grocery chests 2–4, Wish Festival Gift Free Pack. Ads are ~37 s,
  Android Back does nothing mid-video, skip/close appears top right ≈ `(990,90)`. Not a routine — skip and report
  (except Storm, which storm.py handles). Bino has a pass since 2026-10-27; Dino's claims were plain too.
- Unmapped, leave alone: Adventure → Ancient Ruins (red dot), main-screen "Mars's Gift".
- A `swipe` once failed with `INJECT_EVENTS permission` and the game was back on the main screen — screenshot and re-navigate.

## Starting the game

**Scripted (preferred):** `scripts/boot.sh <mumu index>...` — does all of the below via ADB in parallel and prints
the serials. Measured 2026-10-27: Start button is up <1 s after launch, main screen ~5 s after Start (no 40 s waits).
Main-screen check pixel: Recruit icon `(92,1788)` ≈ `(0,158,230)`; Start button `(440,1508)` ≈ `(255,182,16)`.

1. In **MuMuPlayer**, press ▶ on the instance row (if not running). Wait for the Android home
   screen.
2. Tap the **Mini Heroes** icon `(352, 190)`. Loading screen → tap **Start** `(352, 1022)` (device `(540,1510)`).
3. Event popups may appear on the main screen — close with their ✕, then screenshot to confirm the main screen
   (Adventure button bottom-left). Seen: Pet Arena ✕ window `(524,520)`; event banner ✕ `(806,742)`;
   "Stargems Running Out!" / promo → **Cancel** `(337,1281)`; 2nd Anniversary promo ✕ ≈ `(988–1006, 322–348)`.
   **"Do not remind me today"** checkbox under a popup (e.g. 2nd Anniversary, ≈ device `(390,1675)`) → tick it
   first (green ✓), then close with ✕ (Nick, 2026-10-28). Never GO.

- Instances with a 600×1080 display: `adb shell wm size 1080x1920 && adb shell wm density 480`, restart the
  game → all device coords here apply. Undo with `wm size reset` / `wm density reset`.
- The first tap on the main screen right after loading is often ignored — retry once, then screenshot (a late
  second tap can open a ranking profile; close by tapping outside, e.g. `(900,1500)`).
- Crash → relaunch: `monkey -p com.and.brawlen.web …`, Start `(540,1508)`.

## Land of Trials

**Run `scripts/trials.py <account>` from the list screen** (see Speed); the steps below are for its exit-1 fallback.

Sweep exactly the configured total per dungeon, then move to the next — `max_gem_price_per_sweep` is only a
safeguard (Nick, 2026-10-29/11-03). **Read the next price on the Sweep button itself** (gem icon + 80/160/240) before
tapping: it tells both the price and how many were already bought today (80 = 0, 160 = 1, 240 = 2). Needing to tap
Sweep and see the Tip to learn the price or the limit = something is wrong (Nick, 2026-11-03). The Tip is only the
Confirm of a purchase you already decided; its price must equal the button's.

Path: main screen → **Adventure** `(66, 984)` → **Land of Trials** card, `GO` `(516, 306)`.

Screen header: "Free attempts refresh in: HH:MM:SS" (daily reset).

Dungeon list (scroll position = top; scroll by dragging `(352,1100)→(352,300)` to reveal Gem Mine):

| Dungeon             | `GO` tap (top of list) | `GO` tap (scrolled to bottom) |
| ------------------- | ---------------------- | ----------------------------- |
| Abandoned Mine      | `(568, 390)`           | –                             |
| Ancient Battlefield | `(570, 640)`           | `(570, 448)`                  |
| Mysterious Forest   | `(570, 892)`           | `(570, 698)`                  |
| Moonlight Temple    | `(570, 1142)`          | `(570, 950)`                  |
| Gem Mine            | –                      | `(570, 1200)`                 |

The card shows `Attempts: N` (free left) or `Remaining purchases: N` (free exhausted).

### Sweep dialog

- Shows Difficulty (keep as-is — highest unlocked, currently 35 on Cmajor), Stage Reward,
  and one of:
  - **"Challenge Attempts: N"** + plain yellow **Sweep** button → free sweep.
  - **"Remaining Purchase Attempts: N"** + **Sweep** button with a gem icon and price
    → **paid** sweep. Price escalates per dungeon per day: 80, 160, 240, … (one purchase each).
  - Tapping a paid **Sweep** opens a _Tip_ popup "Spend N diamonds to purchase 1 challenge
    attempt?" → **Confirm** (window coords unverified, ≈ `(352, 790)`; device `(540,1162)`)
    only _buys_ the attempt; the dialog then shows "Challenge Attempts: 1" and you tap
    **Sweep** again to actually sweep.
  - Gem Mine's reward popup animates for a few seconds; wait before dismissing.
- **Sweep** button: `(352, 932)` once the dialog has settled.
- Close dialog ✕: `(632, 408)` (device `(970,570)`, may need a second tap).

Gotchas:

- Each free sweep = two taps (Sweep, then dismiss _Congratulations_); a paid one = four (Sweep → Confirm → Sweep → dismiss).
  The reward popup auto-closes after ~3 s — a dismiss tap after that hits the list behind (opened the next dungeon once),
  and `(540,120)` can close the whole dialog. Sweep → wait 7–8 s → dismiss once at `(540,700)` (device).
- Wait ~1.5 s after the dialog opens / after buying, or the Sweep tap is lost.
- After a paid Confirm the screenshot can look stale although the purchase went through — re-check
  "Challenge Attempts: 1" before tapping again, or you can **double-buy** (Aminor).

### Algorithm per dungeon

```
target = config total sweeps (free + paid)
open dungeon dialog; screenshot
done = 0
while done < target:
    screenshot dialog
    if "Challenge Attempts: N" (N>0): free sweep
    elif "Remaining Purchase Attempts":
        read gem price on the Sweep button → done today = 2 + price/80 − 1; done ≥ target → next dungeon (no tap)
        if price > max_gem_price_per_sweep → stop that dungeon (safeguard), report
        tap Sweep → Tip popup (price = the button's) → Confirm → now "Challenge Attempts: 1"
    else: stop, report unexpected state
    tap Sweep (352,932); screenshot → expect Congratulations; dismiss
    screenshot → verify counter decreased (or switched to purchase mode); done += 1
close dialog (632,408)
```

If the config count is lower than the free attempts available, do only the configured number.
Keep track of sweeps already done today (e.g. from a previous run) — the on-screen counters are
the source of truth: free used = 2 − remaining free; paid used = 5 − remaining purchases
(Cmajor, 2026-10-26: 2 free, 5 purchasable per dungeon).

## Arena

Renamed from "Match" (Nick, 2026-10-29) — the main-screen icon is still labelled **Match** in game.
**Runner step `arena` claims the Ranking Rewards gift boxes first, then runs `scripts/arena.py <account>` from the Arena screen** (see Speed); step 6's win chests = end of the same `arena` step, same visit (reads the win count, taps reached chests without a green ✓). Steps 1–5 below are arena.py's exit-1 fallback.

Mapped 2026-10-26 on Cmajor via ADB. **Device coords (1080×1920)**; window coords not mapped yet.

Goal: spend every free ticket crashing the **topmost attackable** opponent (not in our tribe) — Nick, 2026-10-27.

1. **Tribe roster:** members are fixed (Nick, 2026-10-26). Use the saved list in `accounts/tribe_<name>.txt`;
   only read it in-game if that file doesn't exist yet (then save it). Main screen → **Tribe** `(448,1780)`
   → **Member** `(192,474)` → read all names (29/30 on Peakaboo; scroll with
   `input swipe 540 1550 540 750 1500`). Close ✕ `(972,238)`, back arrow `(98,1808)`.
   Tribemates also show up in Arena (e.g. Morrígan, Zues, Aminor on 2026-10-26) and their names look like
   everyone else's (no blue tag) — cross-check the roster by name.
   To check a single opponent: tap their avatar in the Challenge list → profile shows `Tribe: …`.
2. Main screen → **Match** icon `(100,1280)` (badge = tickets left; the icon keeps a red dot at 0 tickets — read the
   badge) → Arena → **Challenge** `(540,1594)`.
3. Challenge dialog: tickets `N/8` top-left (can exceed the cap after rewards, e.g. "Full" 7/6). Rows, each with
   CP and a button at x=`866`, y ≈ `559, 796, 1033, 1267, 1504` (row 1–5). The list can have only 1–2 rows.
   A 6th row can be cut off: swipe `540,1500→540,900`, then Crash ≈ `(866,1652)`; rows shift ~+100 px after
   scrolling — re-read the screenshot before tapping.
   - Blue **Crash** = instant win vs. a weaker opponent (1 ticket). Use these.
   - Yellow **Challenge** = real fight vs. a stronger one. Not used.
   - A crashed row turns into a shield timer (tapping it does nothing) — re-read rows every round.
   - Don't touch `+` (buys tickets) or **Refresh** (cost unknown).
4. Pick the **topmost** attackable row (scan from row 1 down): blue **Crash** and name not on the roster → tap it.
   **The last row is always a bot — always attackable** (no tribe/server check needed); use it when no
   row above it qualifies, so tickets never go unused (e.g. Dminor's list is all its own server — still crash the bot).
   If the account has `arena.attack_tribemates: true` (Dino, Bino — Nick, 2026-11-04), use `accounts/own_accounts.txt`
   (Nick's own accounts) as the roster instead of the tribe list: tribemates are attackable, Nick's accounts never.
   If the account has `arena.skip_same_server: true`, also skip opponents on the account's own server
   ("S###" tag, or "War Zone: AreaNNN" on the opponent profile). Server unknown → skip.
   The dialog closes and shows _Congratulations_ (+40 arena points, 11000 gold).
   Dismiss with `(540,120)`, confirm the ticket count dropped by 1 on the Challenge button.
5. Repeat from step 2 until tickets = 0. The opponent list changes after every crash.

Weekly win chests (10/20/35/50 wins) along the top bar, 10 ≈ `(376,210)`, 20 ≈ `(536,210)`, 35 ≈ `(696,210)`,
50 ≈ `(864,210)` — free once reached.

6. **Claims (Nick, 2026-10-28)**, after tickets = 0 (wins may unlock a chest), on the Arena screen:
   - **Win chest** that glows gold (no ✓, reached) → tap it, claim, dismiss `(540,120)`. ✓ = already claimed; dull = not reached.
   - **Ranking Rewards** — done FIRST, on entering the Arena (Nick, 2026-10-29; runner `ranking_rewards()`):
     buttons at the bottom, Week ≈ `(568,1828)`, Day ≈ `(895,1828)`; a red **gift box** on the button's top-right
     corner (≈ x+113, y 1700–1790) = claimable → tap the button: it claims at once ("Congratulations — Rewards for
     attaining N place", no Claim button; Cmajor Day 2026-10-29: 100 gems, 2 relic shards?, 12 medals) → dismiss `(540,120)`.
     No gift box → don't tap it, not even to check (Nick, 2026-10-29). Arena back arrow `(120,1780)`; `(60,56)` opens Rules (close with `keyevent 4`).

**Interrupt: tickets full.** During any daily, a popup can say Match attempts are full. Its **Confirm**
(`(696,1162)`–`(740,1162)`) opens the Arena since 2026-10-29 (it used to only close it; `trials.py` now taps Cancel
and continues) — either way, go to the Arena, run the routine above until tickets = 0
(same tribe rules), and continue the daily you were on.

## Shop freebies (red dots)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Nick explicitly allows this one Shop task:
claim the **free** red-dot items only. Every other button in the Shop costs real money ($) — never tap them.

1. Main screen → **Shop** `(100,330)` (opens on Value Pack tab).
2. **Value Pack** → _Free Benefits_ row → **Claim** `(894,787)` (10 gems + 1000 gold; button
   becomes "Sold Out"). Dismiss with `(540,120)`.
3. **Hero Pack** tab `(480,1846)` → **Select Hero** `(895,420)` (red dot): just opening the dialog
   grants **20 gems**. Dismiss `(540,120)`, then close the dialog ✕ `(972,300)` **without picking a hero**.
4. Check every tab for a remaining red dot; back arrow `(92,1810)`. Shop icon's dot is gone when done.

## Play Pass claims (red dots)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free daily claims from cards Nick already
owns. Never tap a $ / purchase button. Weekly/Monthly cards may be unowned on some accounts.

1. Main screen → **Play Pass** `(100,500)`. Tabs along the bottom: Play Pass `(480,1846)`,
   Weekly Card `(648,1846)`, Monthly Card `(818,1846)`, Lifetime Card `(988,1846)`. Visit each tab with a red dot.
2. **Play Pass** tab: passive privileges, nothing to claim.
3. **Weekly Card** (bought, "Purchase to get" items ticked): tap today's highlighted **Day N** tile
   (Day 1 = `(203,1099)`; grid of 3 columns x≈203/540/877, rows y≈1099/1486) → 20 stars, tile shows "Claimed".
4. **Lifetime Card** → **Claim Reward** `(540,1658)` → 288 gems + 3 arena tickets, button turns "Claimed".
5. **Monthly Card not owned:** each "Points reached" row's left free-track item has its own yellow **Claim**
   (red dot, x≈830–896, scroll the list; rows shift as you scroll; dismiss `(300,200)`) — free. The green
   **"Continue to claim"** = the card track: free when its yellow box has **no padlock** (top-right corner, card owned —
   Nick, 2026-11-04; Cmajor got 10 shards + 2000 gold, gems unchanged); padlock = paid, never.
6. Dismiss every reward popup with `(540,120)`; back arrow `(92,1810)`.

## Tower of the Throne (3 daily challenges)

**Run `scripts/adventure.py <account> tower`**; steps below = exit-1 fallback.

Mapped 2026-10-26 on Cmajor via ADB (device coords). Goal: 3 challenges (`tower_of_the_throne` in the config; Nick, 2026-10-27).
Keep the pre-selected lineup (Nick, 2026-10-26: don't bother picking the weakest hero).

1. Main screen → **Adventure** `(100,1460)` → Tower of the Throne **GO** `(787,687)`.
   Ticket count top-left (10/day on Cmajor).
2. **Challenge** `(540,1805)` → lineup screen. **Bone Archer alone** (Nick, 2026-11-02: if 5 heroes are set, set only
   Bone Archer; never set them back): recall all `(1006,1082)` → archer filter `(670,1644)` → its card (skull; template
   `scripts/bone_archer.png`, scroll the grid) → filter back to all `(270,1644)`. `flow.lone_hero()` does it.
   **Any 1 hero already set → keep it**, no recall / archer search (Nick, 2026-11-04): `flow.one_hero()` reads idle
   motion over ~1 s, back slot x < 140 moving and slots 2–5 (x 180–500) still.
3. **Start** `(540,1808)` → result screen. Dismiss by tapping `(540,1700)` (below the
   "Challenge again" button — never tap that). Verify tickets dropped by 1.
4. Repeat steps 2–3 until the configured count is done (stop early if tickets hit 0).
5. **Treasure Chest Level** (all floors of a block cleared: "Remaining floor(s): 0", bottom button **Claim Reward**
   instead of Challenge): tap **Claim Reward** (free) → _Congratulations_ → `(540,120)` → the next floors open with
   **Challenge** → go on (Chien Than Floor 2030 → 2031, 2026-11-03; `adventure.py` `claim_tower`). It used to be
   skipped, which lost the Daily Mission "Challenged the Tower" row.

## Secret Sanctuary (sweep if offered, else climb 10 floors) — Nick, 2026-10-27

**Runner step `sanctuary`** (2026-10-29, tested on Cmajor floors 4–10): sweeps only on a **yellow** Sweep (the intro
shows a greyed one on a fresh map — it used to log a false "swept"), else climbs: next floor = node under the yellow
marker (`floor_marker()`: flags have yellow stripes too, told apart by their red ones); a far weaker floor wins on the
node tap itself (no popup, straight to the bonus screen); bonus/replace picked by the rules below via OCR. A loss → MANUAL.

Sweep only exists for a while after a full clear (Nick: ~7 days); when the map rotates (2026-10-27:
Ice Citadel → **Lava Cave**) there's no Sweep and you **attack from floor 1**. Mapped on Cmajor, ADB device coords.

1. Main screen → **Adventure** `(100,1460)` → Secret Sanctuary **GO** `(787,962)` → map.
   First time: "Bonus Effects" intro → Confirm `(540,1616)`.
2. If a plain **Sweep** `(540,1778)` shows: Sweep → _Tip_ **Confirm** `(533,1197)` → dismiss `(540,120)`. Done.
3. Else climb. Floor nodes (yellow marker = next), Lava Cave: 1 `(664,1440)`, 2 `(526,1210)`,
   3 `(786,1040)`, 4 `(552,956)`, 5 `(264,860)`, 6 `(502,786)`, 7 `(746,724)`, 8 `(630,574)`,
   9 `(414,506)`, 10 boss `(590,340)` (other maps: read the node off the screenshot).
   - Floor popup: yellow **Crash** `(540,1380)` = instant win (we out-power it) → _Congratulations_ → dismiss `(540,120)`.
   - Green **Battle** `(540,1380)` → lineup (HP **carries over** between floors) → if fewer than 5 ticked,
     **Quick Deploy** `(984,1800)` → **Start** `(540,1808)` → ~25 s → _Victory_ → **Confirm** `(540,1404)`.
     Wait with `tap.py 540,1808 --until 400,1404,123,206,49,25` (returns when the Victory Confirm shows).
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

## Gate of Darkness (2 chances/day)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Endless-wave mode; progress carries over.

1. Main screen → **Adventure** `(100,1460)` → wait for the list to finish sliding in (a tap during
   the animation opens an item-info popup; close it by tapping `(540,1400)`) → Gate of Darkness **GO** `(787,1238)`.
2. Screen shows "Chances left today: N" under **Start Challenge** `(540,960)`.
3. **First chance — run it:** Start Challenge `(540,960)` → lineup (default top 10, keep it) →
   **Start Challenge** `(540,1806)` → _Tip_ "Start challenge from Wave N?" → **Confirm** `(760,1164)`.
   **Never tap Restart** (resets wave progress).
   - **Time cap 3m (Nick, 2026-10-29)** from Confirm. If still fighting: **Pause** `(866,1227)` (may need a 2nd tap) →
     **Quit Battle** `(376,920)` (still counts as Victory) → **Confirm** `(540,1406)`.
   - If it ends earlier: _Victory_ (kill count + rewards) → **Confirm** `(540,1406)`.
   - A network-error popup sends the game to the loading screen — that run uses no chance, re-run.
4. **Second chance — Sweep** `(942,1058)` (appears next to Start Challenge after a run) → Confirm ≈ `(760,1370)`–`(770,1390)`.
5. Verify "Chances left today" dropped each time.

## Beast Realm (1 challenge/day) — Nick, 2026-10-27

**Run `scripts/adventure.py <account> beast`**; steps below = exit-1 fallback.

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
   **Confirm** `(540,1756)` / dismiss `(540,1700)` (wait ~2 s for the card flip). Do the configured 2 even when
   more chances show; some accounts/days only get 1. The Free button stays green at "Chances: 0" — read the counter
   ("Chances: 0" with no timer = done for the day). A cooldown (~5 min) shows between
   free chances; never pay.
3. **Ancestor Summon** tab `(896,1610)` → **Free** `(310,1355)` (red dot) → result → **Confirm**
   `(300,1755)`. **Never "Recruit 1"** on the result screen (spends a ticket). Button then shows
   "Free after HH:MM:SS".
4. **Artifact** bottom tab `(618,1840)`. **Auto** checkbox `(866,1658)` must be **unticked** (empty; ticked = green
   check — tap it; the old 1-pixel test at x 900 missed the check and Chien Than Auto-wished, Nick 2026-11-04). Re-check
   before every roll; a reward popup over it eats the tap (close it first). **Roll `recruit.artifact` times (5) WITHOUT Auto** (Nick, 2026-11-02): **Free** `(540,1638)` first, then
   **Wish** (stars) on the same button; dismiss each result (`(540,120)`, or Confirm on a new artifact). Never a button
   showing **280** (Brilliance tier gem price); gem count must not drop.

## Hero upgrade (Bone Archer +5 levels, 1st gear +5 — Nick, 2026-11-02)

**Run `scripts/hero.py <account>`**; steps below = exit-1 fallback.

Mapped 2026-10-26 on Cmajor via ADB (device coords). Costs potions/gold/stones only, never gems.

1. Main screen → **Hero** `(274,1810)`.
2. **Bone Archer** — find him by his **avatar**, not Lv / stars / position (Nick, 2026-11-03): expand icon above the
   strip `(1008,1400)` → **Marksman** filter (green bow) `(662,1800)` (the game keeps it; a 2nd tap keeps it on) →
   scroll to the bottom → his face (template `scripts/bone_archer_strip.png`) — usually last, not always (Bino: one
   Lv.160 after him) → tap → name top-left = "Bone Archer" → close the list ✕ `(1008,1100)`.
3. **Level Up** `(540,1178)` **`hero_levels` times (5)**, stop when out of potions → level +1 each (cost ~23000 potions). Its position shifts after
   the first tap ("↑ Lv.90" quick-level button appears above it at `(540,1060)`) — never tap that.
4. 1st gear (bow, top-left slot) `(117,360)` — or `(117,400)` (Cmajor, Tiger) / `(124,400)` (Kong) → popup
   "Swift Longbow LV.N » N+1", cost gold (+ stones). Open it **once** and tap **Enhance** `(540,1395)` / `(540,1384)`
   `gear_levels` times in a row (Nick, 2026-11-03), checking the button is still there before each tap (out of gold
   may pop a purchase dialog). Hero / gear levels themselves don't matter — Bone Archer is only for the dailies.
   Never the "↑ Lv.69" quick button or Reset (Rebirth + ↑ Lv.90 only in the out-of-potions case below).
5. Close popup `(540,120)`.

**Above Lv.135 → Rebirth + quick Lv.90** at the start of the hero step (Nick, 2026-11-03; `hero.py`). **Below Lv.90 →
quick Lv.90** (the gear is padlocked at low levels). A quick Lv.90 counts as 90 level-ups, so the daily "Leveled-up
any Hero" row is done — **no further Level Ups** that day, straight to the gear (Nick, 2026-11-03).

**Out of potions → Rebirth + quick Lv.90** (Nick, 2026-11-03; `hero.py` `rebirth_90`, mapped on Cmajor): only when
Level Up doesn't raise the level AND the potion line above Level Up shows have < need (e.g. `18M/30300` = enough —
Kong's Lv.170 stuck with `1557k/1351k` is NOT a shortage, don't Rebirth), and the hero is above Lv.90.

1. **Rebirth** (icon above its label, bottom-left ≈`(128,1170)`) → _Rebirth Preview_: free, "100% of the materials
   used during hero **and equipment** level up will be returned" — the gear resets to 0 too → **Confirm** (first tap
   during the pop-in is ignored; re-tap) → _Congratulations_ → `(540,120)`. Hero = Lv.1, gear slots padlocked.
2. **Level Up** once → Lv.2; the **↑ Lv.90** quick button appears above it `(540,1050)`.
3. ↑ Lv.90 → _Quick Level Up_ "Lv.2 → Lv.90", potion cost (`19M/1328k`) → **Confirm** `(740,1160)` → Lv.90, gear
   slots unlocked at LV.0 (the gear step then enhances from 0).

## Tribe (sign-in, Tribe Trial, chat request/assist)

**Run `scripts/tribe.py`** (steps 1–4); steps below = exit-1 fallback.

Mapped 2026-10-26 on Cmajor via ADB (device coords). All free.

1. Main screen → **Tribe** `(448,1780)`.
2. **Sign-in** `(538,476)` (same row as Member `(192,474)`) — already signed today = just a "Signed-In" toast, no dialog
   (Kong 2026-10-28; don't tap the dialog-close spot then, it's on a card) → **Sign-in Reward** `(538,1546)` →
   dismiss `(540,120)` → close the dialog by tapping `(540,1680)`.
3. **Tribe Trial** card `(540,735)` (no red dot = already done, skip — Challenge still starts a "No Rewards" fight)
   → Flame Lord boss → **Challenge** `(540,1806)` → lineup screen.
   The 5 heroes on the field are this mode's preset lineup; keep it → **Start** `(540,1806)`.
   Timed boss fight (~1 min, runs on its own). Poll and Confirm `(540,1483)`
   as soon as _Challenge Complete_ shows — never wait blind longer than ~80 s.
4. Back `(92,1810)` → Tribe screen → **Chat** `(800,1806)` (opening it auto-claims assist rewards) →
   **Request** `(174,1631)` (red dot; may need a 2nd tap at `(174,1636)`) → _Help Request Info_ dialog:
   - **Request** `(334,1660)`: send our own help request (greyed with a cooldown timer if already sent).
   - **Assist** `(740,1660)`: helps every listed request at once; list empties.
   - Close ✕ `(968,228)`.
     Back from Chat usually goes straight to the main screen — but can land on Recruit; screenshot and back again.
     Aminor (2026-10-27): helper found only the compose-bar Request and per-line "A" (translate) icons, no Assist
     — re-check Aminor's chat layout.
5. Never type or send chat messages.

## Fishing (orders, benefit, auto fish)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Done = auto fishing started; leave it running.

1. Main screen → **Fishing** `(624,1780)`.
2. **Order Info** `(190,786)` → _Daily Order_ dialog: 3 orders, refresh-ticket count top-left.
   Tier = filled diamonds (5 max): 1 common, 2 rare, 3 legend, 4 mythic, 5 eternal (name turns red at 4+).
   Target per account: `missions.fishing.min_order_diamonds` (Cmajor: 4 = Mythic+).
3. Refresh buttons x=`849`, y = `704 / 1058 / 1412` (orders 1–3). Costs **1 refresh ticket**. _Order Refresh_
   confirm "Confirm to refresh orders? Cost x1" → **Confirm** `(757,1211)`. Never tick "Do not remind me today".
   "The order is of high quality, continue to refresh?" = something's wrong (we'd refresh a good order) → **Cancel**
   `(320,1212)` and report (Nick, 2026-10-29).
   Automate with `D=<serial> scripts/fish_orders.py ROW MAX MIN` (MIN = `min_order_diamonds`, default 4; pixel check
   on the diamonds; row y = 567/921/1275, diamond x = 633/706/778/851/921; filled = R>200, empty = (58,85,115)).
   It handles both popups itself (WARN line on high quality) and returns `None` on any other popup (e.g. out of tickets).
4. Out of tickets: **buy as many packs as needed** until every order reaches `min_order_diamonds` (Nick, 2026-11-03:
   "unlimited, buy as lacking, don't care about price" — always 50 gems). A Refresh tap with 0 scrolls opens the
   _Order Refresh Scroll_ popup (also `+` `(272,425)` next to the count): **5 scrolls**, price above the button →
   **Purchase** `(540,1203)`; the popup stays open, close by tapping `(540,1600)`. The scroll count (left of `+`) must
   go up after each buy — else stop (runner `buy_scrolls()`; price only logged).
5. Close ✕ `(973,270)`. **Benefit** (runner: `fishing` step, 2026-10-29) `(330,1800)` **only if it has a red dot** — no red dot = don't open it → **Claim Reward** `(540,1662)`
   (60 bread, 5 refresh tickets, baits) → dismiss `(540,120)` → close ✕ `(970,238)`.
6. **Auto** `(982,1222)` → _Auto Fish_ settings (keep as-is: Auto-submit Orders ✓) → **Start** `(540,1485)`.
   Button becomes "Auto Fishing". Leave it.
7. **Order rewards (end of run only):** Order Info → a completed order shows a yellow **Claim** where Refresh
   normally is (`(849, 704|1058|1412)`) → tap → dismiss `(540,1880)` (+50/60 hammers each). Orders keep completing
   while Auto runs.

Auto stops on its own when bread runs out ("Insufficient Bread", screen shows "Tap water surface to start Fishing")
or on "Stop at new Archive". **Start Auto once per run (step 6).** Never tap Auto while the button reads "Auto Fishing"
(it's running). At the end of the run, restart it only if it stopped for "Stop at new Archive" — not for no bread.
Accounts without the fishing pass (Cmajor, Kong, …) get no daily bread → stopping at 0/100 is expected.

## Divine Weapon (benefit + Excelsior Veins)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free.

1. Main screen → **Divine Weapon** `(798,1780)` → Arsenal.
2. **Benefit** `(309,1810)` (red dot) → **Claim Reward** `(540,1662)` (1500 crystals, 2 potions,
   2 embers) → dismiss `(540,120)` → close ✕ `(970,238)`. Accounts without the forging pass ($8.99) have no Benefit. Do it **after** Forge (step 5): the Benefit milestones ("Divine Weapon dismantled N times") count the
   dismantles the forging just made (Nick, 2026-11-04); `daily.py` claims every Claim Reward there.
3. **Excelsior Veins** `(980,1810)` → mining grid. Attempts = pickaxes `N/80` (bottom centre;
   regenerates over time). Keep the "Automatically advance to next floor" tick as-is.
4. **Run `D=<serial> scripts/veins.py`** on the grid — it does the loop below and stops at the first buy popup
   (Bino 2026-10-28: a hand-written loop kept tapping 42x past 0 pickaxes, each time opening the 120-diamond buy popup).
   By hand: **One-Click Mining** `(896,1612)` → _Congratulations_ → dismiss `(540,120)`. Repeat until pickaxes = 0
   (pickaxes found in the mine are added back: 1–6 taps). At 0 it opens "120 diamonds for 5 pickaxes" → close ✕ `(938,636)`.
   Don't use the dynamite / drill items or the `+` on the pickaxe (buys more).
   The Veins back arrow returns to Arsenal, not the main screen.
5. **Forge** (Arsenal, anvil "Forge N/M" `(540,1484)`, crystal cost below e.g. `6755/500` = owned/cost):
   N = filled slots, M = slots per account (7, 8, 13…); 0/M = idle. A timer above = a forge running — NOT a reason to skip: keep filling slots while N < M (Tiger 1/7 + timer, Nick 2026-10-28).
   Else each anvil tap fills one slot (500 crystals, ~4 h) — fill every slot, stop when full or crystals < cost.
   Crystals only, never gems. Queue ≈ `(60,1250)`. Dino's forge stopped responding at 4/8 (cause unknown) — skip after 2 tries.

## Stage (3 runs)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Daily: challenge the current stage `adventure_stage` times (3).

1. Main screen → blue **skull bubble** next to the hero `(994,964)` (not the stage map top-right).
2. Battle setup "Stage: X-Y" → **tab 1 = Bone Archer alone** like Tower (Nick, 2026-11-02, all accounts —
   breaks climb accounts' tab 1: re-set lineups + `climb.py --record` before a climb) → **Start** `(540,1806)`.
3. **Defeat** → **Challenge again** (shows ~3 s after) = back on the hero selection, lineup kept → **Start**; repeat
   until `adventure_stage` fights (Nick, 2026-11-03 — no close + re-open per fight). A **Victory** moves the stage on →
   close `(540,120)` and re-open from the skull. After the last fight close `(540,120)`. (Tower: still never
   "Challenge again" — it starts the next floor.)

## Stage climb (occasional, not dailies)

Nick sometimes leaves an account on the game's own auto stage climb. Auto stops after X-40 (a 3-wave boss; result
shows "Stage Reward" with no "Next Stage (Ns)" countdown) → main screen "Next chapter" `(992,970)` → skull `(994,964)`
→ Start `(540,1806)`. On Defeat, "Challenge again" (Nick, 2026-10-31). All automated:
`scripts/climb.py <account>... [--minutes N]` (runs ~9 min per call, re-run to keep watching; exit 1 = look).
**Before starting a stage, recheck the lineups** (Nick, 2026-11-02): screenshot tabs 1/2/3 and confirm the heroes, not just power — a mis-tapped swap + `--apply` matched powers with wrong heroes on Chien Than.
**No swap, no climb** (Nick, 2026-11-02): run the climb only if the account can swap (fresh `--record`, swap not failing). Can't swap → tell Nick, don't run; a failed swap (exit 2) = stop and report, never `--apply` + Start.

**3 losses in a row on one stage → swap lineups** (Nick, 2026-10-31; climb.py does it from `stage_lineups` cells — losing wave's team ↔ next tab, max 3 swaps per stage, then exit 2). Lineups +
what each is good for: `stage_lineups` in the account yaml — new account: `scripts/climb.py <account> --record`
(reads the green deploy checks, rows 1-4). Manual steps:

1. A setup opened via Challenge again keeps already-won waves locked and **doesn't save edits** — back `(80,1810)` to
   the main screen, skull `(994,964)` for a fresh setup.
2. Tabs 1/2/3 `(380|540|700,1088)`. The circular arrow `(1000,1080)` = **recall all** of the open tab (no swap button).
3. Recall both tabs, then tap the other team's cells into each (tapping a free card deploys it; locked = in another
   tab). Grid at top: row1 y 1250, row2 y 1480, cols x 136/336/536/736/936; row 3+ → swipe `540,1450→540,1210`
   (800 ms) and screenshot for its y. Check the tab's power equals the other team's old power, then Start.

## Patrol (claim all + speed patrol)

**Run `scripts/patrol.py <account>`** (`--claim-only` for the late Patrol step); steps below = exit-1 fallback.

Mapped 2026-10-26 on Cmajor via ADB (device coords). Order changed by Nick 2026-10-31: Arena (all tickets) →
**Claim All first** → Speed Patrols → Arena again (the loot refills tickets).

1. Main screen → patrol **bag** with timer, right side `(983,1463)` → _Loot_ dialog.
2. **Claim All** `(742,1590)` → _Congratulations_ (auto-closes) → dismiss `(540,1880)`. Patrol timer resets to 00:00.
   If that closed the Loot dialog, reopen the bag (step 1). _(Claim-first path untested, 2026-10-31.)_
3. **Speed Patrol** `(337,1590)` → _Tip_ "Obtain 4 hours of Patrol Gains" → price button `(540,1164)` →
   _Congratulations_ → dismiss `(540,1700)` → the Tip reopens with the next price.
   Prices per day: **Free, Free, 50, 100, …** (escalates). Keep claiming until the button shows
   **100 gems** — don't buy that one, stop (Nick, 2026-10-26). Read the price on the button every time.
4. Close the Tip ✕ `(936,638)`.

## Rune synthesis (1/day)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free.

**Runner step `rune`** (2026-10-29; precise picking 2026-11-03): finds red tiles + lock icons by pixel. **Decide
from the backpack, click precisely** (Nick, 2026-11-03 — misclicks on locked runes): the list keeps coasting ~1–2 s
after a swipe, so scan only a still frame (two equal grabs), skip every tile with the padlock on its top-right corner,
tap the tile's centre. A "Locked" reply means the scan was wrong → stop, never tap another tile to "try". Manual steps:

1. Main screen → menu ☰ bottom-right `(994,1625)` → **Backpack** `(900,1775)` → **Rune** tab `(868,1680)`.
2. Red (Mythic) runes: often on the first screen, else scroll (`input swipe 540 1300 540 700 800`) and **wait until
   the list stops** before reading it. Locked tile = small padlock on its top-right corner (screenshot at `-w 540` or
   full size; `-w 270` is too small to see it). Tap the centre of a tile **without** the padlock → popup shows
   **Synthesize** (`(540,1203)` with 4 stat lines; lower with more). Never tap the lock toggle in the popup.
3. _Synthesize Runes_ dialog → **Quick Equip** `(417,1668)` (fills 4 same-quality runes — it picks the
   lowest tier, e.g. 4 blue → 1 purple; that's fine) → **Synthesize** `(824,1668)` with ×1.
4. Result → **Confirm** `(540,1190)` → close ✕ `(972,560)` → close Backpack ✕ `(972,238)`.

## Grocery (free Daily Specials chests)

Mapped 2026-10-26 on Cmajor via ADB (device coords). Free only.

1. Main screen → menu ☰ `(994,1625)` → **Grocery** `(900,1230)` → _Daily Specials_ tab.
2. Top row = 4 free chests, **Free** buttons at y=`893`, x = `163 / 413 / 663 / 913`.
   Rows below have gem prices — never tap them.
   - Chest 1 Gold Coin Pack: 1 claim.
   - Chests 2–4 (Hero, Resource, Growth): **3 claims each**, ~5–8 s cooldown between claims.
3. **Run `D=<serial> scripts/grocery.py`** (colour-based; the popup's Free button moves per item —
   chest 1 `(540,1204)`, chests 2–4 `(540,1344)` — so it scans for the green button). It sometimes stops early
   (chests still green Free) or its last dismiss closes Grocery: reopen Grocery and re-run until all 4 show **Sold Out**.
   Manual: tap a chest showing **Free** → popup must say Free (never a gem price) → claim → wait ~4.5 s → dismiss
   `(540,1850)` (`(540,120)` can close Grocery). Popup Free pixel `(480,1344)`: green (123,206,49) = claimable,
   grey (173,178,189) = cooldown. Growth Chest gives +80 gems per claim; Resource Chest can roll +50.
4. **`grocery_buy`** (per account, optional; **runner step `grocery_buy`** since 2026-10-29 — OCR price/balance, price icon colour = balance icon, popup price = tile price): for each shop tab listed, buy each listed tile **once**. Tabs at
   y=546: Sanctuary `(452,546)`, Tribe `(732,546)`, Ruins `(980,546)`; swipe the tab bar `900→200` → Realm
   `(604,546)` (Tundra further). Tiles are numbered 1–12 left→right, top→bottom; price buttons at
   x = `163 / 413 / 663 / 913`, y = `893 / 1249 / 1605`. Purchase popup `(540,1203)`, dismiss `(540,1850)`.
   - Skip tiles already **Sold Out**, and tiles whose price is more than the shop's balance (top left) — report
     (e.g. Sanctuary tile 12 = 10000 coins, usually more than a day's balance).
   - The price icon must be that shop's own currency (the one next to the balance) — never gems or $.
     Compare the **whole** coin icon (mean of its coloured pixels, left of the number) with the balance icon — a single
     sample point hit the icon's edge and skipped Realm tile 4 every day from late Oct to 2026-11-03 (fixed, bought on Dino).
5. Close ✕ `(966,222)`.

## Events (red dots)

The 2–3 event banners top right of the main screen rotate and change (Wish Festival, 7777 Draws, Match Event,
Weekly Event, Pet Arena, Tribe Clash…). **Red dots only** (Nick, 2026-10-27): open a banner/tab only when it
shows a red dot (a glow/sparkle is not a red dot). Claim only **free** rewards (Claim / Free buttons); never a $
or gem price, never draw/spin with paid currency or event coins, never "Join" without a red dot.
**Collect only — never consume** (Nick, 2026-10-28): no Open All / draw / spin / open / use / exchange of any event
token, ticket, draw, coin or key, even free ones — just claim what's given. Back out
`(88,1812)` when no red dots are left.

- **Runner step `events`** (2026-10-28): hub tab red dots (box right-above each tab), Match Event milestones (Canyon Warrior `(160,320)`, Heroic Trial `(400,310)`, OCR'd Claim in the top row) and 7777's daily Claim; Wish Festival Sign-In/Gift and Weekly Event Free Benefits (2026-10-29: only yellow `Claim`/`Free` buttons); Pet Arena tab with a dot → MANUAL. Hub tabs at y=1840 **shift with the event set** — the runner finds them by label (Kong instance 2026-10-29: Wish 480, 7777 650, Match 815, Weekly 990). Sticky dots ignored: 7777 after its Claim, Wish Festival's Treasure Vault (coin draws). Hub dots are (255,0,74).
- **Event hub:** the 1st banner taps at ≈ `(896,340)` (y≈166–210 misses). Any banner opens the shared hub; use its
  bottom tabs (y≈1820–1850) instead of timing the rotation: Wish Festival `(300,1820)`, 7777 Draws `(648,1850)`,
  Match Event `(860,1850)`, Weekly Event `(1000,1850)`. Banners rotate between screenshots.
- **Pet Arena:** Pack `(88,370)` (dot ≈ `(132,318)`) → Free Pack Claim (20 gems, Limited 1; never the $ packs) → ✕
  `(972,236)`; Achievement `(88,690)` → one Claim `(866,606)` claims all. Runner claims both (Pack since 2026-11-03 —
  it was documented here but never scripted, so it went uncollected).
- **Golden Woods** (2026-11-03; runner `golden_woods()`): sub-tabs King's Treasury `(165,300)`, Exploration Quest
  `(412,300)`, Sign-In Rewards `(660,300)`, Woods Expedition `(908,300)`; each sub-tab's red dot ≈ 63 px right of
  it, y≈190. Collect: **Exploration Quest** (one yellow Claim claims every quest row → Treasury Keys), **Sign-In**
  (today's yellow Claim; "Continue to claim" = $8.99 Deluxe → never), **Expedition gift** (icon top-left `(88,550)`,
  dot ≈ `(134,509)`, 20 gems). Never **King's Treasury** (Shuffle Cards spends keys; its "select the prize" dot
  sticks), Expedition **Draw** / Daily Pack ($). The hub tab's own dot sticks while keys are left.
- **Reward popups** ("Congratulations … Tap anywhere to close"): tap the **"Tap anywhere to close" line** — the popup
  centre is the reward icon and doesn't close it (`close_reward()`).
- **Unknown hub tab with a red dot** → the runner reports `MANUAL … unmapped tab <label>` (Golden Woods went
  uncollected on every account until 2026-11-03 because unknown tabs were invisible) → map it here + in `events()`.
- **Wish Festival:** Sign-In ≈ `(876,1500–1560)` → today's Claim `(862,1498)`; Gift `(270,1600–1660)` → Free Pack
  `(866,912)` ×2 (Limited: 2), close ✕ `(966,190)`. Treasure Vault = event-coin draws → skip.
- **7777 Draws:** daily Claim `(540,1606)` (collects 30 draws; shows a 30-hero-card result → **Confirm** `(540,1748)`) — then stop: **never Open All** / draw (Nick, 2026-10-28:
  collect only). Never "Again" / "claim one more time" — its red dot stays when all daily claims are ticked.
- **Match Event:** Heroic Trial sub-tab `(400,190)` and **Canyon Warrior** tab — free point milestones, Claim
  ≈ `(896,1024)`. The top Claim rolls to the next row after each claim: repeat while pixel `(820,1024)` is yellow
  (255,182,16), dismiss `(300,200)` between taps.
- **Weekly Event / Hero Recruit:** Pet Shop / Recruit Store sub-tab `(410,240)` → Free Benefits `(896,1024)`;
  weekly merchant free 200.
- **Tribe Clash** banner `(880,624)` → Pack `(976–994,1630)` → Free `(866,934)` (20 gems, 1/day). **Never its
  Treasures or "Enter"** (Nick, 2026-10-27). Its red dot can persist with nothing claimable.

## Tribe Clash Guess

Nick names 3 tribes each time (1st, 2nd, 3rd) — never pick them yourself. **`D=<serial> scripts/clash_guess.py <1st> <2nd> <3rd>`**
from the main screen or the Tribe Clash screen (names case/space-insensitive, e.g. `"dragon slayers" potato "purple gang"`).
Free, no gems. Only open while "Remaining guessing time" runs (on Battle days).

- Entry: main-screen **Tribe Clash** banner → **Guess** (dice, bottom right ≈ `(989,1825)`; the label still OCRs under the
  open dialog — a tap there closes it). Dialog: slots 2 / **1** / 3 left→middle→right (`(236,520)` `(538,490)` `(840,520)`),
  slot names OCR at y≈595; 8 tribe tiles (4×2), tap the icon ≈100 px above the name. A pick fills the selected slot
  and moves the selection 1→2→3. **Save** `(540,1656)` (green once all 3 are set; OCR can't read it), no toast →
  close ✕ `(972,222)` (no reopen check, Nick 2026-10-29). Exit 1 → `v_clash_guess.png`.
- **Guesses already there → clear them and start from scratch** (Nick, 2026-10-29): tap the picked tile _in the list_
  to remove it (tapping the slot does nothing). The script does this.
- **No unguessing:** clearing all 3 slots + Save does not stick — reopen shows the old picks (Kong 2026-10-29).
  Picks can only be replaced with 3 new ones.

## Daily Mission (claim all + activity chests) — Nick, 2026-10-27/28

Last step of `/catch-up` (then a final Fishing order claim). **Only if there's a red dot** (Nick, 2026-10-28):
no red dot on the side-menu icon / **Mission** entry → skip, nothing to claim.
**Verified on Kong 2026-10-28 (`daily.py … daily_mission`):** menu dot ≈ `(1040,1580)`; tap the Mission **icon** ≈ `(820,1380)`
— its label doesn't react; top Claim ≈ `(860,672)`; reachable chests glow (above labels at y≈510); dismiss on the
title `(540,240)` — `(540,120)` is outside the dialog and closes it; Weekly tab dot ≈ `(976,1630)`; Daily opens selected.

1. Main screen → list icon with red dot near the Tribe-chat strip ≈ `(990,1630)` → side menu (Settings, Notice,
   E-mail, Lobby, Grocery, **Mission**, Friends, Backpack) → **Mission** ≈ `(800,1360)`. Close ✕ `(972,238)`.
   Tabs at the bottom of the popup: **Daily** ≈ `(297,1693)`, **Weekly** ≈ `(779,1693)` (estimated from a
   screenshot, verify on first use); a red dot on a tab's top-right corner = something to claim there.
2. Do **both tabs** that have a red dot (Daily, then Weekly). On each:
   - Tap **one** yellow **Claim** row — it claims all rows (confirmed on 5 accounts).
     Never tap **GO** (it navigates to the mission, e.g. Grocery diamond purchase / Statue upgrade).
   - **Never scroll**: claimable rows always sort to the top. Top row is GO / grey ✓ → that list is done.
   - Top bar activity chests (Daily: **40 / 80 / 120 / 160** points): tap **one** reachable (glowing, no ✓) chest —
     it claims all reachable ones; dismiss the reward. All ✓ = done.
3. Report per tab each chest still unclaimable and the current points.

**The 18 daily rows** (10 points each; 160 = 16 rows) — every row is scripted except **Upgrade Statue** and **Purchase
with Diamonds in Grocery** (Nick, 2026-11-03), so a full runner pass must reach **160**; anything less = a step failed
or was skipped → find it. Rows → step: Stage → `stage`; Leveled-up any Hero + Enhanced Equipment → `hero`; Speed
Patrol + Claimed Patrol Rewards ×2 → `patrol` / `patrol_claim`; Recruitment ×2 + Artifact Wishing → `recruit`; Land
of Trials → `trials`; Match Challenges ×3 → `arena`; Tribe Trial → `tribe`; Canyon Clash → `canyon` (closed Mon
daytime); Won 1 wave at Secret Sanctuary → `sanctuary`; Synthesized Runes → `rune`; 10 Bread in Fishing → `fishing`;
Gate of Darkness → `gate`; Challenged the Tower → `tower` (incl. the chest-level Claim Reward).

## Pet Arena (join + Auto Deploy)

**Only open Mon, Tue, Wed** — skip on other days. Run it first in the dailies. **Scripted: `daily.py <acct> pet_arena`**
(2026-11-02; checks/sets sprites + order + check boxes, `per_pet` → MANUAL); steps below = its fallback.
Added by Nick 2026-10-26. Strategy per account (`missions.pet_arena`): **all accounts Random Selection, 2 sprites** (Nick, 2026-11-03 — was
High to Low / 4 except Cmajor). The game's own default is 4 / High to Low, so each account's first run changes both dropdowns once.

- **Be fast, touch only what's wrong** (Nick, 2026-11-03): the arena is busy right after the reset. 4 sprites / High to
  Low is the game's default and it keeps the dialog settings — if the dialog already shows the expected values, don't
  open a dropdown, just Start. **No free attempts left** ("Not enough free deployment attempts" after Start, or "attempts
  used up" on Join) **= done for the day**, however it got done. The top-left ticket counter is NOT the free attempts
  (it read 0 on accounts that could still Start).
- **Reading the arena** (traced 2026-11-03): pool = "Participating Pet: N/64" → N < 64 = open (decide on the count —
  the "X has deployed Y" ticker often hides the "Auto Deploy" label); a fight = only the "N Arena" header + a bar.
  Back from the pool goes straight to the Join screen (no dialog); only a fight asks "Exit this match?".
  A fight can start between Join and the Auto Deploy tap → the dialog never opens → exit, Join again.
  Don't re-tap Join while the arena loads: the spot lands on the pool's big **Deploy** button (manual deploy panel).
- The sprites value is a lone digit: OCR misses it on some frames — read the settled dialog, retry on an enlarged crop.
- **Cap 64 pets per arena** (Nick, 2026-11-02): at 64/64 the fight starts and you can't deploy until it ends —
  back arrow → "Exit this match?" Confirm ends it sooner, then Join again.
- The **"Champion" popup** ("Result of this round" / "Match Details") is the round result, not last season's: it pops
  after every round, so don't wait around in the arena — Start, then leave. Auto Deploy keeps running off-screen.
- Dropdowns open upward: sprites `(700,454)` → options 1–4 at y≈136/212/286/360; order `(700,620)` → High to Low /
  Low to High / Random Selection at y≈398/474/541 (x≈700). Check boxes `(898, 620/900/1210/1376)`.

1. Main screen → event hub `(896,340)` (the banner rotates; any banner opens the hub) → bottom tab **Pet Arena** —
   find it by label: the tabs shift with the events (≈`(310,1840)` on 2026-11-03), and its red dot hides "Pet" from
   OCR, so match "Arena" → **Join** `(540,1528)`. _Champion_ round popup ✕ `(972,548)` — it reopens a few s later,
   so open Auto Deploy right after closing it.
2. **Auto Deploy** `(956,1640)` → _Auto Deploy_ dialog:
   - **Deployed Sprite per Battle** = config `sprites` (4).
   - Strategy `stamina_order`: tick **Deploy by Stamina Order** (right checkbox) and set its dropdown to
     config `order` (**High to Low**; options High to Low / Low to High / Random Selection). The per-pet
     rows (Pet 1–4 rarity + stamina) stay unticked.
   - Strategy `per_pet`: untick the stamina row, tick the Pet 1–4 block, and set each Pet row's rarity +
     stamina dropdowns from config `pets` (only the first `sprites` rows are used). E.g. Cmajor: 2 sprites,
     Pet 1 = Eternal + Highest Stamina, Pet 2 = Eternal + Lowest Stamina.
   - Keep **Auto-Stop when free attempts are used up** ✓ and **If available slots < set amount…** ✓.
3. **Start** `(540,1570)` → "Auto Deploying" shows. Leave it running. Never buy attempts. Dialog ✕ `(938,282)`;
   back from the pool → Join screen; from a fight → "Exit this match?" → Confirm `(760,1162)`.

## Canyon Clash (Tribe group)

Added by Nick 2026-10-26; mapped on Cmajor via ADB (device coords).

**Season: opens Monday 17:00, closes the next Monday 06:00.** So Tue–Sun it's part of the normal dailies; on
**Monday** it's closed until 17:00 — do it in a separate run after 17:00 instead
(e.g. `/catch-up`, which does Storm + Canyon). If it's locked on screen ("Tribe Clash: Unlocks in …"), skip.
The main-screen "Tribe Clash" banner countdown is not Canyon's — check inside the Tribe screen.

Entry: main screen → **Tribe** `(448,1780)` → **Canyon Clash** card `(540,1090)` → vertical map (scroll with
`input swipe 540 1500 540 600 600`). Header shows your current spot ("Unoccupied" or e.g. "Silver Battlefield",
Occ. Time, Occ. Gains) and **Attempts N** (5 on Cmajor; never tap `+`, buys more).

Map, top → bottom: player-held spots (green dome = shield), then **Gold Sentinel** spots (white/gold platforms,
~60K CP NPCs), then **Silver Sentinel** spots (purple platforms = the "purple 9/m" spots: 9/min + 1 medal/h,
~41–44K CP NPCs). Glory spots are presumably above/among the top ones. Truly **empty** platforms (no occupant at
all) also appear — just below the Gold rows, in the Silver Sentinel rows, next to your own spot — prefer those
first; otherwise a Sentinel-held spot (no player) counts as free — beat it to take it. Occupant names: **blue**
name background = tribe member, **purple** = not in our tribe; your own spot shows a **green** name.

**Scan the whole map first** (scroll top → bottom, screenshot each screen) and choose by priority — empty
platform > Sentinel-held — before tapping anything. Never a player-held spot (Nick, 2026-10-30).
Silver (purple-platform) spots: consider **only the first 10** from the top (Nick, 2026-10-26) — ignore
silver spots further down. Spots change while you scroll and fill within seconds when several workers run —
re-screenshot before tapping and re-check the popup's name before confirming.

Empty platform: tap it (wait for map scroll inertia to stop first, or the tap misses) → popup "About to occupy
the empty <Type> Battlefield — costs no challenge attempts" → **Occupy** `(744,1340)` → wait ~3–5 s: if you already held a spot, a _Resource_ popup ("you left the old
Battlefield", gains from it) appears → **Confirm** `(540,1460)`. Moving to an empty spot is free, so it's fine to
move later — but pick the empty spot first anyway (saves an attempt).
**Read the popup text before confirming:** "About to challenge <Tribe> <name>'s …" means it isn't empty — if it's
your own tribe, **Cancel** (Chien Than 2026-10-28: a platform looked empty but was tribemate B.VN.'s). Spots can
also fill between screenshot and tap (another helper of ours — Dino/Kong raced for one — or an NPC Sentinel).
The map opens scrolled to your current area.

Taking a spot: tap the spot → popup "<Type> Battlefield", Occ. Gains, "Use 1 challenge attempt" → **Challenge**
`(742,1334)` (Cancel `(336,1334)`) → lineup (top 5 pre-selected, keep) → **Start** `(540,1808)` → battle ~10–45 s
(poll; it may return straight to the map with no Victory screen — check the header) → _Victory_ → tap the TOP `(540,150)` — never `(540,1500)`: it hits the map behind and chained 4 extra Sentinel fights, all 5 attempts gone (Kong 2026-11-02); confirm Attempts −1 exactly.
After Occupy/Victory the header can keep showing the old spot — back out to Tribe and re-enter to confirm
(your name in green on the new platform).

**`scripts/canyon.py <account>`** (runner step `canyon`, 2026-10-28) does this for EMPTY platforms: disc with no name label, popup text "occupy the empty" checked before Occupy, waits for map inertia. No empty spot → exit 2 → helper (Sentinel choice; never a player).
**Take a new spot every run, even if you already hold one** (Nick, 2026-10-27) — a held spot doesn't count as
done. Pick by the rules below; done once the header shows the newly taken spot. Never spend gems on attempts.

- **Never attack a player, of any kind** — tribe or not (Nick, 2026-10-30). Only empty or Sentinel-held (NPC)
  spots. Nothing empty or Sentinel-held → skip and report.
- **Mon–Fri:** take a **purple (9/m) spot**. Prefer an **empty** one, else beat a Silver Sentinel.
- **Sat–Sun:** take a **Glory** or **Gold** spot if one is empty or Sentinel-held, else a **purple/silver** one
  (empty first, else a Silver Sentinel).
- Never spend gems.
- **`canyon_clash: highest_free`** in the account file (Tiger, Nick 2026-10-28) replaces the day rules above, every day:
  take the **highest** spot on the map (topmost: Glory > Gold > Silver, any of the silver rows) that is **empty or
  Sentinel-held** — occupy it, or beat the Sentinel. If the current spot is
  already higher than every free one, keep it (counts as done). Nothing free → skip and report.
  `canyon.py` reads the header ("Glory/Gold/Silver Battlefield") and never moves a highest_free account down a tier
  (it took Tiger Glory → empty Gold on 2026-11-03 before that check).

**Occupation lasts 8h** ("Collect Time 08:00:00"), then ends on its own: on the next visit a _Resource_ popup
shows the gains → **Confirm** `(540,1460)` → dismiss `(540,1210)`; header shows "Unoccupied" → take a spot again.
Swipe slowly (`540 700 → 540 1500`, 1500 ms) to come back up; fast swipes fling far.
2026-10-29: a fast swipe (600 ms) on the map once kicked Cmajor back to the main screen — scroll down slowly too
(`540 1500 → 540 700`, 1500 ms). Leave the map with the back arrow `(92,1810)` only: taps a little higher hit the
left icon column (**Lineup** opens the Defense Lineup — Dminor, nothing saved). Empty purple spots can appear minutes
after `canyon.py` found none (7 accounts, 2026-10-29: the helpers all found empty Silver spots right below the
tribemate rows) — the helper re-checks for empty ones before beating a Sentinel.

**Points Reward** (runner: start of step `canyon`, same visit): left-side **Rewards** `(88,745)` with a red dot → **Claim Reward** `(540,1618)` (free) →
dismiss `(540,1880)` → close ✕ `(972,240)`.

Tribe chat pinned notice (Peakaboo, 2026-10-27): "Canyon: Move to 8/m if you reached 80k early. Dont attack
people not 80k yet." — not yet reflected in the rules above; ask Nick.

- **Points Rewards** `(88,745)` (left HUD with Records / Rank / Lineup — fixed while the map scrolls) → **Claim Reward**,
  repeat while it shows → ✕ `(972,240)`. Do it **after** occupying: the new spot earns the points (Nick, 2026-11-04).

## Poseidon's Ruins (Tribe, 3 attacks)

Added by Nick 2026-10-26; mapped on xFaktor via ADB (device coords). Skill: `miniheroes-poseidon`.
**Script:** `scripts/poseidon.py <serial>...` does all of this, accounts in parallel (per-ship locks). By hand only on its exit 1.

1. Main screen → **Tribe** `(448,1780)` (first tap right after the main screen appears may be ignored — retry once)
   → **Poseidon's Ruins** card `(540,1440)` (red dot = attempts left; "In Battle: hh:mm:ss") → Loading ~3 s →
   battle map, **Enemies** tab selected (Allies/Enemies at the bottom).
2. Header: **Attack Attempts N** top-left (3/day on xFaktor). Ignore Report / Rewards / Contribute.
3. Enemy ships in rows of 3, sorted by CP high → low (big ships first, rowboats at the bottom). Each shows
   name + CP and 3 hearts: **red** = alive, **grey + fire** = sunk. Scroll with `input swipe 540 1500 540 700 800`
   (~3 swipes reach the bottom). Sunk ships move down the list after a fight.
4. Pick the **lowest-CP ship with a red heart** → tap the ship → _Plunder_ popup ("Consume 1 attempt") →
   **Attack** `(742,1336)` (Cancel `(336,1336)`) → lineup pre-selected (top 5, keep) → **Start** `(540,1808)`
   → fight ~8 s → _Victory_ → tap `(540,1700)`. Back on the map: attempts −1, target −1 heart.
5. Repeat on the same target until attempts = 0; if it sinks or is being attacked, take the next-lowest
   ship with red hearts. Tribemates attack live — hearts change between screenshot and tap; the Plunder popup
   shows the current hearts, so re-check there.
6. Back `(92,1810)` → Tribe screen. Red dot on the card gone = attempts used.

**Being attacked**: **crossed swords** over the ship in the list; tapping it shows a toast "This player is being
challenged" (vi: "Người chơi này đang bị khiêu chiến") instead of Plunder.
If the target sinks while you're on the lineup, **Start does nothing** — back `(84,1810)`, no attempt is lost,
pick the next ship. Lineup cards can render black for a moment; Start still works.

## Storm Battlefield (right after Pet Arena)

**One account per server block at a time** (Nick, 2026-11-02): s201–210 (Aminor, Cmajor, xFaktor, Dminor) and
s211–220 (Bino, Dino, Chien Than, Kong) can be matched against each other — never overlap their Storm runs.
`daily.py` step `storm` holds a per-block lock (`storm_block()`, from `server:` in the yaml); a helper running
`storm.py` by hand must wait until no other account of its block is in Storm.

Added by Nick 2026-10-26; mapped on Cmajor via ADB (device coords). Free tickets only.

**Season: opens Monday 17:00, closes the next Monday 05:00** (like Canyon Clash). Tue–Sun: part of the normal
dailies. Monday: closed until 17:00 — run `/catch-up` after that.

1. Main screen → **2nd event card** (top right, y≈480). It rotates every few seconds (Storm Battlefield /
   Dragon Temple…); swiping it doesn't work. Pixel `(760,450)` gold ≈ `(230,150,66)` = Storm showing (use y=450
   for `--until`; at y=460 it reads darker), blue = other event; then tap `(880,480)` — tapping while another
   card shows usually still opens the event screen on the Storm tab. Event tabs at the bottom.
   **New season (Mon 17:00): the card opens "Welcome to Storm Battlefield! Please deploy your Heroes"** — Deploy
   `(540,1223)` → Quick Deploy `(984,1800)` → Save `(540,1808)` → back `(88,1812)` → **Start** `(540,1219)` → arena
   (`daily.storm_welcome()`, 2026-11-02: every account failed "arena did not open" before it).
   **Monday ≥ 17:00 with the game already running since before 17:00: restart the game first**
   (`am force-stop com.and.brawlen.web` + relaunch) — otherwise the Storm card never shows (Nick, 2026-10-26).
2. **Always start with a full lineup** — the previous run left only 1 hero (step 6). `scripts/storm.py` does
   this (and step 6) itself; the manual steps below are the fallback. First time (CP 0):
   **Deploy** `(540,1220)`; later runs: **Lineup** `(960,1600)` on the arena screen. Then **Quick Deploy**
   `(984,1800)` (top 5) → **Save** `(540,1808)` → back `(88,1812)` (→ **Start** `(540,1220)` if on the
   welcome screen). Verify the CP is the top-5 value before the first Start Match (helpers have skipped this
   and played with the 1-hero lineup).
3. Arena screen: tickets `N/5` at `(540,1428)`. **Start Match** `(540,1610)` → matches vary: some are instant (~5–8 s), close ones are
   real fights (~60–80 s) — poll until the arena screen is back → _Victory/Defeat_ → tap `(540,120)`. Repeat until 0/5.
4. **Free tickets — one visit of the + popup per run** (Nick, 2026-10-26). `scripts/storm.py` does steps 3–4: plays
   until 0, then (popup opens itself on Start Match at 0, or via **+**) taps the **left green button** until it's grey.
   Three looks: **Free** (pass accounts, instant), **Claim** with a camera icon
   (no pass → real video ad, Mintegral `MBRewardVideoActivity`), or grey "Chances: 0" = done. Never
   **Diamonds Redeem** (price varies per account: 30 / 50 / 150 gems). Ads: wait for the video to end (~35 s), then Android **Back** (`keyevent 4`) closes the end
   card and grants +1 — Back mid-video aborts with no reward (chance not used). Never tap the ad body/Install.
   Then close `(100,1150)`, play the new tickets; next time tickets hit 0 → close the popup and stop.
   Button state: sample `(260,1250)` — green (123,206,49) / grey (181,178,181). `(260,1274)` hits the "Free" text or
   the camera icon: that made storm.py miss the ad popup, "dismiss" it as a Victory and count fake 5 s matches.
5. **Rewards** `(96,880)` (left side) — runner: end of step `storm`, same visit (red dot box `(110,830)-(180,900)`; taps the Gold/Silver/Bronze icons, MANUAL if the dot stays) — if it has a red dot: _Rank Reward_ tab lists King/Glory/Gold/Silver/Bronze
   rows; tap a reached rank's highlighted item icon, not the row background (Bronze `(372,1404)`, Silver `(372,1180)`, Gold `(372,962)`) → claims the whole row (checkmarks) →
   dismiss `(540,1900)`. _Ranking Rewards_ tab = end-of-season table, nothing to claim. Close ✕ `(972,228)`;
   the red dot should be gone.
6. **At King rank: skip this step** — keep the full lineup (Nick, 2026-10-31). Below King: **Lineup** `(960,1600)` → quick-remove ↺ `(1006,1084)` (clears all) → tap only the **first** hero card
   `(140,1250)` (highest) → **Save** `(540,1808)` ("Successfully saved"). Done.

Tickets regen 1 per 2h (timer under the counter) — one can arrive right after storm.py stops.

**Open question (2026-10-27):** Aminor's Canyon spot showed 1043k CP = the 1-hero Storm lineup, while
tribemates' spots show 2.7–4.9M. If Canyon defence uses the Storm lineup, step 6 weakens it — ask Nick.

## Floating Realm (Tribe cross-server event, every 2 weeks) — learning, Kong 2026-11-03

Mapped on Kong via ADB (device coords). Skill: `miniheroes-realm`. **Script:** `scripts/realm.py <account>` does all
of this (untested end-to-end); by hand only on its exit 1.

Schedule: Preparation Mon → **Battle Tue/Wed/Thu 10:00–22:00** (server time = UTC) → Claim Fri. Battlefield
(declare war) opens 19:00. Stamina caps at 60 (regen +3 / ~15 min). It's reset to 30 at 05:00 Mon/Wed/Thu, so
stamina left over before a reset is lost.

1. Main screen → **Floating Realm** banner `(880,628)` (right column, under Dragon Temple; loads a few s late after a
   boot; if taps on it do nothing while other buttons work, restart the game — xFaktor/Aminor 2026-11-03) → event screen
   (day tabs, **Target** `(976,1320)` = stamina-used milestones 50…4100, **Enter** `(540,1476)`).
   **Target Rewards** (red "!" on Target and on the main-screen banner = a milestone reached): green **Claim** at the
   row's right `(864,622)` for the top row → _Congratulations_ → close on its "Tap anywhere to close" text `(540,1208)`;
   a claimed row drops to the bottom. ✕ `(972,228)`. realm.py claims them after exploring (Nick, 2026-11-03).
   Bottom **Rewards** = ranking-prize Preview only (sent by email after the event), nothing to claim.
2. Explore screen: **Explore** `(540,1380)` (cost 1 on F1, 2 on F2, 3 on F3). A **1x** toggle `(340,1516)` appears left of
   Explore once enough stamina is spent (the 3× explore unlock; not used yet). **Skip** checkbox `(816,1532)` right of Explore: keep it
   ticked (green check) before exploring (Nick, 2026-11-03; it was off on Tiger); realm.py ticks it. Each explore = 1 event; the event's
   button sits at the same spot:
   - _Gold/Silver Treasure_ → **Claim** `(540,1380)` → "Tap anywhere to close" `(540,500)`. ~1,000–1,500 pts.
   - Monster (e.g. _Drift Ship_ ~1.5M CP vs our 6.75M) → dialog with **Crush** `(540,1264)` = instant win,
     ~1,100–1,200 pts + a beast core (CP grows during the run: 6752k → 6977k after 4).
   - Stronger monster (F2 _Veteran Pilot_ 2.3M, 4 skulls) → **Attack** `(540,1264)` → lineup screen (empty the
     first time: **Quick Deploy** `(984,1800)`, beast cores show in its CP) → **Start** `(540,1808)` → Victory
     ~2,700 pts → Confirm. F3: _Sky Overlord_ (monster, 2.8M, ~4,900 pts) and _Encounter Battle_ (a player
     from another tribe, 5–6.4M, ~5,100 pts), same Attack flow (Kong won all 4, 2026-11-03). **Always Attack, CP doesn't matter; Defeat → always Mark it for tribe assist (Nick).**
     _Defeat_ (Kong vs a 91M player on F3): still pays a little (3000 gold + 100 pts) and knocks their supply −5%;
     Confirm `(540,1454)` → the event dialog returns with **Mark** `(320,1264)` | **Bypass** `(760,1264)` → Mark →
     straight back to the explore screen (no confirm). Losing your own attack does **not** drop you a floor.
     **Another player beating you** (F3) pops _Encounter Battle_ "You were defeated by [player], lost one [core], and have
     been returned to the previous floor" with only **Confirm** `(538,1259)` (Chien Than 2026-11-03: Confirm ignored 8×
     = connection lost; a game restart cleared it, the account was back on F2). No X on the dialog: every event must be done before the next explore.
   - _Monster Lair_: stake one of your beast cores on a breakthrough (rows ~`(540,1064/1228/1392)`, Refuse last).
     **Failure keeps the core unchanged** and still pays ~2,600 pts → never Refuse. **Rule (Nick):** highest tier
     first, same tier ATK → DEF → HP. Tiers: blue 10y < purple 100y < orange 1ky < red (name unseen). Success =
     the core moves up a tier (Cmajor 1ky ATK → red, 2026-11-03); its result screen closes like the failed one.
     **Warehouse** `(988,1812)` lists the cores and the total ATK/DEF/HP bonus (exploration only).
   - **Taps ignored but the screen looks normal** (timers tick, stamina doesn't drop) = the game lost its
     connection to the account (Kong 2026-11-03, after a Lair) → stop and report, don't keep tapping.
3. Floors: F1 Nagrand Island → F2 Land of Blaze → F3 Floating Castle (players from other tribes; losing to one
   sends you back a floor). Map: **Next Area** `(924,320)` → tap the floor's Go → entry dialog:
   **kill 2 Cloud Bandits** _or_ **use a Floating Realm Treasure Map** (green Go `(844,1034)`). A "conditions
   met, proceed?" tip pops up as soon as you hold a map.
   Counts are read off the screen at each decision (map's top-left scroll counter = maps held, the dialog's
   "Kill X (k/2)"); nothing has to be remembered across a stop. The dialog's "(m/1)" shows all maps held (Dino: 3), not capped at 1. The floor card label
   (top right) updates a beat after the explore screen shows: wait for it, don't read it once.
   **Map strategy (Nick, 2026-11-03), any day.** One map item works on every floor:
   - **F1→F2:** 0/2 Cloud Bandits → use a map. 1/2 → hunt the 2nd bandit. Every round (day) restarts on F1, and
     knockbacks drop you to F2, never F1, so this costs at most 1 map per day (3 per event).
   - **F2→F3:** keep **5 maps for the last battle day (Thu)**. Tue/Wed climb by killing 2 Veteran Pilots. A map may be spent before Thu only if 5 would still be left, and only at 0 kills. At 1 kill, hunt
     the rest even then. Thu: use the maps to reach and get back to F3.

4. **Pack** (event screen, right column `(980,1684)`; Mon–Thu, none in the truce) → _Daily Special_ list, each row
   "Limited to 1 purchases per day", button ~166 px below the row title, "Sold Out" once bought:
   Free Pack (20 gems) · **Support Pack** (4 stamina + 1000 coins, **80 gems**) · **Motivation Pack** (potion + 2 bags, **400 gems** on Dminor; all accounts but Chien Than/xFaktor, Nick) ·
   **Value Pack $0.99** · **Joy Pack $4.99** · Deluxe $9.99 / Supreme $19.99 / King $49.99 (never). The $ buttons
   are paid in **Stargems** (the white currency next to the gems, top left). Runner step `realm_packs` (dailies only, not the catch-up — Nick) buys the
   account's `floating_realm_packs` (Nick, 2026-11-03), reading the balances from crops of the counters (whole-screen
   OCR read Stargems "620" as "6201ng Realm"). Close ✕ `(972,228)`.
   Free Pack's button reads **Claim**; Support (80 gems) and Motivation (400 gems) buy straight away → reward popup →
   Sold Out. A **$ button opens a Tip "Pay with N Stargems … Cancel | Confirm"** ($0.99 = 60 Stargems) → Confirm →
   reward popup (Dminor, 2026-11-03). All target packs are at the top (Nick): Free + Support on the first screen, then
   **one slow 2-row drag** (`drag(1400, 640)`) shows Motivation, Value and Joy together.
