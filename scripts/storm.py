#!/usr/bin/env python3
# Play Storm Battlefield matches until tickets run out. Arena screen (yellow "Start Match") must be open.
# usage: D=<serial> scripts/storm.py   — polls every ~0.5 s, so a match costs only its real length.
# Free tickets: in ONE visit of the "+" popup, tap the left green button (Free / Miễn phí / Claim+video ad)
# until it turns grey, watching the ad when there is one (Nick, 2026-10-26); the next time tickets hit 0
# the script closes the popup and stops. Never taps the 30-gem Redeem.
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab
D = os.environ['D']
near = lambda p, c, tol=30: all(abs(a - b) <= tol for a, b in zip(p, c))
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


def main():
    if not arena(grab()):
        print('not on arena screen; stop'); return 1
    claimed, n = False, 0
    while n < 30:
        im = grab()
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
    sys.exit(main())
