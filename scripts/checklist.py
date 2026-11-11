#!/usr/bin/env python3
# Dailies checklist (Nick 2026-11-11): checklists/<game day>/<account>.md - grocery coins on top, then the open boxes
# (FAIL/MANUAL/never run/short), then the done ones (OK/SKIP); the Daily Mission 160 chest is one of the boxes.
# Rules (Nick 2026-11-11): Pet Arena done at +40 deployments that day (count from pet_check, any run), or once pets deployed
# after the count last changed (by hand, or an Auto Deploy restart) cover the missing ones - rounds count late; Sanctuary
# done only at floors 10/10; Events done only with no red dot left (the step reports them, Tribe Clash excepted);
# a "N/M done" / "forge N/M" short of M = open. A later no-op re-run line ("claimed nothing") keeps the earlier result.
# Source = logs/<account>/<game day>.log: dailies runs and targeted re-runs (`daily.py <acct> [--catch-up] <step>...`);
# full catch-up runs (`--catch-up`, no steps) are their own task - only their pet deployment count is used.
# daily.py calls this after every run.
# usage: scripts/checklist.py [<game day> [<account>...]]   (default: today's game day, every account with a log)
#        scripts/checklist.py --test
import datetime, os, re, sys
os.environ.setdefault('D', '')
from daily import CATCHUP, GAME_DAY, ORDER, SHOP_TABS

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
HEAD = re.compile(r'^(\d\d:\d\d):\d\d === \S+ \S+ daily\.py \S+ ?(.*?) \(serial')
LINE = re.compile(r'^\d\d:\d\d:\d\d (OK|SKIP|FAIL|MANUAL) (\w+)(?: \(\d+s\))?: (.*)')
DUNGEON = re.compile(r'^\d\d:\d\d:\d\d\s+(\w+): (\d+)/(\d+) done today')
PET = re.compile(r'pet deployments (\d+) \(yesterday (\d+), \+(\d+) today\)')
HAND = re.compile(r'pet: deployed by hand \(free attempt\) x(\d+)')
SENT = re.compile(r'request:? sent\b|cooldown 0?(5:5\d|6:00):\d\d')   # a fresh 6 h timer = sent just now
NOOP = re.compile(r'nothing|\(0 this run\)|after 0 crashes|no red dot|already on')


def parse(lines):
    """-> dict: res {step: (tag, text)}, chests, runs, pet (n, yesterday, +today) or None, dungeons {key: (done, total)}."""
    p = {'res': {}, 'chests': set(), 'runs': [], 'pet': None, 'dungeons': {}, 'sent': False, 'refill': 0, 'auto': False}
    use = False
    for l in lines:
        if h := HEAD.match(l):
            args = h.group(2).split(); steps = [a for a in args if not a.startswith('--')]
            use = '--catch-up' not in args or bool(steps)
            if use: p['runs'].append(f'{h.group(1)} {" ".join(steps) or "full"}' + (' (catch-up)' if '--catch-up' in args else ''))
            continue
        # Pet Arena (Nick 2026-11-11): the count rises only when a round ends, so pets deployed after it last changed -
        # by hand, or an Auto Deploy restart (not "already on") - count toward the missing ones
        if m := PET.search(l):
            if not p['pet'] or p['pet'][0] != int(m[1]): p['refill'], p['auto'] = 0, False
            p['pet'] = tuple(map(int, m.groups()))
        if m := HAND.search(l): p['refill'] += int(m[1])
        if re.search(r'(OK|MANUAL) pet_check.*Auto Deploying:', l): p['auto'] = True
        if SENT.search(l): p['sent'] = True                # tribe help request sent this game day, by any run
        if not use: continue
        if m := DUNGEON.match(l): p['dungeons'][m.group(1)] = int(m.group(2)), int(m.group(3))
        m = LINE.match(l)
        if not m or 'already OK this game day' in m.group(3): continue   # that one points at an earlier OK
        tag, name, text = m.groups()
        if tag == 'OK' and NOOP.search(text) and p['res'].get(name, ('',))[0] == 'OK': continue
        p['res'][name] = tag, text
        if c := re.search(r'daily chests \[([^\]]*)\]', text): p['chests'] |= {int(x) for x in re.findall(r'\d+', c.group(1))}
    return p


def coins(text):
    """Grocery shop coins {shop: n}: the 'coins:' tail (since 11-11), else derived from the buy lines (balance read
    before a buy)."""
    if m := re.search(r'coins: (.*)$', text):
        return {t: int(v) if v.isdigit() else v for t, v in re.findall(r'(\w+) (\S+)', m.group(1))}
    got = {t: int(b) - int(pr) for t, pr, b in re.findall(r'(\w+) \d+ bought for (\d+) \(balance (\d+)\)', text)}
    got.update({t: int(b) for t, b in re.findall(r'(\w+) \d+ skipped: \d+ > balance (\d+)', text)})
    return {t: got[t] for t in SHOP_TABS if t in got}


HIGH = {'sanctuary': 10000, 'tribe': 6000, 'ruins': 3000, 'realm': 12000}   # bold above these (Nick 2026-11-11)


def table(head, body, right):
    """Markdown table padded the way prettier writes it; right[i] = right-aligned column."""
    w = [max(3, *(len(c) for c in col)) for col in zip(head, *body)]
    row = lambda r: '| ' + ' | '.join(c.rjust(n) if a else c.ljust(n) for c, n, a in zip(r, w, right)) + ' |'
    return [row(head), '| ' + ' | '.join('-' * (n - 1) + ':' if a else '-' * n for n, a in zip(w, right)) + ' |'] + [row(r) for r in body]


def coin_table(c):
    """One row, a column per shop, thousands separators, bold above HIGH."""
    if not c: return ['Not read.']
    cell = lambda t, v: (f'**{v:,}**' if v > HIGH.get(t, float('inf')) else f'{v:,}') if isinstance(v, int) else v
    return table([t.capitalize() for t in c], [[cell(t, v) for t, v in c.items()]], [True] * len(c))


def outstanding(c):
    """{shop: n} above HIGH."""
    return {t: v for t, v in c.items() if isinstance(v, int) and v > HIGH.get(t, float('inf'))}


def rows(p):
    """[(done, line)] - the Daily Mission chest, then one per step."""
    res = p['res']
    folded = {'pet_check', 'tribe_chat', 'canyon'}           # shown in the pet_arena / tribe rows
    names = [n for n, _ in ORDER] + [n for n, _ in CATCHUP if n in res and n not in dict(ORDER) and n not in folded]
    rows = [(160 in p['chests'], f'**Daily Mission 160 chest** (claimed: {", ".join(map(str, sorted(p["chests"]))) or "none"})')]
    for n in names:
        tag, text = res.get(n, ('', 'not run'))
        if text.startswith('not in config'): continue
        done = tag in ('OK', 'SKIP')
        if n == 'pet_arena' and tag != 'SKIP':
            if p['pet']:
                c, y, k = p['pet']; r = p['refill']; done = k + r >= 40 or p['auto']
                more = (f', +{r} by hand since' if r else '') + (', Auto Deploy restarted since' if p['auto'] else '')
                text = f'deployments {c}/{y + 40} (+{k} today{more}); {text}'
            else: done = False; text = f'deployments not read yet (catch-up pet_check); {text}'
        if n == 'tribe' and tag:                             # request + canyon, each from its latest attempt (catch-up re-runs too)
            req, sent = res.get('tribe_chat', ('', text))[1], p['sent']   # a later "NOT SENT (cooldown)" = the earlier send's timer
            canyon = 'no empty platform' not in text or res.get('canyon', ('',))[0] == 'OK'
            done = sent and canyon
            text = f'request {"sent" if sent else "NOT sent"}, canyon {"done" if canyon else "NOT done"}; {req if "tribe_chat" in res else text}'
        if n == 'sanctuary':
            lost = re.search(r'floor (\d+) LOST', text)
            text = f'floors {10 if tag == "OK" else int(lost[1]) - 1 if lost else "?"}/10; {text}'
        if n == 'trials' and (short := [f'{k} {d}/{t}' for k, (d, t) in p['dungeons'].items() if d < t]):
            done = False; text = f'short: {", ".join(short)}; {text}'
        if any(int(a) < int(b) for a, b in re.findall(r'forge (\d+)/(\d+)', text)) and 'crystals' not in text: done = False   # out of crystals = all it could
        if n == 'grocery': text = re.sub(r',? ?coins: .*$', '', text)
        text = re.sub(r' \((screenshot |on Tribe chat;)[^)]*\)', '', re.sub(r'^(SKIP|MANUAL) ', '', text))[:240]
        rows.append((done, f'{n}: {"skipped, " if tag == "SKIP" else tag + " " if tag in ("FAIL", "MANUAL") else ""}{text}'))
    return rows


def render(acct, day, p):
    res, rows_ = p['res'], rows(p)
    todo, done = [t for d, t in rows_ if not d], [t for d, t in rows_ if d]
    weekday = datetime.date.fromisoformat(day).strftime('%a')
    return '\n'.join([f'# {acct} - dailies {day} ({weekday})', '',
                      '## Grocery coins', ''] + coin_table(coins(res.get('grocery', ('', ''))[1])) + ['',
                      f'{len(done)}/{len(rows_)} done. Runs: {", ".join(p["runs"])}. Source: `logs/{acct}/{day}.log`.', '',
                      f'## Not done ({len(todo)})', ''] + [f'- [ ] {t}' for t in todo]
                     + ['', f'## Done ({len(done)})', ''] + [f'- [x] {t}' for t in done]) + '\n'


def highlights(day, accts):
    """_highlights.md: each account's open boxes (up to the first ';'), then the coins above HIGH. accts = [(acct, p)]."""
    weekday = datetime.date.fromisoformat(day).strftime('%a')
    undone = [(a, [t.split(';')[0] for d, t in rows(p) if not d]) for a, p in accts]
    undone = [(a, ts) for a, ts in undone if ts]
    rich = [(a, outstanding(coins(p['res'].get('grocery', ('', ''))[1]))) for a, p in accts]
    rich = [(a, o) for a, o in rich if o]
    shops = [t for t in SHOP_TABS if any(t in o for _, o in rich)]
    out = [f'# Highlights - dailies {day} ({weekday})', '', f'## Undone ({len(undone)} of {len(accts)} accounts)', '']
    out += [l for a, ts in undone for l in [f'- **{a}**'] + [f'  - {t}' for t in ts]] or ['Nothing undone.']
    out += ['', '## Outstanding coins', '', 'Above sanctuary 10k, tribe 6k, ruins 3k, realm 12k.', '']
    out += table(['Account'] + [t.capitalize() for t in shops], [[a] + [f'{o[t]:,}' if t in o else '' for t in shops] for a, o in rich],
                 [False] + [True] * len(shops)) if rich else ['None.']
    return '\n'.join(out) + '\n'


def write(day, acct):
    log = f'{ROOT}/logs/{acct}/{day}.log'
    if not os.path.exists(log): return None
    p = parse(open(log))
    if not p['runs']: return None                        # no dailies that game day (catch-up only)
    out = f'{ROOT}/checklists/{day}/{acct}.md'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(render(acct, day, p))
    return out


def test():
    log = ['12:18:24 === 2026-11-11 12:18:24 daily.py kong (serial 1)',
           '12:19:00 OK pet_arena (25s): Auto Deploying: 1 sprites, Random Selection',
           '12:20:00 FAIL fishing (75s): waited 8s (screenshot /tmp/x.png)', '12:21:00 OK fishing (40s): auto started',
           '12:22:00 OK shop (10s): claimed [\'Free Benefits\']', '12:23:00     gem_mine: 4/5 done today (4 this run, paid [80, 160])',
           '12:23:01     moonlight_temple: 3/3 done today (3 this run, paid [80])', '12:23:02 OK trials (99s): gem_mine: 4/5 done today',
           '12:24:00 OK sanctuary (15s): swept', '12:25:00 OK divine (60s): pickaxes 0, forge 4/7',
           '12:26:00 OK grocery (90s): done; sanctuary 12 bought for 10000 (balance 13251), ruins 1 skipped: 3000 > balance 806',
           '12:30:00 MANUAL tribe (143s): MANUAL tribe done, request NOT SENT (cooldown 00:12:13: sent < 6 h ago); MANUAL no empty platform', '12:31:00 FAIL home after gate: lost the main screen; stop',
           '12:35:00 MANUAL events (60s): MANUAL 7777 daily; red dots left: [\'weekly_event\']',
           '12:40:00 OK daily_mission (68s): [\'daily chests [40, 80, 120]\']',
           '20:00:00 === 2026-11-11 20:00:00 daily.py kong --catch-up (serial 1)', '20:01:00 OK arena (9s): from catch-up',
           '20:05:00     pet deployments 116 (yesterday 80, +36 today)',
           '20:53:20 === 2026-11-11 20:53:20 daily.py kong --catch-up canyon (serial 1)', '20:54:00 OK canyon (60s): occupied',
           '21:00:00 === 2026-11-11 21:00:00 daily.py kong shop daily_mission (serial 1)', '21:00:01 OK shop (5s): claimed nothing',
           '21:01:00 OK daily_mission (27s): [\'daily chests [160]\']']
    p = parse(log)
    assert p['runs'] == ['12:18 full', '20:53 canyon (catch-up)', '21:00 shop daily_mission'], p['runs']
    assert p['res']['shop'][1].startswith('claimed [') and 'arena' not in p['res'] and p['pet'] == (116, 80, 36), p
    md = render('kong', '2026-11-11', p)
    top, bottom = md.split('## Done')
    assert '| Sanctuary | Ruins |' in top and '|     3,251 |   806 |' in top, md
    assert coin_table({'sanctuary': 10001, 'tribe': 6000, 'realm': 12500})[2] == '| **10,001** | 6,000 | **12,500** |'
    assert coins('done, coins: sanctuary 3251 / tribe ? / ruins 806') == {'sanctuary': 3251, 'tribe': '?', 'ruins': 806}
    for open_ in ('pet_arena: deployments 116/120 (+36 today)', 'trials: short: gem_mine 4/5', 'divine:',
                  'tribe: MANUAL request NOT sent, canyon done',
                  'events: MANUAL', 'arena: not run'):
        assert f'- [ ] {open_}' in top, (open_, md)
    for ok in ('**Daily Mission 160 chest**', 'sanctuary: floors 10/10; swept', 'fishing: auto started'):
        assert f'- [x] {ok}' in bottom, (ok, md)
    assert 'home' not in md
    h = highlights('2026-11-11', [('kong', p), ('tiger', parse(log[:1] + ['12:26:00 OK grocery (9s): done, coins: sanctuary 900 / tribe 22830']))])
    assert '- **kong**\n  - pet_arena: deployments 116/120 (+36 today)\n' in h, h
    assert '| tiger   | 22,830 |' in h and '| kong ' not in h, h
    q = parse(log[:1] + ['13:52:00     pet deployments 118 (yesterday 80, +38 today)',
                         '13:54:00     pet: deployed by hand (free attempt) x1, this round 1/4',
                         '13:58:00     pet deployments 118 (yesterday 80, +38 today)',
                         '13:59:00     pet: deployed by hand (free attempt) x1, this round 2/4', '13:59:30 OK pet_arena (9s): Auto Deploying: 1 sprites'])
    assert '- [x] pet_arena: deployments 118/120 (+38 today, +2 by hand since)' in render('dino', '2026-11-11', q), render('dino', '2026-11-11', q)
    q = parse(log[:1] + ['13:52:00     pet deployments 118 (yesterday 80, +38 today)', '13:54:00     pet: deployed by hand (free attempt) x1, this round 1/4',
                         '20:05:00     pet deployments 119 (yesterday 80, +39 today)', '20:05:30 OK pet_arena (9s): Auto Deploying: 1 sprites'])
    assert '- [ ] pet_arena: deployments 119/120 (+39 today)' in render('dino', '2026-11-11', q)
    print('ok')


if __name__ == '__main__':
    if sys.argv[1:] == ['--test']: test(); sys.exit()
    day = sys.argv[1] if len(sys.argv) > 1 else str(GAME_DAY)
    accts = sys.argv[2:] or sorted(os.listdir(f'{ROOT}/logs'))
    for a in accts:
        if p := write(day, a): print(f'checklist: {os.path.relpath(p, ROOT)}')
    accts = [(a, p) for a in sorted(os.listdir(f'{ROOT}/logs')) if os.path.exists(log := f'{ROOT}/logs/{a}/{day}.log')
             and (p := parse(open(log)))['runs']]
    if accts: open(f'{ROOT}/checklists/{day}/_highlights.md', 'w').write(highlights(day, accts))
