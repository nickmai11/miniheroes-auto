#!/usr/bin/env python3
# Offline check of tap.py's display scaling: scripts think in 1080x1920, a 900x1600 Phone display is upscaled in grab()
# and coords go back down in dev() (Nick 2026-11-25). usage: python3 scripts/test_tap.py
import os, sys, types
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tap


def frame(w, h, rgba=(10, 200, 30, 255)):
    tap.subprocess.run = lambda *a, **k: types.SimpleNamespace(stdout=w.to_bytes(4, 'little') + h.to_bytes(4, 'little') + bytes(4) + bytes(rgba) * (w * h))
    return tap.grab()


im = frame(900, 1600)
assert im.size == (1080, 1920) and im.getpixel((1079, 1919)) == (10, 200, 30), (im.size, im.getpixel((1079, 1919)))
assert tap.dev(540, 1920, 92, 1788) == ['450', '1600', '77', '1490'], tap.dev(540, 1920, 92, 1788)
assert frame(600, 1080).size == (600, 1080) and tap.SIZE['test'] == 900          # odd boot frame: untouched, scale kept
assert frame(1080, 1920).size == (1080, 1920) and tap.dev(92, 1788) == ['92', '1788']
print('ok')
