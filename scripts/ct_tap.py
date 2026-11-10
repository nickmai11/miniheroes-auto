#!/usr/bin/env python3
"""Crystal Throne text taps: D=<serial> scripts/ct_tap.py <step ...>  step = REGEX (tap the first OCR box matching it) or x,y.
Re-OCRs before every text step and prints the screen text after each step. Exit 1 + 'NO <regex>' when a label isn't on screen."""
import re, sys
from flow import Stop, joined, ocr, tap_text, tap_wait
for s in sys.argv[1:]:
    if re.fullmatch(r'\d+,\d+', s): tap_wait(*map(int, s.split(',')))
    else:
        try: tap_text(s)
        except Stop: print('NO', s, '|', joined(ocr())[:200]); sys.exit(1)
    print(s, '->', joined(ocr())[:220], flush=True)
