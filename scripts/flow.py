"""OCR helpers for the mission scripts: find buttons by their text, wait for a screen, fail loudly.
Text matching is English (every account's UI language). An unexpected screen times out a wait and the script
stops with exit 1 (Stop), never guessing."""
import os, re, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']


class Stop(Exception): pass


near = lambda p, c, tol=30: all(abs(a - b) <= tol for a, b in zip(p, c))


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


def tickets_full(boxes):
    """"Current entry tickets have reached the max" popup (can pop over any screen): Confirm (opens the Arena), spend
    every ticket with arena.py, back to the main screen. True if it was up. The interrupted step's screen is gone, so
    callers redo it (Nick 2026-10-31: the rule is exhaust them now; Cancel + arena2 later wasted the refills)."""
    t = joined(boxes)
    if not ('reached the' in t and 'max' in t): return False
    acct = os.environ.get('ACCOUNT')
    if not acct: raise Stop('MATCH_FULL popup but no ACCOUNT env to run arena.py with')
    c = find(boxes, r'^Confirm$')
    if not c: raise Stop('MATCH_FULL popup without a Confirm button')
    tap_wait(*c); wait(r'^Lineup$|Ranking', 10)
    r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'arena.py'), acct],
                       capture_output=True, text=True)
    print('    tickets-full popup: Confirm -> arena.py:', (r.stdout.strip().splitlines() or ['?'])[-1], flush=True)
    if r.returncode: raise Stop('MATCH_FULL: arena.py failed (screenshot v_arena.png)')
    for _ in range(3):                                   # Arena -> main (back can land on Recruit: back again)
        tap_wait(92, 1810); time.sleep(1)
        if near(grab().getpixel((92, 1788)), (0, 158, 230)): return True
    raise Stop('MATCH_FULL: arena tickets spent but not back on the main screen')


def wait(pattern, timeout=10, region=(0, 0, 1080, 1920)):
    """Poll until a box matches; returns the boxes. Stop on timeout."""
    t0 = time.time()
    while True:
        boxes = ocr()
        if find(boxes, pattern, region): return boxes
        if tickets_full(boxes): raise Stop('MATCH_FULL: arena tickets spent, redo this step')
        if time.time() - t0 > timeout: raise Stop(f'waited {timeout}s for {pattern!r}; screen: {joined(boxes)[:200]}')
        time.sleep(0.7)


def tap_text(pattern, region=(0, 0, 1080, 1920), boxes=None, settle=True):
    p = find(boxes or ocr(), pattern, region)
    if not p: raise Stop(f'no button {pattern!r} on screen')
    tap_wait(*p) if settle else tap(*p)
    return p


def battle(start_screen, timeout=180, setup=None):
    """Challenge (bottom) -> lineup Start -> result -> close -> back on start_screen. Never 'Challenge again'.
    setup() runs on the lineup screen before Start. Returns the result screen's text."""
    tap_text(r'^Challenge$', (0, 1600, 1080, 1920))
    boxes = wait(r'^Start$', 10)
    if setup: setup(); boxes = wait(r'^Start$', 10)
    if not find(boxes, r'^Start$', (0, 1650, 1080, 1920)): raise Stop('Start not at the bottom of the lineup screen')
    tap_text(r'^Start$', (0, 1650, 1080, 1920), boxes)
    res = joined(wait(r'Tap anywhere to close', timeout))
    t0 = time.time()
    while time.time() - t0 < 15:
        boxes = ocr()
        if find(boxes, start_screen): return res
        c = find(boxes, r'^Confirm$')
        # Confirm, or 'Tap anywhere' at the TOP: (540,1700) below "Challenge again" started the next Tower floor on a
        # Victory (Bino/Chien Than/Dino 2026-11-01: a new fight was running when the close loop gave up)
        tap(*(c or (540, 120))); time.sleep(1.5)
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


def find_img(path, region=(0, 1150, 1080, 1590), im=None):
    """Template match (gray, 1/4 scale) of a png crop inside region -> (x, y, diff): device center of the best spot and
    its mean abs gray diff (0 = identical; Bone Archer card ~<15, other cards ~40+)."""
    import numpy as np
    from PIL import Image
    g = np.asarray((im or grab()).crop(region).convert('L').reduce(4), dtype=np.float32)
    t = np.asarray(Image.open(path).convert('L').reduce(4), dtype=np.float32)
    d = np.abs(np.lib.stride_tricks.sliding_window_view(g, t.shape) - t).mean(axis=(2, 3))
    y, x = np.unravel_index(d.argmin(), d.shape)
    return region[0] + 4 * x + 2 * t.shape[1], region[1] + 4 * y + 2 * t.shape[0], round(float(d.min()), 1)


def one_hero():
    """Battle setup: exactly 1 hero deployed? Idle animation over ~1 s: motion in our back slot (x<140), none in slots
    2-5 (x 180-500). Measured xFaktor 3-35 (archer alone): 0-140 ~13k moving px, 180-500 0; enemy 5 heroes span ~500 px.
    ponytail: a moving background in slots 2-5 reads as "more heroes" -> lone_hero() just redoes the lineup (safe)."""
    import numpy as np
    fr = []
    for _ in range(6): fr.append(np.asarray(grab().convert('L'), dtype=float)[700:1010, 0:540]); time.sleep(0.2)
    cols = (np.max([abs(a - fr[0]) for a in fr[1:]], axis=0) > 25).sum(axis=0)
    return cols[:140].sum() > 1000 and cols[180:500].sum() < 300


def lone_hero(tabs=False):
    """Battle setup (Tower, Stage tab 1) -> Bone Archer alone (Nick 2026-11-02: fast daily fights; never set back).
    Recall all, archer filter, find its card by template (an undeployed card scores ~10, others ~50), tap it, filter
    back to all (climb.py reads the all-heroes grid), check our power isn't 0."""
    if tabs: tap_wait(380, 1088)                         # Stage: tab 1
    if one_hero(): return                                 # any 1 hero already set: keep it (Nick 2026-11-04)
    tap_wait(1006, 1082); tap_wait(670, 1644)            # recall all, archer filter
    for _ in range(8):
        x, y, d = find_img(os.path.join(HERE, 'bone_archer.png'))
        if d < 25: break
        swipe(540, 1500, 540, 1300, 800); time.sleep(1)
    else: raise Stop('Bone Archer card not found in the archer grid (deployed on another tab = padlock?)')
    tap_wait(x, y); tap_wait(270, 1644)
    wait(r'[1-9]\d*K', 4, (0, 0, 540, 140))
