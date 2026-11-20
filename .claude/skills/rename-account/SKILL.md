---
name: rename-account
description: Rename one of Nick's Mini Heroes accounts everywhere - "<account> has changed to <name>", "rename <account> to <name>" - the in-game name lists (Arena no-attack), and, when he says everywhere, the account key, yaml, MuMu instance, logs and state (scripts/rename_account.py).
---

# Rename an account

1. **In-game name** (always): in `accounts/own_accounts.txt` and every `accounts/tribe_*.txt` roster holding the old
   in-game name, replace that line with the new name exactly as shown in the game, plus a dated note under the header
   comments (`# <account> = <new> (was <old>, Nick <date>).`). Arena matches names ignoring case, spaces and emoji.
2. **Account key + instance** (only when Nick says "everywhere" / "rename the account"): stop the instance first
   (`mumu-cli close <index>`; never while a task runs on it), then
   `scripts/rename_account.py <old key> <new key> [--name <instance name>] --dry`, read the list, run it without `--dry`.
   It renames `accounts/<old>.yaml` (`name` + `mumu_instance`), the old key / name / instance in every repo file
   (not `docs/archive/`, not the in-game lists of step 1), the MuMu instance (`vmName` in its bundle's
   `setting/vm.json`), `logs/<old>` and `/tmp/miniheroes-state/<old>-*`. Instance names have no spaces (scripts read
   them with `\S+`). Check `mumu-cli info all` shows the new name, and handle the "still mention" files by hand.
3. Prettier on the changed `.md` files (CLAUDE.md "Docs"), log the action, and offer the commit.
