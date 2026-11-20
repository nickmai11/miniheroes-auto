# Environment setup

## MuMuPlayer (macOS)

- One MuMu Android instance per game account; `mumu-cli info all` lists them with index and ADB port (not every
  instance is a game account — `accounts/` is the list).
- Instance list window: app **MuMuPlayer**. Each row has a ▶ (start) / ⏻ (stop) button and ⋮
  (settings). The game window for a running instance belongs to app **MuMu Android Device**
  and is titled with the instance name (e.g. `Cmajor`), ~704×1289 px.
- Game: **Mini Heroes: Magic Throne**, icon on the Android home screen (top row, middle).
- Instance settings (⋮ → Settings, or menu _MuMu Android Device → Settings for "<name>"_):
  - _Developer_ tab: Root Access, System Disk Mode (Readonly/Writable), ADB default port.
  - Menu _Developer → Open ADB (<port>)_ shows the instance's ADB port.
- Display: every instance is 1080×1920, 360 dpi (`mumu-cli config <i> --setting '{"resolutionWidthHeight":"1080x1920","resolutionDPI":360}'`,
  applies on restart). Chien Than, Cris, PuPu and pawn1 were 600×1080 with an `adb shell wm size 1080x1920` override
  (windows ~7 px narrower) until 2026-11-06 (Nick: all instances same config). A restart can move the ADB port by 1
  (26752 → 26753): always read it from `mumu-cli info`.
- Frame rate: the rule is CLAUDE.md "FPS" (skill `fps` sets it). `maxFpsLimit` applies live; any cap below 30 is ignored (10–25 tried on Bino 2026-11-17, game stays at 30). 30 measured on Dminor:
  idle CPU 28% → 21%, boot and an Arena step no slower; 11 idle on main: 30 fps ~145% vs 60 fps ~230% total.
- CPU: **1 vCPU per instance** (Nick 2026-11-17, `vmCpuCount`, applies at instance start; `boot.sh` sets it). Catch-up
  on 11 at once (2026-11-17): MuMu ~10% less CPU at work (612% → 552%), boot 414% → 279% in the same ~2.4 min, all 11
  booted. Earlier single-instance tries: Dminor 11-12 boot 28 → 53 s, Bino 11-17 19:55 boot-timeout.

- Same config on every instance (Nick, 2026-11-06): root off, system disk read-only, no Wi-Fi proxy.

## Traffic capture — removed 2026-11-06

The game API is encrypted with a per-request nonce (`docs/api-findings.md`), so capture was dropped after one look
(2026-10-26). The Proxyman setup (Cmajor proxy, root, writable disk, system CA) is in git history before this change
(`git show b903e74:docs/setup.md`).

## Launcher list order

The MuMuPlayer launcher's instance order = `mumu:` in `accounts/layout.yaml` (Nick, 2026-11-13). MuMu stores it in
`setting/common.json` → `managerListIndexs` (`<instance index>-<position>`), read at launcher start; no `mumu-cli`
command. Restore it with `scripts/mumu_order.py` (skill `mumu-order`), then restart the launcher (it closes running
instances — not while one is in use).
