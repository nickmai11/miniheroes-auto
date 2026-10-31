#!/usr/bin/env python3
# Redeem a gift code: main screen -> menu ☰ -> Settings -> Redemption -> type code -> Redeem -> close back to main.
# usage: D=<serial> scripts/giftcode.py <CODE>   (main screen, or the Redemption dialog already open)
# Prints the game's reply (e.g. "invalid", "already redeemed", rewards). exit 1 = unexpected screen (v_giftcode.png).
import subprocess, sys, time
from flow import D, Stop, find, joined, main, ocr, tap_text, wait
from tap import tap as tap_wait

FIELD, REDEEM_X, SETTINGS_X = (540, 936), (916, 704), (968, 272)


def run(code):
    boxes = ocr()
    if not find(boxes, r'Redemption Code'):
        if not find(boxes, r'^Play Pass$'):           # other screen -> go to main, don't stop (Nick, 2026-10-31)
            from daily import home
            if not home(): raise Stop(f'could not reach the main screen; screen: {joined(ocr())[:200]}')
        tap_wait(994, 1625)                       # menu ☰
        tap_wait(820, find(wait(r'^Settings$'), r'^Settings$')[1])   # the icon; side-menu labels don't react
        tap_text(r'^Redemption$', boxes=wait(r'^Redemption$'))
        wait(r'Redemption Code')
    tap_wait(*FIELD)
    subprocess.run(['adb', '-s', D, 'shell', 'input', 'text', code])
    time.sleep(0.5)
    subprocess.run(['adb', '-s', D, 'shell', 'input', 'keyevent', '66'])   # Enter: close the keyboard
    time.sleep(1)
    boxes = ocr()
    if not find(boxes, r'^Redeem$'): raise Stop(f'no Redeem button after typing; screen: {joined(boxes)[:200]}')
    tap_text(r'^Redeem$', boxes=boxes, settle=False)
    boxes = wait(r'Tap anywhere to close|Invalid|redeemed|expired', 6)   # reward popup, or a toast over the dialog
    print(f'{code}: {joined(boxes)[:300]}', flush=True)
    if find(boxes, r'Tap anywhere to close'):    # success: Redemption dialog is gone, rewards over Settings
        tap_wait(540, 272)                        # Settings title (inert) dismisses the rewards
    else:
        wait(r'^Redeem$', 6); tap_wait(*REDEEM_X)
    tap_wait(*SETTINGS_X)


if __name__ == '__main__':
    main(run, sys.argv[1])
