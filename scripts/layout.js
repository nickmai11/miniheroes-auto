// Tile running MuMu instance windows on the main screen: each 1/2 of the usable height,
// packed in 2 rows from the left edge (index order), skipping names in accounts/layout.yaml `exclude`.
// usage: osascript -l JavaScript scripts/layout.js
// Needs Accessibility permission for the terminal app (System Settings > Privacy & Security > Accessibility).
ObjC.import('AppKit')
const app = Application.currentApplication(); app.includeStandardAdditions = true
const dir = app.doShellScript('dirname "$(dirname ' + JSON.stringify($.NSProcessInfo.processInfo.arguments.js.map(a => a.js).pop()) + ')"')
const cfg = app.doShellScript(`grep '^exclude:' "${dir}/accounts/layout.yaml" || true`)
const exclude = (cfg.match(/\[(.*)\]/) || [, ''])[1].split(',').map(s => s.trim()).filter(Boolean)
const info = JSON.parse(app.doShellScript('"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all'))
// ONLY="0 2 4" (set by boot.sh) = tile just these MuMu indices — booting 8 accounts once moved Aminor's window too
const only = ($.NSProcessInfo.processInfo.environment.objectForKey('ONLY').js || '').split(' ').filter(Boolean).map(Number)
const insts = info.return.results.filter(r => r.state === 'running' && r.pid && !exclude.includes(r.name) && (!only.length || only.includes(Number(r.index))))
  .sort((a, b) => a.index - b.index)

// main screen usable area, converted to top-left origin (AX coordinates)
const scr = $.NSScreen.screens.js[0], f = scr.frame, v = scr.visibleFrame
const top = f.size.height - v.origin.y - v.size.height, h = Math.floor(v.size.height / 2)

const se = Application('System Events')
let x = v.origin.x, colW = 0
insts.forEach((r, i) => {
  const p = se.processes.whose({ unixId: r.pid })
  if (!p.length || !p[0].windows.length) return console.log(`${r.name}: no window`)
  const w = p[0].windows[0]
  w.size = [Math.round(h * 9 / 16), h]   // MuMu may snap width to its aspect; we read it back below
  const [ww] = w.size()
  w.position = [x, top + (i % 2) * h]
  colW = Math.max(colW, ww)
  if (i % 2) { x += colW; colW = 0 }
  console.log(`${r.name}: ${w.position()} ${w.size()}`)
})
