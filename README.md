# miniheroes-auto

Daily-mission automation for **Mini Heroes: Magic Throne**, running on MuMuPlayer (macOS),
one MuMu instance per game account, driven over ADB by scripts and per-account config files.

## Layout

```
CLAUDE.md               ← start here in a new Claude session
.claude/skills/         ← project skills (load only in this repo; edit here, nothing to sync)
  miniheroes-dailies, catch-up, miniheroes-match/-poseidon/-relic, layout
accounts/
  _template.yaml        ← copy this to add an account
  cmajor.yaml           ← per-account mission config
docs/
  setup.md              ← MuMuPlayer instances, ADB, Proxyman/cert setup
  ui-routine.md         ← how each mission is done in the UI (taps, coordinates, gotchas)
  api-findings.md       ← what we learned about the game's HTTP API (and why we use the UI)
```

## How it runs

ADB only. `scripts/boot.sh` starts instances; `scripts/daily.py <account>` runs the whole Daily run order with no LLM
(OCR via macOS Vision, `scripts/ocr.swift`), calling one script per mission (`match.py`, `trials.py`, `patrol.py`,
`hero.py`, `tribe.py`, `adventure.py`, `storm.py`, `veins.py`, `grocery.py`, `fish_orders.py`, `relic_shovels.py`).
Judgment steps and failures are left to a Claude helper (`.claude/agents/mh-helper.md`). Mission rules and coords:
`docs/ui-routine.md`. Gem spending only within the account config caps, price read on screen before every buy.

## Why UI and not API

The game encrypts request bodies/query strings, and the encrypted payload includes a
per-request value — a byte-identical replay of a captured `POST /fam/sweep` is rejected with
`errcode 40001 "Parsing failed, please log in again"`. See `docs/api-findings.md`.
