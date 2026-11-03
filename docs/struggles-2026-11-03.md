# Struggles — dailies 2026-11-03 (game day 2026-11-03, 9 accounts)

Source: runner logs `/tmp/miniheroes-2026-11-03/*.log`, helper answers in `logs/<account>/2026-11-03.log`.
Ordered by impact. Status: ✅ fixed · 🧪 fixed, waiting for a live test (`docs/untested.md`) · 🟡 partly (something still open) · ❌ open · ❓ needs Nick. Kong is out of scope for this review (Nick). Untested fixes are tracked in
`docs/untested.md` (tested on one account in the dailies Pre-flight). Last updated: 2026-11-03 20:05 (catch-up: Pet Arena restart + dropdown change passed live).

| #   | Task                     | What went wrong                                   | Status       |
| --- | ------------------------ | ------------------------------------------------- | ------------ |
| 1   | Pet Arena (8 accounts)   | Failed everywhere; ran last instead of first      | 🧪           |
| 2   | Hero (6 FAILs)           | Card not found, mid-animation reads               | 🧪           |
| 3   | Rune (Bino ×2, Tiger ×1) | Taps from a still-scrolling list hit locked tiles | 🧪           |
| 4   | Grocery Realm tile 4     | Skipped 24× since late Oct — never bought         | ✅           |
| 5   | Chien Than daily 150/160 | Tower chest level skipped → Tower row missing     | ✅           |
| 6   | Tiger Stage              | Bone Archer locked on team 2                      | ❌           |
| 8   | Dminor Events            | False MANUAL → out-of-scope "Again" tap           | ❌           |
| 9   | Storm lock wait          | Cmajor idle 246 s                                 | ❌           |
| 10  | Sanctuary (Dino)         | No floor popup once                               | ✅ transient |
| 11  | Boot (Aminor)            | Game never launched, 90 s wait                    | ✅           |
| 12  | Events (all accounts)    | Golden Woods + Pet Free Pack never collected      | ✅           |
| 13  | Coordination             | Slow feedback, piecemeal fixes, helper mis-taps   | 🟡           |

Not struggles: Tower 3/3 and Stage 3/3 Defeat (by design — Bone Archer alone); Grocery "price > balance" skips.

---

## 1. Pet Arena — 🧪

- Runner FAIL on every account (14 FAIL lines); pets done by helpers ~40 min after the run started.
- Causes (traced / probed live):
  - Hub tab: the red dot hides "Pet" from OCR → only "Arena" reads.
  - Arena decided "full" while it was open: the "X has deployed Y" ticker hides the "Auto Deploy" label; the
    script required that label.
  - Back from the pet pool goes straight to Join; only a fight asks "Exit this match?" — script always waited for it.
  - Re-tapping Join while the arena loads lands on the pool's big **Deploy** button (manual deploy panel).
  - A fight can start between Join and the Auto Deploy tap → dialog never opens.
  - Lone digit "4" missed by OCR on frames read while the dialog was still animating.
  - Top-left ticket counter ≠ free attempts (Aminor read 0 and could still Start).
- Nick's notes (2026-11-03): defaults 4 / High to Low — don't open a dropdown if it already shows the expected
  value; no free attempts = done; be fast after the reset; exit a fight right away.
- Done: `pet_arena` rewritten (`pet_state`, `pet_dialog`, `pet_back`, `pet_sprites`); passes on all 8 in 18–28 s.
- **Passed live (catch-up 2026-11-03 20:03):** Chien Than `pet_check` at +38/40 restarted Auto Deploy with a dropdown
  change (`changed: sprites 2, Random Selection`, matches its config); re-check a minute later: +40.
- **Open:** the busy arena after the reset → `docs/untested.md`, first real test at the next reset (Wed).

## 2. Hero — 🧪

Proven live: finding Bone Archer by avatar (4 accounts), level-read polls (Cmajor Lv.90→105 over 3 runs), gear popup
opened once + Enhance ×5 (Nick). `hero` on Cmajor: 51 s. Waiting for a live test: `rebirth_90`. Gear level read-back
dropped (levels don't matter).
Extra / missing hero or gear levels are not a concern — Bone Archer is only for the dailies (Nick, 2026-11-03);
the per-day level cap was removed again.

| Account      | Failure                                                         | Cause                                                 | Status                                                                           |
| ------------ | --------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------- |
| xFaktor      | "'Bone Archer' not among the last 6 cards" ×2                   | Located cards by "Lv.N" labels; "Lv.97" not OCR'd     | ✅ now by avatar: expanded list → Marksman → bottom → face template (Nick's way) |
| Aminor, Dino | "hero level / Level Up not readable"                            | Single OCR read mid-animation (Aminor after 4 levels) | ✅ polls (Cmajor Lv.90→105 live)                                                 |
| Dino, Tiger  | gear "LV 6 -> None", "None -> 8"; Tiger "None -> 1" (gear at 0) | Gear badge read flaky                                 | ✅ read-back dropped; popup opened once, Enhance ×5 (Nick)                       |

- First avatar version scrolled the strip and took 79 s per account: "wait until still" needed identical frames,
  but the list keeps animating (card shine, red dots) → now <2% changed pixels = still.

**New rule — out of potions → Rebirth + quick Lv.90** (Nick, 2026-11-03):

- Done by hand on Cmajor (Nick: "Rebirth, Lv90 only"): Bone Archer Lv.96 → Rebirth (free, 100% of hero **and gear**
  materials back; gear reset to 0) → Lv.1 → Level Up → ↑ Lv.90 → Quick Level Up (1328k potions) → **Lv.90**, gear LV.0.
- Scripted: `hero.py` `rebirth_90` — only when the level didn't move AND potions have < need AND the hero is > Lv.90
  (a stuck level with enough potions does NOT trigger it). Script path never ran → `docs/untested.md`. Doc: ui-routine Hero section.

**Speed-ups from this review (Nick, 2026-11-03):** Stage — on Defeat tap "Challenge again" and Start again until the
target instead of close + re-open per fight (Cmajor 38 s for 3, was ~52 s).

## 3. Rune — 🧪

- Bino: "no unlocked red rune (25 red tiles, 25 without lock)" ×2; Tiger: "(25 red tiles, 21 without lock)" ×1
  (retry OK). Nick: "misclicked too many times on the locked runes".
- Cause: the script scanned the list 1.2 s after a swipe while it was still coasting, then tapped where the tiles
  _had been_ → other tiles, incl. locked ones. The lock detector itself is right: Tiger's 4 still pages, 12/12
  padlocks found, no false ones. (Not the Synthesize search band — Bino's button is at y 1203, inside it.)
- Fix (`daily.py` `still`, `rune_tiles`, `rune_pick`): read only a still frame, skip padlocked tiles, tap the tile
  centre, find Synthesize anywhere in the popup; a "Locked" reply stops the step instead of trying more tiles.
- Live dry run (popup opened, nothing synthesized): Tiger and Bino each picked an unlocked Mythic rune on the first
  tap, 8–9 s. Untested: the swipe-to-next-page path (both found one on the first screen) → `docs/untested.md`.

## 4. Grocery Realm tile 4 — ✅

- `realm 4 SKIPPED: not priced in the shop coin` — **24 times** in the logs since late October; never bought.
- Live check on Dino: tile 4 = red stone ×1000 for 3000, paw coin like the rest of the Realm Shop.
- Cause: the coin colour was one small sample at a fixed offset `bx - 73`; it hit the icon's edge / paw (tile 4 green
  82 vs balance 118, tolerance 35). Even text-relative points varied 13–54 — the paw print inside the coin.
- Fix (`daily.py` `coin`): mean of the icon's coloured pixels left of the price text vs the same for the balance icon →
  all 12 Realm tiles within 2–4 of the balance. Live: Dino `realm 4 bought for 3000`.
- Still open (audit): tiles are picked by slot number from the config; the item itself isn't checked — a reordered
  shop would buy the wrong item.

## 5. Chien Than daily 150/160 — ✅

- Open rows: Upgrade Statue, Purchase with Diamonds in Grocery, Challenged the Tower.
- Nick: only **2** of the 18 rows aren't scriptable (Statue, Diamonds) — 16 rows = 160 exactly, so Tower had to be
  doable. It was: Tower stood on the Treasure Chest Level ("Claim Reward", no Challenge) and `adventure.py` SKIPped it.
- Fix (`adventure.py` `claim_tower`): Claim Reward (free) → next floors open with Challenge → fight on. Chien Than:
  Floor 2030 claimed, 3 challenges, **daily chests [160]**. Doc: Tower step 5 + the 18 rows → steps list in
  "Daily Mission". The script's claim path itself → `docs/untested.md` (the claim was tapped by hand before the run).

## 6. Tiger Stage — ❌

- "Bone Archer card not found in the archer grid (deployed on another tab = padlock?)" ×2.
- Helper: Bone Archer was on **team 2** → "Move hero to the current team?" Confirm, removed the other tab-1 hero.
  Team 2 no longer has Bone Archer.
- To do: script handles the padlock (move prompt) on any tab.

## 8. Dminor Events — ❌

- Runner line: `MANUAL 7777 daily, match_event x2, weekly free x1; red dots left: ['pet_arena']` — everything was
  claimed; MANUAL only because Pet Arena's own red dot counted as left over.
- I misread it as "7777 claim left" → helper tapped 7777's yellow **"Again"** (out of scope; NO_CHANGE).
- To do: events ignores tabs owned by other steps (pet_arena); make the claimed list vs MANUAL reason unambiguous.

## 9. Storm lock wait — ❌

- Cmajor `storm: waited 246s for s201` (one account per server block at a time).
- Idea: run another step while the block is busy and come back to Storm.

## 10. Sanctuary (Dino) — ✅ transient

- "no floor popup under the marker (156,828)" once; retry swept.

## 11. Boot (Aminor) — ✅

- Game sat on the Android home screen; boot waited its 90 s Start timeout.
- `boot.sh` now relaunches every 30 s, 3 tries.

## 12. Events not all collected — ✅

- Nick (evening): "you failed to collect everything, some are left".
- Golden Woods (new hub tab) was unknown to `events()` → its free claims (Exploration Quest keys, Sign-In, Expedition
  gift) were never touched and never reported. Pet Arena's Free Pack was in the doc but not in the script.
- Fixed: `golden_woods()`, Pet Free Pack, `close_reward()` (tap the "Tap anywhere to close" line — the popup centre
  is the reward icon), and unknown dotted hub tabs now report `MANUAL … unmapped tab <label>` (checked on 3 pre-claim
  screenshots). Collected on all 8 accounts; a verification pass on all 8: `nothing claimed`, no MANUAL.
- Side effect: my "look" tap on Tiger's Expedition gift icon claimed it (20 gems, free).

## 13. Coordination — 🟡

Still open: helpers mixing screenshot and device coords.

- Blocked on a long boot command while Aminor was stuck; Nick waited ("I don't like waiting").
- Failure monitor first version was noisy (tail headers).
- Pet Arena patched one failure at a time mid-run instead of understanding the flow first.
- Helpers mixed screenshot and device coords → many NO_CHANGE taps; a player profile opened twice (closed safely).
- Done: memory `fast-feedback`. Open: helper coord-scaling mistakes.
