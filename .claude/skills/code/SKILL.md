---
name: code
description: Mini Heroes: Magic Throne gift code - redeem a code ("giftcode XXXX", "code XXXX") on Nick's accounts (menu → Settings → Redemption) via ADB (scripts/code_all.py → scripts/giftcode.py). Accounts = the ones named, else scripts/accounts.py code (accounts/tasks.yaml).
---

# Gift code

1. Accounts: the ones Nick names, else `scripts/accounts.py code` (`code:` in `accounts/tasks.yaml`). Skip an instance
   Nick is using right now (he said he took it over) and say so.
2. `scripts/code_all.py <CODE> [acct...]` (Bash, foreground or background + wait for the notification): batches of
   6 — boots the stopped instances (`boot.sh`, which also fixes a wrong account), redeems on each
   (`scripts/giftcode.py`: main screen → ☰ → Settings → Redemption → type → Redeem → close), then closes only the
   instances it booted. Already-running ones are redeemed as they are, not rebooted. Logs one line per account.
3. Report per account the game's reply (rewards / "already redeemed" / "invalid" / "expired") and any `NOT RUN` /
   exit 1 (`v_giftcode.png` in `/tmp/miniheroes-gift-<CODE>`). Free — never a purchase.
