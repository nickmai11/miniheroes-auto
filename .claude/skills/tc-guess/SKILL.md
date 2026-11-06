---
name: tc-guess
description: Mini Heroes: Magic Throne Tribe Clash → Guess - set Nick's 1st/2nd/3rd tribe picks and Save, on his MuMuPlayer accounts via ADB (scripts/clash_guess.py). Also "fr guess": the Floating Realm Guess (scripts/realm_guess.py).
---

# Tribe Clash Guess

Use when Nick says "tribe clash guess" / "tc guess" or "fr guess" + 3 tribe names, on one or more accounts.
**"fr guess" = Floating Realm Guess**: same steps with `scripts/realm_guess.py` (doc section "Floating Realm Guess").

1. Picks come from Nick's message, in order 1st, 2nd, 3rd ("today: dragon slayers, potato, purple gang" → 1 Dragon
   Slayers, 2 Potato, 3 Purple Gang). Missing or ambiguous → ask; never choose tribes yourself.
2. Accounts: the ones named ("group 1/2" → `accounts/groups.yaml`), else `scripts/accounts.py tc_guess` (`fr_guess` for fr guess). Not running → `scripts/boot.sh <idx>...`.
   Already running → screenshot first; don't interrupt a battle or something Nick is doing (ask).
3. Run all in parallel, no LLM: `D=<serial> scripts/clash_guess.py "<1st>" "<2nd>" "<3rd>"` per account.
   Last line `saved: [...]` = done. Exit 1 → read `v_clash_guess.png` (in the cwd: give each
   account its own cwd when running in parallel) and report; details in `scripts/doc.sh "Tribe Clash Guess"`.
4. Report per account: saved picks, or skipped + why.
