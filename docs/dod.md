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

1. **Pet Arena** (Mon–Wed) — "Auto Deploying" on screen, or "Not enough free deployment attempts".
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
13. **Recruit** — the free draws in the config are used: Common, Ancestor ("Free after …" shows), Artifact.
14. **Hero** — Bone Archer leveled at least once and gear enhanced at least once (levels don't matter). Out of
    potions → Rebirth → quick Lv.90.
15. **Tribe** — signed in; Tribe Trial has no red dot; Request + Assist done. **Canyon:** a new spot occupied
    (our name on it) and Points Rewards has no red dot.
16. **Divine Weapon** — pickaxes 0; every free Forge slot filled (or not enough crystals / forge off in config).
17. **Stage** — 3 fights done (Defeat → Challenge again).
18. **Patrol claim** — Claim All → "Congratulations".
19. **Rune** — 1 synthesis ("Congratulations … Rune"), no locked rune tapped.
20. **Grocery** — free chests show "Sold Out"; each config tile bought (or price > balance / sold out).
21. **Events** — no red dot on any event hub tab (**Pet Arena, Golden Woods, 7777 Draws, Match Event, Weekly
    Event**) and none on the weekly tribe events (**Floating Realm, Tribe Clash**) (Nick, 2026-11-03).
22. **Fishing rewards** — no yellow Claim left on the orders.
23. **Daily Mission** — rows and chests claimed, **160 ✓** (see "Whole run").
24. **Play Pass again** — no red dot on the Play Pass icon or any of its tabs (after the missions).

## Catch-up

Same as the dailies step with the same name, except:

- **Fishing** — only Auto started (no order refresh).
- **Divine Weapon** — veins + forge, no Benefit.
- **Tribe** — Request + Assist only.
- **Recruit** — free Common draws only (cooldown → one more try at the end).
- **Daily Mission** — claim, then report the points and the chests still locked (160 only if the dailies ran today).
- **Play Pass again** — same as dailies step 24.

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
