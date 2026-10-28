#!/bin/sh
# Print only the needed sections of docs/ui-routine.md (saves helpers ~10k tokens each).
# usage: scripts/doc.sh Arena Fishing "Divine Weapon"   (case-insensitive "## <prefix>" match)
# Always includes Speed, ADB alternative, General gotchas.
cd "$(dirname "$0")/.." && awk -v want="speed|adb alternative|general gotchas$(printf '|%s' "$@" | tr 'A-Z' 'a-z')" '
BEGIN { n = split(want, w, "|") }
/^## / { p = 0; h = tolower(substr($0, 4)); for (i = 1; i <= n; i++) if (w[i] != "" && index(h, w[i]) == 1) p = 1 }
p' docs/ui-routine.md
