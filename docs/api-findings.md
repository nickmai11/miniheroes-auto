# Game API findings (2026-10-26, game version 1.25.26)

## Hosts

| Host                                        | Purpose                              |
| ------------------------------------------- | ------------------------------------ |
| `us-su-bldld.maxngame.com`                  | **Game server** (all gameplay calls) |
| `us-cdn-bldld.maxngame.com`                 | Game CDN                             |
| `heart.maxngame.com`                        | Heartbeat                            |
| `passport.mgamestore.com`                   | Account login                        |
| `api.mgamestore.com`, `hwtj.mgamestore.com` | Platform API / analytics             |
| `119.29.29.99`                              | Tencent HTTPDNS (host resolution)    |

The existing **Postman collection "Miniheroes"** targets the _web events_ site, not these
in-game APIs.

## Observed endpoints (us-su-bldld.maxngame.com)

- `POST /basic/hook`, `POST /basic/login`, `GET /basic/get-server-open-info`, `GET /basic/log`
- `POST /pay/check`, `GET /tower/config`, `GET /chat/show-zone-msg`, `GET /guild/show`
- `GET /wish/show`, `POST /wish/free-gift`, `POST /wish/sign`, `POST /player/resource`, `POST /player/tga-log`
- `GET /fam/show` — Land of Trials state
- `POST /fam/sweep` — Land of Trials sweep

## Request format

Headers on every call:

```
Authorization: <session token>          # from /basic/login
appToken:      <base64 token>
channel: om    channelBranch: om_web    version: 1.25.26    lang: en
lastURL: <previous path>                lastSpeed: <ms>
Content-Type: application/x-www-form-urlencoded
User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; <device model> Build/...)
```

Bodies (POST) and query strings (GET) are **encrypted**, base64url-encoded — e.g. the sweep
body is 64 chars (48 raw bytes = 3 AES-sized blocks). Not readable.

## Replay test — failed

Re-sending a captured `POST /fam/sweep` byte-for-byte (same headers, valid session) returned:

```json
{
  "errcode": 40001,
  "errmsg": "Parsing failed, please log in again",
  "data": null
}
```

→ the encrypted payload carries a per-request value (timestamp / nonce / counter). Plain replay
is not possible; API automation would require reverse-engineering the client encryption
(decompile the APK, find the cipher + key). Parked for now — **UI automation is the chosen
approach.** Avoid sending more invalid requests (anti-cheat may log 40001s).

## APK tables (`apk-insights/`, 2026-11-25)

The game's static config, pulled from the APK: `mh-tables/*.json` (409 tables) and `mh-configs/` (all UI text in 12
languages — `en.json` key → text, `en_text.csv` the same as CSV — plus `hero_skills.csv`). Data only: no client code,
so nothing here helps with the request encryption above. Server-side state (dig boards, opponents, fight results) isn't
in it either.

**Trust:** it is a snapshot, the screen stays the truth (prices are still read on screen before every paid tap). Values
that could be compared with the live game matched on 2026-11-25: Wish x1 240 / x10 2280, Land of Trials 80/160/240,
Floating Realm packs 80 / 400 gems, Rune Salvage 60 cap and 10/20/30/45/60 chests. One mismatch: Crystal Throne Main
Base durability (table 150, doc 120).

**Look up a text** (an unknown popup, an item key like `wildMap`):
`grep -i "treasure map" apk-insights/mh-configs/en_text.csv`. Table rows name their texts by key (`WILD_MAP_NAME1`).

Table prefix → mission (the facts taken from them sit in that mission's doc section):

- `castle*` (text keys `FORTGVG_*`, `pointGvg*`) — **Crystal Throne**: `castleMaps` = the 23 nodes + which touches which → `docs/crystal-throne.md`, `docs/ct-nodes.txt`
- `wt*` (`WILD_*`) — **Floating Realm**: floors, stamina cost, points per event, map cost, packs → ui-routine "Floating Realm"
- `siege*` (`ATTACKCITY_*`) — **Tribe Clash**: `siegeBox*` = Chieftain's Treasure (9 floors, keys per chest) → ui-routine "Tribe Clash Treasure"
- `fam*` — **Land of Trials**: `famUnlocks.buyDiamond` = the sweep price ladder → ui-routine "Land of Trials"
- `hallow*` — **Relics (Archaeology)**: `hallowBuyCounts` = shovel buys, `hallowMaps` = the 9 areas and their drop rates → relic skill
- `monthActivity*` (`MONTH_EVENT_*`, `flipCard`) — **King's Treasury**: prize tiers by level (1/3/5/7/10/15), flip milestones every 50 to 350
- `glyphs*` — **Runes**: `glyphsBreakRewards` = Rune Salvage chests
- `smithy*` (`DIAOYU_*`) — **Fishing**: orders, bait shop (40 gems / 5), refresh tickets (5 for 50 gems)
- `quickHangupConditions`, `hangupRewards` — **Patrol**: Speed Patrol: 1 free, then 50 / 100 / 100 / 200 / 200 gems
- `summonArtifact*` — **Artifact wishes**: Holy Light cost per tier 200 / 250 / 500 / 1000 / 1500; tier 4 also lists 280 gems
- `doubleDan*`, `wish*` — **Joyful Holiday / Wish Summon**: draw prices, pools
- `weapon*` — **Divine Weapon**: forge, veins (`weaponMineral*`: pickaxe 120 gems / 5)
- `hero`, `skinInfos`, `heroSkills` — **Heroes**: 81 named heroes, 92 non-default skins (names only, no images) — the face library's 69 heroes all match a name here
- `taskDailys`, `taskWeeks`, `taskLists` — **Daily / Weekly Missions**: 22 daily tasks, 10 points each
- `unlockMainFunctions` — **Function unlocks**: level per function (Storm 90, Pet Arena 125, Divine Weapon 140, Relic / Rune Salvage 150) — **unverified**: not confirmed that the condition is team level
- `constConfig` — **Global constants**: caps and prices (`upperLimitShove` 500, `breakGlyphsLimit` 60, `wildTraceEnergyMax` 60)
