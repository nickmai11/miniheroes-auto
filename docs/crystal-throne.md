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

## Seen in-game 2026-11-08 (first qualifier, Cmajor 02:30–02:40 local)

- The card says "Not Open / Preparing" until 03:00, but the hub's **Enter** already opens the battlefield from at least
  02:30 — that is the setup window. Hub bottom bar: Rewards / Ranking / Groups / Guessing / Shop; battlefield bottom bar:
  Lineup / Battle Report / Contribution / Guide; minimap (device ~900,260) = full draggable map, back `92,1810`.
- Main base durability shows **150/150** (rules said 120). Peakaboo = Main Base 8, power rank 7, battlefield rank 4 at start.
- **Deployed Lineup was empty on Cmajor** (Lineup button red dot) → check it on every account before a match.
- Before the countdown ends the battlefield map ignores taps (own base and the highlighted adjacent hex both did
  nothing on 11-08) — the move popup can only be mapped once the match is live.
- Bases this week (same 15-node layout): top-left **150** PurpleGang · top **156** Second Phase · top-right **197** Natus
  Vincere · left **201 Peakaboo (H)** · right **54** Potato · bottom-left **175** TOXIC · bottom **221** Vie Gang ·
  bottom-right **245** ELITE.

## Operating rules for a live match (Nick, 2026-11-05)

Nick commands, Claude executes on all accounts in parallel — never picks targets itself.

- **Orders** come from Nick in the session (or Discord): target base + action (march / attack / station). Unknown map
  until the first battlefield; naming agreed during the Sun 02:00 setup window.
- **Free revives: automatically, as soon as available** (a per-account watcher during the match, no order needed).
- **Revive scrolls (item revives): only on Nick's order.**
- **Every move: one 20-diamond speed-up** (exactly one per march; tick "Don't show again" on its confirm popup if it
  appears). Note the rules: no speed-up is offered when the remaining march is ≤ 10 s, i.e. a single hop.
- Speed target: order typed → all accounts acting in ~10 s (script path, no screenshot reads in the loop).

## Map and target names (agreed with Nick 2026-11-05)

Screenshot `docs/crystal-throne-map.png` (819×835; the coloured lines and digits on it are someone's annotations, not
game content — ignore them). **Labelled version: `docs/crystal-throne-names.png`** — open it before a match.

- **Nodes:** rows A–E top→bottom, numbered 1–3 left→right within the row (no gaps): A1 A2 A3 in front of the top
  bases; B1 B2 B3 inner ring top; C1 / **F** (centre Fortress) / C3 on the sides; D1 D2 D3 inner ring bottom;
  E1 E2 E3 in front of the bottom bases.
- **Main bases are called by the server number shown on the map** ("Зона 201 Peakaboo" → `201`), never by tribe name
  or compass. `H` = our own base, whichever number it is that week (201 on 11-05).
- Icon types are a guess until seen in-game: ⚡ lightning/beacon icon (A1 A2 A3 B2 C1 C3 D2 E1 E2 E3, 10 of them) =
  Watchtower 30 pts; 🏰 tower icon (B1 B3 D1 D3) = Stronghold 60 pts; centre hex cluster F = Fortress 150 pts.

| Node | Image x,y | Node | Image x,y | Node | Image x,y |
| ---- | --------- | ---- | --------- | ---- | --------- |
| A1   | 180,235   | A2   | 415,230   | A3   | 620,225   |
| B1   | 305,320   | B2   | 415,320   | B3   | 525,320   |
| C1   | 210,430   | F    | 415,435   | C3   | 620,435   |
| D1   | 305,545   | D2   | 415,540   | D3   | 525,545   |
| E1   | 210,645   | E2   | 415,650   | E3   | 650,630   |

Main bases on the 11-05 map (image x,y): top-left 180,120 · top 415,105 · top-right 690,130 · left 80,375 ·
right 755,480 · bottom-left 180,745 · bottom 415,760 · bottom-right 655,745 (Peakaboo, 201). Pixel positions are for
calibrating the device tap table at the first battlefield (Sun 2026-11-08 02:00 local).

**Order grammar:** `<who> <action> <target>` — who = `all`, `g1`, `g2`, account names; action = `atk` (attack),
`go` (march), `def` (station), `revive` (scroll revive; free revives are automatic); target = node or base **server
number** or `H`. Examples: `g1 atk 150`, `all go B3`, `kong tiger def H`, `all revive`.

**Base numbers → positions (Nick, 2026-11-05):** at the start of each match Nick feeds the map; Claude must then resolve
every base number to its map position itself, before the first order — one OCR pass over the device map (the "Зона NNN"
/ zone label under each main base) builds the `number → x,y` table, so an order like `g1 atk 150` needs no screenshot.
Nodes are fixed positions; only the 8 base numbers change per match. If a number can't be read, say so at once rather
than guess.

**Captured bases (Nick, 2026-11-05):** when a tribe takes another tribe's main base, its on-screen label becomes the
captor's zone line plus a second line, e.g. `150 PurpleGang` / `Base 2` (two lines under the base icon). Nick orders it
as `150 base 2` (also accepted as `150b2`); the OCR must match the number on the first line and the `Base N` on the
second, ignoring the tribe name. A tribe's original base is `150` (= Base 1, no second line).
The table must therefore map `<number> [base N]` → position: after any capture or Displaced relocation Nick says so
(or an order names a base not in the table) → one more OCR pass over the map before acting.

**Scripts (2026-11-08):** `scripts/ct_enter.sh <serial>...` = main → Tribe → Crystal Throne → Enter on every instance in
parallel; `scripts/ct_do.sh <g1|g2|g3|all|name,name> [tap.py args]` = the same taps on every account of a group in
parallel (`CT_TOOL=ct_tap.py` for OCR text taps: `ct_do.sh g1 '^Lineup$' 80,1810`), serial map in `/tmp/ct_serials.txt`
(`<group> <account> <serial>`, groups `ct_g1..3` in `accounts/groups.yaml`). Every call is logged to the account's log.
Still unmapped (taps are dead before the countdown ends): the node popup with March / Attack / Station, the 20-diamond
speed-up popup and its "Don't show again" tick — map them on one account in the first minute of the match. No revive
`scripts/ct_revive.sh [minutes]` = free-revive watcher on every account (~1 s polls: taps Free Revive through its 60 s
cooldown until it takes, reopens the popup via the big Revive button 840,1600 if it was closed — 11-08 Cris/PuPu/xFaktor
sat defeated with it closed — stops at free `Times:0/5`; never Revive Now). Windows: `LAYOUT=ct` (layout skill).
taps (node positions on the device, the tap-on-base popup with March / Attack / Station, the 20-diamond speed-up popup
and its "Don't show again" tick) get mapped during the setup hour and written here.
