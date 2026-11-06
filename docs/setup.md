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
- Display: most instances are 1080×1920 (9:16). **Chien Than and xFaktor** are 600×1080 with an `adb shell wm size
1080x1920` override, so scripts still get 1080×1920 coords, but their windows keep the 600:1080 ratio, about 7 px
  narrower at full height (layout 2, 2026-11-06). Right after boot a screenshot can still come back at 600×1080 (`tap.py`).

| Instance | ADB port                                     | Root | System disk | Wi-Fi proxy               | Proxyman CA                           |
| -------- | -------------------------------------------- | ---- | ----------- | ------------------------- | ------------------------------------- |
| Cmajor   | 26625 (was 26624; check `mumu-cli info all`) | on   | Writable    | 192.168.1.2:9090 (manual) | installed as system cert `d69f971d.0` |

> Cmajor's Wi-Fi proxy points at Proxyman on Nick's Mac. If Proxyman isn't running, the game
> on Cmajor loses connectivity — set the proxy back to _None_ (Settings → Network & internet →
> Internet → ⚙ on the Wi-Fi → ✎ → Advanced options → Proxy) when not capturing.
> A MuMuPlayer update resets the Writable system disk (and the installed cert).

## Traffic capture (optional — only needed for API investigation)

1. Proxyman listens on `192.168.1.2:9090` (Nick's Mac LAN IP; check Proxyman's title bar).
2. In the instance: Wi-Fi → Advanced → Proxy _Manual_, host `192.168.1.2`, port `9090`.
3. SSL proxying enabled in Proxyman for: `us-su-bldld.maxngame.com`, `us-cdn-bldld.maxngame.com`,
   `heart.maxngame.com`, `api.mgamestore.com`, `passport.mgamestore.com`.
4. Install the Proxyman CA as a system cert (needs Root + Writable system disk, then restart):

```bash
# export first: Proxyman → Certificate → Export → Root Certificate as PEM → ~/Desktop/proxyman.pem
cd ~/Desktop && ADB=$(command -v adb || find /Applications/MuMu*.app -type f -name adb 2>/dev/null | head -1) \
 && D=127.0.0.1:<adb-port> && "$ADB" connect $D \
 && h=$(openssl x509 -inform PEM -subject_hash_old -in proxyman.pem | head -1) && cp proxyman.pem $h.0 \
 && "$ADB" -s $D push $h.0 /sdcard/ \
 && "$ADB" -s $D shell "su -c 'mount -o rw,remount / ; mount -o rw,remount /system ; cp /sdcard/$h.0 /system/etc/security/cacerts/ && chmod 644 /system/etc/security/cacerts/$h.0'"
```

Proxyman's "Android Emulator" auto-setup guide does **not** detect MuMu — use the manual steps.
