#!/usr/bin/env python3
# Play Storm Battlefield matches until tickets run out. Arena screen (yellow "Start Match") must be open.
# usage: D=<serial> scripts/storm.py [account]   — polls every ~0.5 s, so a match costs only its real length.
# Free tickets: in ONE visit of the "+" popup, tap the left green button (Free / Claim+video ad)
# until it turns grey, watching the ad when there is one (Nick, 2026-10-26); the next time tickets hit 0
# the script closes the popup and stops. Never taps the 30-gem Redeem.
# Lineup (Nick, 2026-10-27, after helpers played with the leftover 1-hero lineup): sets the full lineup
# (Quick Deploy) before the first match and leaves only the first hero after (ui-routine Storm steps 2 + 6).
# storm_max_rank in the account file (Nick, 2026-10-31: Aminor/Kong "King +10", default King +1): read the rank under the badge
# ("King", "King +3", OCR) before every match; at/above the cap stop, even with tickets left.
# UNTESTED (written 2026-10-27) — verify on one account before a multi-account run.
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait
from flow import near, ocr
TIERS = ['Bronze', 'Silver', 'Gold', 'Glory', 'King']


def rank(text):
    """'King +10' -> (4, 10); 'King' / 'King 0' (the ⓘ icon) -> (4, 0); None if no tier."""
    m = re.search(r'(' + '|'.join(TIERS) + r')\s*(?:\+\s*(\d+))?', text)
    return m and (TIERS.index(m.group(1)), int(m.group(2) or 0))


def max_rank(account):
    """storm_max_rank from the account file; default King +1 (Nick, 2026-10-31: the rest stop at King +1)."""
    try: m = re.search(r'storm_max_rank:\s*([^#\n]+)', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts', account + '.yaml')).read())
    except (OSError, TypeError): m = None     # no account (old daily.py) -> default
    return rank(m.group(1)) if m else (4, 1)


def cur_rank(im):
    return rank(' '.join(t for x, y, w, h, t in ocr(im) if 400 < x + w // 2 < 700 and 560 < y + h // 2 < 720))
D = os.environ['D']
def arena(im): p = im.getpixel((400, 1580)); return p[0] > 200 and p[1] > 150 and p[2] < 80  # Start Match yellow
# "+" popup: left button body. y=1274 hits the "Free" text / camera icon of the ad "Claim" variant, so
# sample above it: green (123,206,49) = chances left, grey (181,178,181) = "Chances: 0"
def free_btn(im):
    p = im.getpixel((260, 1250))
    return 'green' if near(p, (123, 206, 49)) else 'grey' if near(p, (181, 178, 181)) else None
def tap(x, y): subprocess.run(['adb', '-s', D, 'shell', 'input', 'tap', str(x), str(y)])
def close_popup(): tap(100, 1150); time.sleep(1)


def focus():
    out = subprocess.run(['adb', '-s', D, 'shell', 'dumpsys', 'window'], capture_output=True, text=True).stdout
    return next((l for l in out.splitlines() if 'mCurrentFocus' in l), '')


def wait_ad():
    """After tapping Claim: if an ad (other activity) took over, let it play, then Back out of it.
    Back before the video ends aborts it with no reward (chance not used), so wait 35 s first."""
    t0 = time.time(); time.sleep(2)
    while time.time() - t0 < 120:
        if 'AppActivity' in focus(): return True        # back in the game (or there was no ad)
        if time.time() - t0 > 35: subprocess.run(['adb', '-s', D, 'shell', 'input', 'keyevent', '4'])
        time.sleep(3)
    return False


def claim_free():
    """Popup is open: tap the left button while it's green (max 8 tries), then close. Returns taps."""
    got = 0
    while got < 8 and free_btn(grab()) == 'green':
        tap(350, 1274); got += 1
        if not wait_ad(): print('ad did not close in 120 s; stop'); sys.exit(1)
        time.sleep(1); tap(540, 200); time.sleep(1)    # dismiss the Congratulations popup each claim
    if free_btn(grab()): close_popup()
    return got


def lineup(full):
    """Lineup (960,1600) -> Quick Deploy (top 5) or clear + first hero -> Save -> back to the arena."""
    tap_wait(960, 1600)
    if full: tap_wait(984, 1800)
    else: tap_wait(1006, 1084); tap_wait(140, 1250)
    tap_wait(540, 1808); tap_wait(88, 1812)
    t0 = time.time()
    while not arena(grab()):
        if time.time() - t0 > 10: print(f'lineup ({"full" if full else "1 hero"}): not back on arena; stop'); return False
        time.sleep(0.5)
    print(f'lineup set: {"full (Quick Deploy)" if full else "first hero only"}', flush=True); return True


def main(account=None):
    if not arena(grab()):
        print('not on arena screen; stop'); return 1
    cap = max_rank(account)
    if cap and (cur_rank(grab()) or (-1,)) >= cap: print(f'rank {cur_rank(grab())} already at max {cap}; no matches'); return 0
    if not lineup(True): return 1
    r = play(cap)
    if r == 0 and not lineup(False): return 1
    return r


def play(cap=None):
    claimed, n = False, 0
    while n < 30:
        im = grab()
        if cap and arena(im):
            r = cur_rank(im)
            if r is None: print('rank unreadable with a max rank set; stop'); return 1
            if r >= cap: print(f'rank {TIERS[r[0]]} +{r[1]} reached max; done (tickets left)', flush=True); return 0
        if free_btn(im) and not arena(im):           # popup open (we opened it or the game did at 0 tickets)
            if claimed or free_btn(im) == 'grey':
                close_popup(); print('out of tickets (free chances checked once); done'); return 0
            claimed = True; print(f'tapped free button {claim_free()}x', flush=True); continue
        if not arena(im):
            print('unexpected screen; stop'); return 1
        before = im.getpixel((560, 1430))             # ticket counter digit
        tap(540, 1610); t0 = time.time(); time.sleep(1.5)
        im = grab()
        if free_btn(im) and not arena(im): continue    # 0 tickets -> game opened the "+" popup
        if arena(im) and im.getpixel((560, 1430)) == before:
            if claimed: print('Start Match did nothing; done'); return 0
            tap(642, 1428); time.sleep(1.5); continue  # open "+" once to check free chances
        while time.time() - t0 < 150:
            im = grab()
            if arena(im): break
            if free_btn(im): break                      # popup, not a battle: handled at loop top
            if time.time() - t0 > 4: tap(540, 120)      # dismiss Victory/Defeat once it shows
            time.sleep(0.5)
        else:
            print('match did not finish in 150 s; stop'); return 1
        n += 1; print(f'match {n}: {time.time() - t0:.0f}s', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
