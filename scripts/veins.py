#!/usr/bin/env python3
# Excelsior Veins: One-Click Mining until pickaxes run out. Veins mining grid must be open.
# usage: D=<serial> scripts/veins.py   — exit 0 = pickaxes 0 (buy popup closed), 1 = unexpected screen.
# Why a script: Bino's helper (2026-10-28) looped One-Click + dismiss blindly 45x; pickaxes hit 0 at try 3 and
# every later try opened "Spend 120 diamonds to buy 5 Pickaxe" (one tap from Confirm). Stop at the FIRST popup.
# Never taps Confirm, the pickaxe "+", dynamite or drill.
# Also stops on the pickaxe counter "0/M" (bottom centre): accounts with < 120 gems get NO buy popup at 0, the
# grid just stays (Aminor 2026-10-28: 40 "mined" taps at 0/77, twice).
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap
from flow import ocr, near


def pickaxes(im):
    """Pickaxe counter N/M under the pickaxe button. Full-frame OCR misreads its thin white digits ("0/77" -> "Of7z",
    Aminor 2026-10-28), so OCR an enlarged black-on-white crop pasted on a blank frame."""
    from PIL import Image
    c = im.crop((520, 1795, 720, 1865)).convert('L').point(lambda v: 0 if v > 200 else 255).resize((600, 210))
    big = Image.new('RGB', (1080, 1920), 'white'); big.paste(c.convert('RGB'), (200, 800))
    m = re.search(r'(\d+)\s*/\s*\d+', ' '.join(b[4] for b in ocr(big)).translate(str.maketrans('OoОо', '0000')))
    return int(m.group(1)) if m else None


def buy_popup(im): return near(im.getpixel((540, 900)), (206, 215, 230)) and near(im.getpixel((938, 636)), (255, 255, 255), 15)
def grid(im): return near(im.getpixel((940, 1600)), (123, 202, 49))  # One-Click Mining green (dimmed under a popup)


def main():
    im = grab()
    if buy_popup(im): return close(0)
    if not grid(im): print('not on the Veins grid; stop'); return 1
    for n in range(1, 41):  # ponytail: 80 pickaxes + refunds never needed >~15 taps; 40 is a hard stop
        for _ in range(3):                              # counter can be mid-animation: re-read a fresh frame
            k = pickaxes(grab())
            if k is not None: break
            time.sleep(0.7)
        if k == 0: print(f'pickaxes 0 after {n - 1} One-Click taps (no buy popup)'); return 0
        im = tap(940, 1600)
        t0 = time.time()
        while not buy_popup(im) and not grid(im) and time.time() - t0 < 8:  # mining animation / Congratulations
            time.sleep(0.5); im = grab()
            if not buy_popup(im) and not grid(im): tap(540, 120); im = grab()
        if buy_popup(im): return close(n)
        if not grid(im): print(f'try {n}: unexpected screen; stop'); return 1
        print(f'try {n}: mined (pickaxes were {k})', flush=True)
    print('40 tries without reaching 0 pickaxes; stop'); return 1


def close(n):
    tap(938, 636)
    if buy_popup(grab()): print('buy popup did not close; stop'); return 1
    print(f'pickaxes 0 after {n} One-Click taps; buy popup closed (nothing bought)'); return 0


if __name__ == '__main__':
    sys.exit(main())
