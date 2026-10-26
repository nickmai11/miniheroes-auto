# miniheroes-auto

Daily-mission automation for **Mini Heroes: Magic Throne**, running on MuMuPlayer (macOS),
one MuMu instance per game account. Missions are performed by Claude through computer use
(screenshots + taps on the emulator window) or, without computer use, via ADB (`screencap` + `input tap`), driven by per-account config files.

## Layout

```
CLAUDE.md               ← start here in a new Claude session
.claude/skills/         ← project skills (load only in this repo; edit here, nothing to sync)
  miniheroes-dailies/SKILL.md
  miniheroes-match/SKILL.md
accounts/
  _template.yaml        ← copy this to add an account
  cmajor.yaml           ← per-account mission config
docs/
  setup.md              ← MuMuPlayer instances, ADB, Proxyman/cert setup
  ui-routine.md         ← how each mission is done in the UI (taps, coordinates, gotchas)
  api-findings.md       ← what we learned about the game's HTTP API (and why we use the UI)
```

## Status

| Mission | Automated via | Notes |
|---|---|---|
| Land of Trials sweeps | UI (computer use or ADB) | Verified on Cmajor, 2026-10-26 (ADB) |
| Match (Arena) crashes | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Shop freebies (red dots) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Play Pass claims (red dots) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Tower of the Throne (1 challenge) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Secret Sanctuary sweep | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Gate of Darkness (run + sweep) | UI (ADB) | Mapped on Cmajor, 2026-10-26 (quit button unmapped) |
| Recruit (free summons) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Hero upgrade (Bone Archer) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Tribe (sign-in, trial, request/assist) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Fishing (orders, benefit, auto) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Divine Weapon (benefit, Excelsior Veins) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Adventure stage (1 run) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Patrol (speed ×3, claim all) | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Rune synthesis | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Grocery free chests | UI (ADB) | Mapped on Cmajor, 2026-10-26 |
| Others | – | Add to `docs/ui-routine.md` + account configs as they're mapped |

## Why UI and not API

The game encrypts request bodies/query strings, and the encrypted payload includes a
per-request value — a byte-identical replay of a captured `POST /fam/sweep` is rejected with
`errcode 40001 "Parsing failed, please log in again"`. See `docs/api-findings.md`.

## Schedules

The repo is the source of truth: each launchd job is a plist in `schedules/`. After adding, editing or
deleting one, run `scripts/sync-schedules.sh` — it installs/updates them in `~/Library/LaunchAgents`, removes
`com.nick.miniheroes-*` jobs no longer in the repo, and prints every schedule with its last exit code.

| Job | When | What |
|---|---|---|
| `com.nick.miniheroes-dailies` | daily 13:00 | `scripts/run-dailies.sh`: headless `claude -p` dailies for all accounts except Cmajor |
| `com.nick.miniheroes-monday` | Monday 17:05 | `scripts/run-dailies.sh monday`: Storm Battlefield + Canyon Clash (seasons open Mon 17:00), all accounts except Cmajor |

Allowed commands for headless runs: `.claude/settings.json` (no push, no deletes). Output:
`logs/<mode>-<date>.log` + a macOS notification. Needs you logged in; if the Mac sleeps through the time it
runs on wake. Run now: `launchctl kickstart gui/$(id -u)/com.nick.miniheroes-dailies`.
