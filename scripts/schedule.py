#!/usr/bin/env python3
"""Schedule a task with launchd, the way fr_all.sh is scheduled (Nick, 2026-11-17).
usage: scripts/schedule.py add <name> <when> <command> [arg ...]
       scripts/schedule.py list
       scripts/schedule.py rm <name>
<when> (Mac local time):
  +5m / +2h / +1d        once, that long from now
  21:45                  once, the next 21:45
  2026-11-20@05:00       once, that date
  daily@17:00            every day
  mon,wed,fri@05:00      those weekdays, every week
A one-time job removes itself after it ran. Job com.nickm.miniheroes-<name> runs <command> from the repo root under
`caffeinate -i -s` (no idle sleep mid-run), output -> logs/launchd-<name>.log. A Mac asleep at that time runs the job when
it next wakes (launchd); no pmset wake is set here: pmset has one repeat slot, used by fr's 04:29 Wed/Thu/Fri wake."""
import datetime as dt, glob, os, plistlib, subprocess, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LA = os.path.expanduser('~/Library/LaunchAgents')
GUI = f'gui/{os.getuid()}'
DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']   # launchd Weekday 0 = Sunday


def path(name): return f'{LA}/com.nickm.miniheroes-{name}.plist'


def at(t): return [{'Month': t.month, 'Day': t.day, 'Hour': t.hour, 'Minute': t.minute}]


def parse(when, now):
    """-> (launchd StartCalendarInterval list, one-time?)"""
    if when.startswith('+'):
        return at(now + dt.timedelta(minutes=int(when[1:-1]) * {'m': 1, 'h': 60, 'd': 1440}[when[-1]])), True
    day, _, hhmm = when.rpartition('@')
    h, m = map(int, hhmm.split(':'))
    assert 0 <= h < 24 and 0 <= m < 60, f'bad time {hhmm}'
    if day == 'daily': return [{'Hour': h, 'Minute': m}], False
    if not day:
        t = now.replace(hour=h, minute=m)
        return at(t if t > now else t + dt.timedelta(days=1)), True
    if day[0].isdigit():
        t = dt.datetime.strptime(day, '%Y-%m-%d').replace(hour=h, minute=m)
        assert t > now, f'{when} is in the past'
        return at(t), True
    return [{'Hour': h, 'Minute': m, 'Weekday': DAYS.index(d[:3].lower())} for d in day.split(',')], False


def show(iv):
    def day(i):
        if 'Weekday' in i: return DAYS[i['Weekday']]
        return '%02d-%02d' % (i['Month'], i['Day']) if 'Day' in i else 'daily'
    return ' '.join('%s@%02d:%02d' % (day(i), i['Hour'], i['Minute']) for i in (iv if isinstance(iv, list) else [iv]))


def test():
    now = dt.datetime(2026, 11, 17, 21, 50)
    assert parse('+5m', now) == (at(dt.datetime(2026, 11, 17, 21, 55)), True)
    assert parse('+3h', now) == (at(dt.datetime(2026, 11, 18, 0, 50)), True)
    assert parse('22:00', now) == (at(dt.datetime(2026, 11, 17, 22, 0)), True)
    assert parse('21:00', now) == (at(dt.datetime(2026, 11, 18, 21, 0)), True)
    assert parse('2026-11-20@05:00', now) == (at(dt.datetime(2026, 11, 20, 5, 0)), True)
    assert parse('daily@17:05', now) == ([{'Hour': 17, 'Minute': 5}], False)
    assert parse('Mon,fri@5:00', now)[0] == [{'Hour': 5, 'Minute': 0, 'Weekday': 1}, {'Hour': 5, 'Minute': 0, 'Weekday': 5}]
    for bad in ('25:00', '2026-11-01@05:00', 'xyz@05:00'):
        try: parse(bad, now); raise SystemExit(f'accepted {bad}')
        except (AssertionError, ValueError): pass
    print('ok')


cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ('list', [])
if cmd == 'add' and len(args) >= 3:
    name, when, *run = args
    iv, once = parse(when, dt.datetime.now().replace(second=0, microsecond=0))
    if once:   # run, then unschedule itself (launchd has no year: it would fire again next year)
        run = ['/bin/sh', '-c', f'"$@"; s=$?; "$0" rm {name}; exit $s', os.path.abspath(__file__), *run]
    p = {'Label': f'com.nickm.miniheroes-{name}', 'WorkingDirectory': R,
         'EnvironmentVariables': {'PATH': os.environ['PATH']},   # the PATH that works now (adb, python3, node, claude)
         'ProgramArguments': ['/usr/bin/caffeinate', '-i', '-s', *run], 'StartCalendarInterval': iv,
         'StandardOutPath': f'{R}/logs/launchd-{name}.log', 'StandardErrorPath': f'{R}/logs/launchd-{name}.log'}
    subprocess.run(['launchctl', 'bootout', f"{GUI}/{p['Label']}"], capture_output=True)   # replace an existing one
    with open(path(name), 'wb') as f: plistlib.dump(p, f)
    subprocess.run(['launchctl', 'bootstrap', GUI, path(name)], check=True)
    print(f"scheduled {name}: {show(iv)}{' once' if once else ''} -> {' '.join(args[2:])}  (log logs/launchd-{name}.log)")
elif cmd == 'rm' and len(args) == 1:
    os.remove(path(args[0]))   # file first: a one-time job runs this itself and the bootout ends it
    print(f'removed {args[0]}', flush=True)
    subprocess.run(['launchctl', 'bootout', f'{GUI}/com.nickm.miniheroes-{args[0]}'], capture_output=True)
elif cmd == 'list':
    for f in sorted(glob.glob(path('*'))):
        with open(f, 'rb') as fh: p = plistlib.load(fh)
        if 'StartCalendarInterval' not in p: continue
        on = subprocess.run(['launchctl', 'print', f"{GUI}/{p['Label']}"], capture_output=True).returncode == 0
        run = [a for a in p['ProgramArguments'] if a not in ('/usr/bin/caffeinate', '-i', '-s')]
        print(f"{p['Label'].split('miniheroes-')[1]:10} {show(p['StartCalendarInterval']):30} {' '.join(run)}"
              f"{'' if on else '  (NOT LOADED)'}")
elif cmd == 'test':
    test()
else:
    sys.exit(__doc__)
