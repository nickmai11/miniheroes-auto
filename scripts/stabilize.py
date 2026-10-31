#!/usr/bin/env python3
# Clear the start-up event popups until the bare main screen shows (Nick, 2026-10-28: "stable" = no popup).
# usage: D=<serial> [NAME=<mumu instance>] scripts/stabilize.py   (boot.sh passes NAME; game past the Start button)
# Account check (Nick, 2026-10-31): the ID top-right must be the account file's game_id; else switch with
# ☰ -> Settings -> Server -> the "S<server>" row -> Confirm (Kong reopened on S288 MRKONG II instead of S220).
# Each popup: tick "Do not remind me today" if it has one, then tap its X (top-right grey-blue square, white cross).
# exit 0 = main screen clear, 1 = popup it can't close (screenshot v_stabilize.png) -> close it by hand.
# Popup open = main screen's blue Recruit icon dimmed (0,158,230 -> ~0,33,50 under Dino's anniversary popup).
import glob, os, re, time
from flow import find, grab, ocr, tap_text, wait
from tap import tap as tap_wait

near = lambda p, c, tol=40: all(abs(a - b) <= tol for a, b in zip(p, c))
def is_main(im): return near(im.getpixel((92, 1788)), (0, 158, 230))


def close_x(im):
    """Centre of the popup's X button: the 64px block (right side, upper half) with the most white cross pixels that also
    touches the grey-blue frame. Frame-only blocks have <=34/256 white, the X ~80 (Dino anniversary popup, 2026-10-28)."""
    best, pos = 0, None
    for y0 in range(80, 1000, 16):
        for x0 in range(700, 1016, 16):
            ring = white = 0
            for y in range(y0, y0 + 64, 4):
                for x in range(x0, x0 + 64, 4):
                    p = im.getpixel((x, y))
                    ring += near(p, (115, 125, 156), 22); white += near(p, (255, 253, 255), 12)
            if ring >= 10 and white >= 50 and white > best: best, pos = white, (x0 + 32, y0 + 32)
    return pos


def account():
    """(game_id, server) from the accounts/*.yaml whose mumu_instance is $NAME, else (None, None)."""
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts', '*.yaml')):
        t = open(f).read()
        if re.search(r'mumu_instance:\s*' + re.escape(os.environ.get('NAME', '\0')) + r'\s*$', t, re.M):
            g, s = re.search(r'game_id:\s*(\d+)', t), re.search(r'server:\s*(\d+)', t)
            return g and g.group(1), s and s.group(1)
    return None, None


def check_account():
    """Main screen: 'ok' (right account / nothing to check), 'switched' (popups come back) or 'fail'."""
    gid, server = account()
    if not gid: return 'ok'
    # switch only on a different full ID read twice: an empty/garbled read (ID not drawn yet) is not a wrong account
    seen = []
    for _ in range(8):
        top = ' '.join(t for x, y, w, h, t in ocr() if y < 40)
        if gid in top: return 'ok'
        m = re.search(r'\d{8}', top)
        if m: seen.append(m.group())
        if len(seen) >= 2 and seen[-1] == seen[-2]: break
        time.sleep(1)
    else: print(f'account ID unreadable ({top[:30]}); not switching'); return 'ok'
    if not server: print(f'wrong account ({top[:30]}), no server in the account file; stop'); return 'fail'
    print(f'wrong account ({top[:30]}), switching to S{server}', flush=True)
    tap_wait(994, 1625); b = wait(r'^Settings$'); tap_wait(820, find(b, r'^Settings$')[1])
    b = wait(r'Redemption'); tap_wait(*find(b, r'^Server$'))
    b = wait(r'Recommended'); row = find(b, r'^S' + server + r'\b')
    if not row: print(f'S{server} not on the Server list (other ranges unmapped); stop'); return 'fail'
    tap_wait(row[0], row[1] + 16); b = wait(r'Switch to Server ' + server)
    tap_text(r'^Confirm$', boxes=b)
    wait(gid, 60)                                   # reloads straight into the game (~6 s), popups again
    return 'switched'


def main():
    switched = False
    for n in range(14):  # ponytail: ~3 stacked popups seen at most (x2 after a server switch); 14 is a hard stop
        im = grab()
        if is_main(im):
            time.sleep(1.5)                                   # popups slide in late: confirm once more
            if not is_main(grab()): continue
            r = 'ok' if switched else check_account()
            if r == 'fail': return 1
            if r == 'ok': print(f'stable ({n} popups closed{", account switched" if switched else ""})'); return 0
            switched = True; continue
        boxes = ocr(im)
        if find(boxes, r'Do not remind me today'): tap_text(r'Do not remind me today', boxes=boxes); time.sleep(0.5)
        x = close_x(grab())
        if not x: break
        tap_wait(*x); time.sleep(1)
    grab().resize((540, 960)).save('v_stabilize.png'); print('popup not closable; stop (screenshot v_stabilize.png)'); return 1


if __name__ == '__main__':
    raise SystemExit(main())
