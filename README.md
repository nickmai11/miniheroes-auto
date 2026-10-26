# miniheroes-auto

Daily-mission automation for **Mini Heroes: Magic Throne**, running on MuMuPlayer (macOS),
one MuMu instance per game account. Missions are performed by Claude through computer use
(screenshots + taps on the emulator window) or, without computer use, via ADB (`screencap` + `input tap`), driven by per-account config files.

## Layout

```
CLAUDE.md               ← start here in a new Claude session
skills/miniheroes-match/SKILL.md   ← Match (Arena) skill
skills/miniheroes-dailies/SKILL.md
                        ← the "Mini Heroes dailies" skill (also saved to Nick's Claude account;
                          keep both in sync when editing)
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
