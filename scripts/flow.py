"""OCR helpers for the mission scripts: find buttons by their text, wait for a screen, fail loudly.
Text matching is English (every account's UI language). An unexpected screen times out a wait and the script
stops with exit 1 (Stop), never guessing."""
import os, re, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']


class Stop(Exception): pass


def tap(x, y): subprocess.run(['adb', '-s', D, 'shell', 'input', 'tap', str(x), str(y)])


def swipe(x0, y0, x1, y1, ms=500): subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', *map(str, (x0, y0, x1, y1, ms))])


def ocr(im=None):
    """[(x, y, w, h, text)] in device coords, top-left origin."""
    binary = os.path.join(HERE, 'ocr')
    if not os.path.exists(binary):
        subprocess.run(['swiftc', '-O', binary + '.swift', '-o', binary], check=True)
    with tempfile.NamedTemporaryFile(suffix='.png') as f:
        (im or grab()).save(f.name)
        out = subprocess.run([binary, f.name], capture_output=True, text=True).stdout
    boxes = []
    for line in out.splitlines():
        xywh, _, t = line.partition('\t')
        boxes.append((*map(int, xywh.split()), t))
    return boxes


def find(boxes, pattern, region=(0, 0, 1080, 1920)):
    """Center (x, y) of the first box whose text matches pattern (re.search) inside region x0,y0,x1,y1."""
    x0, y0, x1, y1 = region
    for x, y, w, h, t in boxes:
        if x0 <= x + w // 2 <= x1 and y0 <= y + h // 2 <= y1 and re.search(pattern, t):
            return x + w // 2, y + h // 2
    return None


def joined(boxes): return ' | '.join(b[4] for b in boxes)


def wait(pattern, timeout=10, region=(0, 0, 1080, 1920)):
    """Poll until a box matches; returns the boxes. Stop on timeout."""
    t0 = time.time()
    while True:
        boxes = ocr()
        if find(boxes, pattern, region): return boxes
        if time.time() - t0 > timeout: raise Stop(f'waited {timeout}s for {pattern!r}; screen: {joined(boxes)[:200]}')
        time.sleep(0.7)


def tap_text(pattern, region=(0, 0, 1080, 1920), boxes=None, settle=True):
    p = find(boxes or ocr(), pattern, region)
    if not p: raise Stop(f'no button {pattern!r} on screen')
    tap_wait(*p) if settle else tap(*p)
    return p


def battle(start_screen, timeout=180):
    """Challenge (bottom) -> lineup Start -> result -> close -> back on start_screen. Never 'Challenge again'.
    Returns the result screen's text."""
    tap_text(r'^Challenge$', (0, 1600, 1080, 1920))
    boxes = wait(r'^Start$', 10)
    if not find(boxes, r'^Start$', (0, 1650, 1080, 1920)): raise Stop('Start not at the bottom of the lineup screen')
    tap_text(r'^Start$', (0, 1650, 1080, 1920), boxes)
    res = joined(wait(r'Tap anywhere to close', timeout))
    t0 = time.time()
    while time.time() - t0 < 15:
        boxes = ocr()
        if find(boxes, start_screen): return res
        c = find(boxes, r'^Confirm$')
        tap(*(c or (540, 1700))); time.sleep(1.5)   # Confirm, or tap below "Challenge again" (never on it)
    raise Stop(f'result screen did not close back to {start_screen!r}')


def adventure(card):
    """Main screen -> Adventure -> the card's GO (the GO box ~170 px below the card name)."""
    tap_wait(100, 1460)
    boxes = wait(r'Tower of the Throne', 10)
    if not find(boxes, card):
        swipe(540, 1500, 540, 700); time.sleep(1); boxes = ocr()
    n = find(boxes, card)
    if not n: raise Stop(f'{card!r} not on the Adventure list')
    go = find(boxes, r'^GO', (600, n[1] + 60, 1080, n[1] + 300))
    if not go: raise Stop(f'no GO under {card!r}')
    tap_wait(*go)


def main(fn, *args):
    """Run fn; Stop -> screenshot v_<script>.png, exit 1."""
    try:
        r = fn(*args)
        sys.exit(r or 0)
    except Stop as e:
        name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        grab().resize((540, 960)).save(f'v_{name}.png')
        print(f'{e}; stop (screenshot v_{name}.png)'); sys.exit(1)
