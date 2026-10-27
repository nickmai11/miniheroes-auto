#!/usr/bin/env python3
# Excelsior Veins: One-Click Mining until pickaxes run out. Veins mining grid must be open.
# usage: D=<serial> scripts/veins.py   — exit 0 = pickaxes 0 (buy popup closed), 1 = unexpected screen.
# Why a script: Bino's helper (2026-10-28) looped One-Click + dismiss blindly 45x; pickaxes hit 0 at try 3 and
# every later try opened "Spend 120 diamonds to buy 5 Pickaxe" (one tap from Confirm). Stop at the FIRST popup.
# Never taps Confirm, the pickaxe "+", dynamite or drill.
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap

near = lambda p, c, tol=30: all(abs(a - b) <= tol for a, b in zip(p, c))
def buy_popup(im): return near(im.getpixel((540, 900)), (206, 215, 230)) and near(im.getpixel((938, 636)), (255, 255, 255), 15)
def grid(im): return near(im.getpixel((896, 1612)), (73, 105, 59), 40)  # One-Click Mining green, no popup


def main():
    im = grab()
    if buy_popup(im): return close(0)
    if not grid(im): print('not on the Veins grid; stop'); return 1
    for n in range(1, 41):  # ponytail: 80 pickaxes + refunds never needed >~15 taps; 40 is a hard stop
        im = tap(896, 1612)
        t0 = time.time()
        while not buy_popup(im) and not grid(im) and time.time() - t0 < 8:  # mining animation / Congratulations
            time.sleep(0.5); im = grab()
            if not buy_popup(im) and not grid(im): tap(540, 120); im = grab()
        if buy_popup(im): return close(n)
        if not grid(im): print(f'try {n}: unexpected screen; stop'); return 1
        print(f'try {n}: mined', flush=True)
    print('40 tries without reaching 0 pickaxes; stop'); return 1


def close(n):
    tap(938, 636)
    if buy_popup(grab()): print('buy popup did not close; stop'); return 1
    print(f'pickaxes 0 after {n} One-Click taps; buy popup closed (nothing bought)'); return 0


if __name__ == '__main__':
    sys.exit(main())
