#!/usr/bin/env python3
# Tribe: Sign-in, Tribe Trial (only if its card has a red dot), chat Request + Assist. All free.
# usage: D=<serial> scripts/tribe.py [--chat-only] [--no-request]      (main screen must be open; ends on the Tribe chat, dialog closed)
# Never types in chat. Canyon Clash / Poseidon stay with the helper. exit 1 = unexpected screen (v_tribe.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import re, sys, time
from flow import Stop, battle, find, grab, main, ocr, tap, tap_text, tap_wait, wait


def trial_red_dot():
    im = grab()  # red dot at the Trial card's top-right (bino s191 before / s201 after, 2026-10-28)
    return sum(1 for y in range(520, 620, 4) for x in range(1000, 1080, 4)
               if (lambda p: p[0] > 210 and p[1] < 70 and p[2] < 70)(im.getpixel((x, y)))) >= 4


def run(chat_only=False, request=True):
    tap_wait(448, 1780)                                       # Tribe
    wait(r'Tribe Trial', 10)
    if not chat_only: sign_in_and_trial()
    chat(request)


def sign_in_and_trial():
    tap_text(r'^Sign-in$', (400, 380, 700, 560))
    boxes = wait(r'Sign-in Reward|Signed.In', 8)
    if find(boxes, r'^Sign-in Reward$'):
        tap_text(r'^Sign-in Reward$', boxes=boxes); time.sleep(1.5); tap_wait(540, 120); print('sign-in: claimed')
        tap_wait(540, 1680)                                   # close the sign-in dialog
    elif find(boxes, r'^Signed-In$'): print('sign-in: already signed in (toast, no dialog)')  # Kong 2026-10-28
    else: print('sign-in: already signed in'); tap_wait(540, 1680)
    time.sleep(1.5); wait(r'Tribe Trial', 8)
    # dot read once right after the sign-in dialog closed was missed (dimmed?) - Chien Than's Trial left 0/1 (2026-11-01)
    if any(trial_red_dot() or time.sleep(1) for _ in range(3)):
        tap_wait(540, 735)
        wait(r'Flame Lord|Single Highest', 10)
        res = battle(r'Single Highest|Flame Lord', timeout=120)
        print(f'tribe trial: fought ({res[:80]})')
        tap_wait(92, 1810); wait(r'Tribe Trial', 8)
    else: print('tribe trial: no red dot (done today); skipped')


TIMER = r'^\d{1,2}:\d{2}:\d{2}$'                             # cooldown under the greyed Request (6 h after sending)


def cooldown(boxes=None):
    return next((t.strip() for x, y, w, h, t in boxes or ocr()
                 if re.fullmatch(TIMER, t.strip()) and 150 <= x + w // 2 <= 520 and 1690 <= y + h // 2 <= 1800), None)


def chat(request=True):
    tap_wait(800, 1806)                                       # Chat (auto-claims assist rewards)
    for y in (1631, 1636):
        tap_wait(174, y)
        boxes = ocr()
        if find(boxes, r'Help Request'): break
    else: raise Stop('Help Request Info did not open')
    # the tap alone proved nothing: on cooldown from the morning catch-up it did nothing, logged "tapped" (2026-11-07)
    cd = cooldown(boxes)
    if not request: req = f'skipped ({"cooldown " + cd if cd else "--no-request"})'
    elif cd: req = f'NOT SENT (cooldown {cd}: sent < 6 h ago)'
    else:
        r = find(boxes, r'Request$', (150, 1560, 520, 1760))
        if r: tap_wait(*r)
        for _ in range(6):
            cd = cooldown()
            if cd: break
            time.sleep(0.5)
        req = f'sent (cooldown {cd})' if cd else 'NOT SENT (no cooldown timer after the tap)'
    print(f'request: {req}')
    a = find(ocr(), r'^Assist$', (560, 1560, 960, 1760))
    if a: tap_wait(*a); print('assist: tapped')
    else: print('assist: button not found')
    tap_wait(968, 228)                                        # close the dialog
    print(f'tribe done, request {req} (on Tribe chat; back out and screenshot — Back can land on Recruit)')


if __name__ == '__main__':
    main(run, '--chat-only' in sys.argv, '--no-request' not in sys.argv)
