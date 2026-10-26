# Game API findings (2026-10-26, game version 1.25.26)

## Hosts

| Host | Purpose |
|---|---|
| `us-su-bldld.maxngame.com` | **Game server** (all gameplay calls) |
| `us-cdn-bldld.maxngame.com` | Game CDN |
| `heart.maxngame.com` | Heartbeat |
| `passport.mgamestore.com` | Account login |
| `api.mgamestore.com`, `hwtj.mgamestore.com` | Platform API / analytics |
| `119.29.29.99` | Tencent HTTPDNS (host resolution) |

The existing **Postman collection "Miniheroes"** targets the *web events* site, not these
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
{"errcode":40001,"errmsg":"Parsing failed, please log in again","data":null}
```

→ the encrypted payload carries a per-request value (timestamp / nonce / counter). Plain replay
is not possible; API automation would require reverse-engineering the client encryption
(decompile the APK, find the cipher + key). Parked for now — **UI automation is the chosen
approach.** Avoid sending more invalid requests (anti-cheat may log 40001s).
