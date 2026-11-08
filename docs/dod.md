# Definition of Done — dailies & catch-up

**Draft for Nick's review (2026-11-03).** Rule: before moving to the next step, check its **Done** line on
screen. Not done → the runner retries once → a helper does that one step → still not → skip it and report why.

## Questions for Nick

1. **Monday:** Canyon is closed until 17:00, so a Monday daytime dailies run tops out at **150**; the evening
   catch-up adds Canyon → 160. OK to call 150 "done" on Monday daytime?
2. **Events dots that only clear by spending** (collect-only rule says never): Golden Woods → King's Treasury
   (Shuffle Cards uses keys), 7777 after the daily claim (Again / Open All = draws), Tribe Clash (only Treasures /
   Enter left). Spend for those, or accept those dots?
3. **Floating Realm** isn't mapped yet — what should be collected there?

## Whole run

- **Dailies done** = every account shows the **160 Daily Mission chest ✓**. Only 2 of the 18 rows can't be scripted
  (Upgrade Statue, Purchase with Diamonds), so less than 160 means a step was missed → find it and do it.
- **Allowed to stop early:** event closed (Pet Arena Thu–Sun, Storm / Canyon Mon daytime), a price over the safeguard
  cap (Trials, Patrol), Grocery price > balance or sold out, no empty Canyon spot.

## Dailies (run order)

1. **Pet Arena** (Mon–Wed) — "Auto Deploying" on screen, or "Not enough free deployment attempts". Proven at the
   end by step 25.
2. **Fishing** — every order worth ≥ min diamonds (refresh scrolls bought as needed) and the button shows "Auto Fishing".
3. **Arena** (runs 3× in the day) — tickets **0**; Ranking Rewards gift box has no red dot; reached win chests ✓.
4. **Patrol** — Speed Patrol bought until the next price hits the config limit (e.g. 100); Claim All done.
5. **Storm** — tickets 0 (free ticket claimed first) or max rank reached; lineup back to 1 hero; Rewards no red dot.
6. **Shop** — Free Benefits shows "Sold Out"; Select Hero has no red dot.
7. **Play Pass** — no red dot on any tab (never a $ button).
8. **Land of Trials** — every dungeon at its config count (e.g. Gem Mine 4/4), decided from the Sweep button price.
9. **Tower** — 3 challenges fought; if "Claim Reward" (chest level) shows, it's claimed and the fights go on.
10. **Secret Sanctuary** — swept, or **all floors won** (floor 10 won / no next-floor marker left on the map).
11. **Gate of Darkness** — "Chances left today: 0".
12. **Beast Realm** — Chances dropped by 1.
13. **Recruit** — the free draws in the config are used: Common, Ancestor ("Free after …" shows), Artifact. No Play Pass: the ad draws count (Nick 2026-11-08).
14. **Hero** — Bone Archer leveled at least once and gear enhanced at least once (levels don't matter). Out of
    potions → Rebirth → quick Lv.90.
15. **Tribe** — signed in; Tribe Trial has no red dot; Request + Assist done. **Canyon:** a new spot occupied
    (our name on it) and Points Rewards has no red dot.
16. **Divine Weapon** — pickaxes 0; every free Forge slot filled (or not enough crystals / forge off in config). Benefit
    (pass accounts) claimed after the forging — no red dot left on it.
17. **Stage** — 3 fights done (Defeat → Challenge again).
18. **Patrol claim** — Claim All → "Congratulations".
19. **Rune** — 1 synthesis ("Congratulations … Rune"), no locked rune tapped.
20. **Grocery** — free chests show "Sold Out" (no Play Pass: after the 9 ad claims too); each config tile bought (or price > balance / sold out).
21. **Events** — no red dot on any event hub tab (**Pet Arena, Golden Woods, 7777 Draws, Match Event, Weekly
    Event**) and none on the weekly tribe events (**Floating Realm, Tribe Clash**) (Nick, 2026-11-03).
22. **Fishing rewards** — no yellow Claim left on the orders.
23. **Daily Mission** — Daily tab: rows and chests claimed, **160 ✓** (see "Whole run"). **Weekly tab too**: no yellow
    Claim left, its chests up to the points claimed, and **no red dot on either tab** (the step reads both at the end;
    2026-11-04: the Weekly tab was skipped on every account and Nick found 4 unclaimed rows on Aminor).
24. **Play Pass again** — no red dot on the Play Pass icon (opened only when the icon has one; Nick, 2026-11-03).

## Catch-up

Same as the dailies step with the same name, except:

- **Fishing** — only Auto started (no order refresh).
- **Divine Weapon** — veins + forge, then Benefit claimed (pass accounts; no red dot left).
- **Tribe** — Request + Assist only.
- **Recruit** — free Common draws only (cooldown → one more try at the end).
- **Daily Mission** — claim, then report the points and the chests still locked (160 only if the dailies ran today).
- **Play Pass again** — same as dailies step 24.
- **Pet Arena check** (Mon–Wed, catch-up only since 2026-11-04 — Nick removed it from the dailies) — Achievement
  "Cumulative pet deployments completed" is **+40 since yesterday** (all 40 free attempts used), and no yellow Claim
  left there (claimed while reading). Short → Auto Deploy restarted, re-checked in the next catch-up.

## Relics (on request, `scripts/relic_all.sh`)

- **Top-up** (Nick, 2026-11-04; after the free shovels hit 0, once per game day): a `top-up: benefit: …` line (red dot →
  `claimed`; else `no red dot`) and a shovel-buy line per
  configured price — `bought 10 shovels for 80 gems (a -> b)` with the counter up by 10, or `shovel buy skipped: N gems
on screen not in […]` for any other price (never a Confirm on it). Not done: a Tip popup left open, or a buy at a price
  that isn't in the account's `relic_shovel_buys`.
- **Done** = the account's line says `exit 0 (done: N digs, shovels 0/<cap> left, …)`, a booster line precedes it
  (`dynamite/drill rXcY (saves ~N, stock a->b) -> …` or `booster hint (not used)`), and the game is back on the main
  screen. `exit 1` → `out.txt` + `v_relic.png` in `/tmp/miniheroes-relic/<account>/`: on some other screen → it taps back
  itself, else go home and re-run that account at once; otherwise a helper finishes that account by hand;
  `UNKNOWN cells` → teach the sprite (`relic.py --learn`), re-run. Not done: `refused` / `no effect` / `booster not consumed` lines.

## Where the scripts say OK without proving it (fix list)

1. **Daily Mission** never checks the 160 chest — 4 accounts logged OK at 120 today.
2. **The OK line shows only a script's last line**, so Trials / Hero / Storm hide what they did.
3. **Trials** stopping short (cap / no purchases left) still says plain OK instead of reporting it.
4. **Hero** can say OK with 0 level-ups; the gear Enhance isn't checked.
5. **Patrol** Claim All, **Beast Realm** chances and **Canyon** "occupied" aren't confirmed on screen.
6. **Recruit** fewer draws than config, **Divine** forge not responding, **Fishing** Auto stopped, **Grocery** free
   chests not "Sold Out" — all still say OK.
7. **Shop / Play Pass / Tribe / Arena claims** — nothing re-checks the red dot is gone after claiming.
8. **Storm** can say OK with 0 matches when the rank is unreadable; **Stage** counts a fight without seeing
   Victory/Defeat; **Sanctuary** says "swept" without checking.
