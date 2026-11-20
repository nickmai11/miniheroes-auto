# Definition of Done — dailies & catch-up

Rule (Nick, 2026-11-03): before moving to the next step, check its **Done** line on screen. Not done → the runner
retries once → a helper does that one step → still not → skip it and report why. `scripts/checklist.py` applies these
lines to each game-day log; a Done line here that it doesn't check = a `checklist.py` bug. Open questions:
`docs/open-issues.md`.

## Whole run

- **Sundays:** the `weekly` step's line per account — **180 weekly chest ✓**, or what is short and why (daily cap / cost / stars); a Lucky Star swap counts as done only once the row reads 50/50 later (Nick, 2026-11-08).
- **Dailies done** = every account shows the **160 Daily Mission chest ✓**. Only 2 of the 18 rows can't be scripted
  (Upgrade Statue, Purchase with Diamonds), so less than 160 means a step was missed → find it and do it.
- **Allowed to stop early:** event closed (Pet Arena Thu–Sun, Storm Sun 06:00–Mon 17:00, Canyon Mon daytime), a price over the safeguard
  cap (Trials, Patrol), Grocery price > balance or sold out, no empty or attackable Canyon spot.

## Dailies (run order)

1. **Pet Arena** (Mon–Wed) — "Auto Deploying" on screen, or "Not enough free deployment attempts". Proven at the
   end by step 25.
2. **Fishing** — every order worth ≥ min diamonds (refresh scrolls bought as needed) and the button shows "Auto Fishing".
3. **Arena** (runs 3× in the day) — tickets **0**; Ranking Rewards gift box has no red dot; reached win chests ✓.
4. **Patrol** — Speed Patrol bought until the next price hits the config limit (e.g. 100); Claim All done.
5. **Storm** — tickets 0 (free ticket claimed first) or max rank reached; lineup back to 1 hero; Rewards no red dot.
6. **Shop** — Free Benefits shows "Sold Out"; Select Hero has no red dot.
7. **Play Pass** — no red dot on any tab (never a $ button).
8. **Land of Trials** — every dungeon swept until the Sweep button's next price is above its config price (e.g. Gem Mine 4/4 at 160).
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
    Event**) and none on **Floating Realm** (Nick, 2026-11-03); Tribe Clash / Crystal Throne dots are excepted
    (`checklist.py`, 2026-11-14); the 7777 dot stays once the daily claims are ticked (ui-routine "Events").
    21b. **King's Treasury** — `DONE … keys 0` (or `SKIP no Golden Woods event`); point milestones with a red dot claimed.
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
- **Done** = the account's line says `exit 0 (done: N digs, shovels 0/<cap> left, …)`, no `dynamite`/`drill` line
  (boosters are never used — Nick 2026-11-14), and the game is back on the main screen. `exit 1` → `out.txt` + `v_relic.png` in `/tmp/miniheroes-relic/<account>/`: on some other screen → it taps back
  itself, else go home and re-run that account at once; otherwise a helper finishes that account by hand;
  `UNKNOWN cells` → teach the sprite (`relic.py --learn`), re-run. Not done: `refused` / `no effect` lines.
