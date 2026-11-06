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
  applies on restart). Chien Than, Cris, PuPu and xFaktor were 600×1080 with an `adb shell wm size 1080x1920` override
  (windows ~7 px narrower) until 2026-11-06 (Nick: all instances same config). A restart can move the ADB port by 1
  (26752 → 26753): always read it from `mumu-cli info`.

- Same config on every instance (Nick, 2026-11-06): root off, system disk read-only, no Wi-Fi proxy.

## Traffic capture — removed 2026-11-06

The game API is encrypted with a per-request nonce (`docs/api-findings.md`), so capture was dropped after one look
(2026-10-26). The Proxyman setup (Cmajor proxy, root, writable disk, system CA) is in git history before this change
(`git show b903e74:docs/setup.md`).
