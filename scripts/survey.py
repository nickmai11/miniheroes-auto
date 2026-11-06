#!/usr/bin/env python3
"""Submit a Google Form survey (from an in-game mail) once per account, neutral answers (Nick, 2026-11-06).

usage: scripts/survey.py <form url | adb serial> [account ...]     (default: every accounts/*.yaml with a game_id)
  url    = forms.gle/... or docs.google.com/forms/... link
  serial = 127.0.0.1:<port> of an instance whose mail link was just tapped: the URL is read from the browser intent
Answers: short/paragraph text -> 'n/a'; linear scale -> the middle; radio/checkbox -> an option saying fine/no change
if there is one, else the first; the question whose title mentions "ID" -> the account's game_id. --dry-run prints.
"""
import glob, json, os, re, subprocess, sys, urllib.parse

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def curl(url, data=None):  # curl, not urllib: python has no system certs here (Proxyman cert in the chain)
    r = subprocess.run(['curl', '-sL', '-w', '\n%{url_effective}', url] + (['--data', data] if data else []), capture_output=True, text=True).stdout
    return r.rsplit('\n', 1)


def accounts(names):
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'accounts', '*.yaml'))):
        n = os.path.basename(f)[:-5]
        g = re.search(r'^\s*game_id:\s*(\d+)', open(f).read(), re.M)
        if g and (not names or n in names): out[n] = g.group(1)
    return out


def url_from_device(serial):
    t = subprocess.run(['adb', '-s', serial, 'shell', 'dumpsys', 'activity', 'activities'], capture_output=True, text=True).stdout
    m = re.search(r'dat=(https?://\S+)', t)
    if not m: sys.exit('no browser intent on the device: tap the mail link first')
    return m.group(1)


def fetch(url):
    h, final = curl(url)
    d = json.loads(re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);</script>', h, re.S).group(1))
    fbzx = re.search(r'name="fbzx" value="([^"]*)"', h).group(1)
    qs = [(q[1], q[3], e[0], [o[0] for o in (e[1] or []) if o[0]]) for q in d[1][1] if q[4] for e in q[4]]
    return final.split('/viewform')[0] + '/formResponse', fbzx, qs


def answer(title, kind, opts):
    if re.search(r'\bID\b', title): return 'ID'
    if kind in (0, 1): return 'n/a'
    if kind == 18: return opts[len(opts) // 2]
    fine = [o for o in opts if re.search(r'\b(fine|no changes?|neutral|nothing)\b', o, re.I)]
    return (fine or opts)[0]


def main():
    args = [a for a in sys.argv[1:] if a != '--dry-run']; dry = '--dry-run' in sys.argv
    if not args: sys.exit(__doc__)
    url = url_from_device(args[0]) if re.match(r'^[\d.]+:\d+$', args[0]) else args[0]
    post, fbzx, qs = fetch(url)
    plan = [(t, eid, answer(t, k, o)) for t, k, eid, o in qs]
    for t, eid, a in plan: print(f'  {t[:70]!r} -> {a}')
    if dry: return
    for name, gid in accounts(args[1:]).items():
        data = {f'entry.{eid}': (gid if a == 'ID' else a) for _, eid, a in plan}
        data.update(fvv='1', pageHistory='0', fbzx=fbzx)
        h, _ = curl(post, urllib.parse.urlencode(data))
        ok = 'Thank you' in h or 'recorded' in h or 'ViewResponseConfirmation' in h
        print(f'{name} {gid}: {"submitted" if ok else "NOT confirmed"}')
        if not ok: open(f'v_survey_{name}.html', 'w').write(h)


if __name__ == '__main__': main()
