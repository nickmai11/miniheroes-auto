#!/bin/bash
# "dailies all": boot + daily.py on every accounts/tasks.yaml `dailies` account, Kong II after Kong, done.sh per clean
# account (Nick 2026-11-27). Leftovers: scripts/summary.sh /tmp/miniheroes-<date>. --close as in catchup_all.sh.
exec "$(dirname "$0")/catchup_all.sh" --dailies "$@"
