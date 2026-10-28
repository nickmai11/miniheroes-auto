#!/usr/bin/env python3
# Tribe: Sign-in, Tribe Trial (only if its card has a red dot), chat Request + Assist. All free.
# usage: D=<serial> scripts/tribe.py [--chat-only]      (main screen must be open; ends on the Tribe chat, dialog closed)
# Never types in chat. Canyon Clash / Poseidon stay with the helper. exit 1 = unexpected screen (v_tribe.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import sys, time
from flow import Stop, battle, find, grab, main, ocr, tap, tap_text, tap_wait, wait


def trial_red_dot():
    im = grab()  # red dot at the Trial card's top-right (bino s191 before / s201 after, 2026-10-28)
    return sum(1 for y in range(520, 620, 4) for x in range(1000, 1080, 4)
               if (lambda p: p[0] > 210 and p[1] < 70 and p[2] < 70)(im.getpixel((x, y)))) >= 4


def run(chat_only=False):
    tap_wait(448, 1780)                                       # Tribe
    wait(r'Tribe Trial', 10)
    if not chat_only: sign_in_and_trial()
    chat()


def sign_in_and_trial():
    tap_text(r'^Sign-in$', (400, 380, 700, 560))
    boxes = wait(r'Sign-in Reward|Signed In', 8)
    if find(boxes, r'^Sign-in Reward$'):
        tap_text(r'^Sign-in Reward$', boxes=boxes); time.sleep(1.5); tap_wait(540, 120); print('sign-in: claimed')
    else: print('sign-in: already signed in')
    tap_wait(540, 1680)                                       # close the sign-in dialog
    wait(r'Tribe Trial', 8)
    if trial_red_dot():
        tap_wait(540, 735)
        wait(r'Flame Lord|Single Highest', 10)
        res = battle(r'Single Highest|Flame Lord', timeout=120)
        print(f'tribe trial: fought ({res[:80]})')
        tap_wait(92, 1810); wait(r'Tribe Trial', 8)
    else: print('tribe trial: no red dot (done today); skipped')


def chat():
    tap_wait(800, 1806)                                       # Chat (auto-claims assist rewards)
    for y in (1631, 1636):
        tap_wait(174, y)
        boxes = ocr()
        if find(boxes, r'Help Request'): break
    else: raise Stop('Help Request Info did not open')
    r = find(boxes, r'Request$', (150, 1560, 520, 1760))
    if r: tap_wait(*r); print('request: tapped (greyed if on cooldown)')
    a = find(ocr(), r'^Assist$', (560, 1560, 960, 1760))
    if a: tap_wait(*a); print('assist: tapped')
    else: print('assist: button not found')
    tap_wait(968, 228)                                        # close the dialog
    print('tribe done (on Tribe chat; back out and screenshot — Back can land on Recruit)')


if __name__ == '__main__':
    main(run, '--chat-only' in sys.argv)
