# Crystal Throne (Tribe → Crystal Throne) — rules as shown in-game 2026-11-05

Read on Cmajor from the card's **?** (Tribe screen, scroll down, card below Poseidon's Ruins; `?` at device 744,96; the
rules popup scrolls ~300 px per page inside y 600–1420). Not automated: nothing in `daily.py` touches it.

## Schedule (UTC+7 = Nick's local)

- Monthly: 4 **Selection** rounds on Saturdays (11/7, 11/14, 11/21, 11/28), **Finals** Sun 11/29.
- Qualifying rounds: Saturday **20:00–20:40 UTC** = **Sun 03:00–03:40 local**; battlefield opens for defence setup at
  19:00 UTC = **Sun 02:00 local**. Finals: Sunday of week 4, same hours, across the 4 adjacent regions.
- The card's "Preparing" countdown ends at Saturday 05:00 UTC (12:00 local) — the game-day reset, not the battle.

## Participation

- Cross-region; regions older than 30 days; adjacent regions share a competition area.
- Tribe needs ≥ 5 members and 2500 tribe medals earned in 7 days (Peakaboo: 29/5, 12324/2500 on 11-05).
- Top 32 tribes by total power in the zone are picked automatically (elite group holds the top 16 by default). Tribe
  power = sum of every member's highest historical power.
- Joining a cross-server tribe already in the event locks you to it (or a local tribe) for 30 days; not allowed at all
  from Sat 20:00 to Sun 20:00 of the final week.

## Gameplay

- 8 tribes per match, each placed somewhere on the map.
- Structures: Main Base (durability 120, 10 pts), Watchtower (35, 30), Stronghold (50, 60), Fortress (70, 150).
- Each attack takes 1 durability; several tribes can hit one structure; the final blow captures it and earns the points.
- Main base protected 15 min after start; stronghold 20 min. Main base captured = whole tribe eliminated, points reset
  to 0. If the tribe holds other main bases it relocates and everyone gets **Displaced** (march time doubled until the
  original is retaken).
- Marching: only to own or adjacent bases, 10 s per hop; diamonds halve it (not below 10 s) — never spend.

## Battle

- Deployment lineup must be set, else the Arena defence lineup is used.
- Each hero has 100 energy; fights cost energy (winner loses less the bigger the power gap); the loser's heroes drop to
  1 energy and are out. Low energy lowers all stats.
- Revives: 5 free (60 s wait each) + 6 item revives (no wait; more in the finals); energy back to 100 after a revive;
  a short protection after respawn.
- Community guide (Nick, 2026-11-05: https://hackmd.io/@1khp-7TMSpWxNFF5QFSp5g/B1ft-MNI1l) repeats these rules and adds
  only generic tips (use the 15-min shield to grab nearby points, focus high-point structures); nothing on the map or UI.

## Scoring and rewards

- Tribe ranking by points (tie → higher total power; eliminated tribes rank by elimination time, earlier = lower).
  Only players who fought or were attacked get tribe rewards.
- Personal: 10 pts per player defeated, 1 pt per durability point hit; any points > 0 = personal reward. Both sent by
  mail after the match.
- Promotion: weeks 1–3, top 2 regular → elite, bottom 2 elite → regular (elite earns more event points). After week 4
  the 4 areas merge; top 8 → Champion Showdown, 9–16 Glory, 17–24 Gold.
- Guessing opens in the final stage: pick the top 3 of the 8 Champion tribes; rewards by mail.

## Operating rules for a live match (Nick, 2026-11-05)

Nick commands, Claude executes on all accounts in parallel — never picks targets itself.

- **Orders** come from Nick in the session (or Discord): target base + action (march / attack / station). Unknown map
  until the first battlefield; naming agreed during the Sun 02:00 setup window.
- **Free revives: automatically, as soon as available** (a per-account watcher during the match, no order needed).
- **Revive scrolls (item revives): only on Nick's order.**
- **Every move: one 20-diamond speed-up** (exactly one per march; tick "Don't show again" on its confirm popup if it
  appears). Note the rules: no speed-up is offered when the remaining march is ≤ 10 s, i.e. a single hop.
- Speed target: order typed → all accounts acting in ~10 s (script path, no screenshot reads in the loop).

## Map and target names (proposed 2026-11-05, from Nick's screenshot `docs/crystal-throne-map.png`, 819×835)

Fixed grid names, independent of which tribe sits where. Rows A–E top→bottom, columns 1–5 left→right. Icon types are a
guess until seen in-game (⚡ = the lightning/beacon icon, 10 of them; 🏰 = tower icon, 4; the centre hex cluster = the
Fortress). Coordinates are image pixels of the screenshot, for calibrating the tap table on the real device.

| Name | Type (guess)  | Image x,y | Where                               |
| ---- | ------------- | --------- | ----------------------------------- |
| A1   | ⚡ Watchtower | 180,235   | below NW main base                  |
| A3   | ⚡ Watchtower | 415,230   | below N main base                   |
| A5   | ⚡ Watchtower | 620,225   | below NE main base                  |
| B2   | 🏰 Stronghold | 305,320   | inner ring, upper left              |
| B3   | ⚡ Watchtower | 415,320   | inner ring, top                     |
| B4   | 🏰 Stronghold | 525,320   | inner ring, upper right             |
| C1   | ⚡ Watchtower | 210,430   | right of W main base                |
| F    | Fortress      | 415,435   | centre (alias C3)                   |
| C5   | ⚡ Watchtower | 620,435   | left of E main base                 |
| D2   | 🏰 Stronghold | 305,545   | inner ring, lower left              |
| D3   | ⚡ Watchtower | 415,540   | inner ring, bottom                  |
| D4   | 🏰 Stronghold | 525,545   | inner ring, lower right             |
| E1   | ⚡ Watchtower | 210,645   | above SW main base                  |
| E3   | ⚡ Watchtower | 415,650   | above S main base                   |
| E5   | ⚡ Watchtower | 650,630   | above SE main base                  |
| NW   | Main base     | 180,120   | top-left tribe                      |
| N    | Main base     | 415,105   | top-centre tribe                    |
| NE   | Main base     | 690,130   | top-right tribe                     |
| W    | Main base     | 80,375    | left tribe                          |
| E    | Main base     | 755,480   | right tribe                         |
| SW   | Main base     | 180,745   | bottom-left tribe                   |
| S    | Main base     | 415,760   | bottom-centre tribe                 |
| SE   | Main base     | 655,745   | bottom-right tribe (Peakaboo 11-05) |
| H    | our main base | —         | alias for whichever one is ours     |

Order grammar: `<who> <action> <target>` — who = `all`, `g1`, `g2`, account names; action = `march`, `attack`,
`station`, `revive` (scroll); e.g. `all attack B4`, `g1 march E5`, `kong tiger station H`.
