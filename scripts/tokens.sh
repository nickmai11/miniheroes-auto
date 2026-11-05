#!/bin/bash
# Token use of the current Claude Code session (Nick 2026-11-05: report it after every task).
# Sums the usage fields of every assistant turn in the session transcript; with --since <marker> only turns after
# the last line containing that text (e.g. the user's prompt), so one session can report per task.
# usage: scripts/tokens.sh [--since <text>]   (newest transcript of this project; $TRANSCRIPT overrides)
d=~/.claude/projects/-Users-nickm-projects-chidojiro-miniheroes-auto
f=${TRANSCRIPT:-$(ls -t "$d"/*.jsonl | head -1)}
python3 - "$f" "$@" <<'EOF'
import json, sys
f, since = sys.argv[1], (sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--since' else None)
lines = open(f).read().splitlines()
if since:
    idx = [i for i, l in enumerate(lines) if since in l and '"type":"user"' in l]
    lines = lines[idx[-1]:] if idx else lines
t = dict(input=0, cache_write=0, cache_read=0, output=0); n = 0
for l in lines:
    try: u = json.loads(l)['message']['usage']
    except Exception: continue
    n += 1
    t['input'] += u.get('input_tokens', 0); t['cache_write'] += u.get('cache_creation_input_tokens', 0)
    t['cache_read'] += u.get('cache_read_input_tokens', 0); t['output'] += u.get('output_tokens', 0)
tot = sum(t.values())
# ponytail: Opus-class list price, cache read 0.1x, cache write 1.25x — only a rough $ figure
usd = (t['input'] * 15 + t['cache_write'] * 18.75 + t['cache_read'] * 1.5 + t['output'] * 75) / 1e6
print(f"tokens: {tot:,} total over {n} turns (input {t['input']:,}, cache write {t['cache_write']:,}, "
      f"cache read {t['cache_read']:,}, output {t['output']:,}) ≈ ${usd:.2f}")
EOF
