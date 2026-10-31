// Tile running MuMu instance windows on the main screen: each 1/2 of the usable height,
// packed in 2 rows from the left edge (accounts/layout.yaml `top`/`bottom`), then `right` instances at full height; skipping names in accounts/layout.yaml `exclude`.
// usage: osascript -l JavaScript scripts/layout.js
// Needs Accessibility permission for the terminal app (System Settings > Privacy & Security > Accessibility).
ObjC.import('AppKit')
const app = Application.currentApplication(); app.includeStandardAdditions = true
const dir = app.doShellScript('dirname "$(dirname ' + JSON.stringify($.NSProcessInfo.processInfo.arguments.js.map(a => a.js).pop()) + ')"')
const list = k => ((app.doShellScript(`grep '^${k}:' "${dir}/accounts/layout.yaml" || true`).match(/\[(.*)\]/) || [, ''])[1]).split(',').map(s => s.trim()).filter(Boolean)
const exclude = list('exclude'), rows = [list('top'), list('bottom')], right = list('right')
const info = JSON.parse(app.doShellScript('"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all'))
// ONLY="0 2 4" (set by boot.sh) = tile just these MuMu indices — booting 8 accounts once moved Aminor's window too
const only = ($.NSProcessInfo.processInfo.environment.objectForKey('ONLY').js || '').split(' ').filter(Boolean).map(Number)
const insts = info.return.results.filter(r => r.state === 'running' && r.pid && !exclude.includes(r.name) && (!only.length || only.includes(Number(r.index))))
  .sort((a, b) => a.index - b.index)

// main screen usable area, converted to top-left origin (AX coordinates)
const scr = $.NSScreen.screens.js[0], f = scr.frame, v = scr.visibleFrame
const top = f.size.height - v.origin.y - v.size.height, h = Math.floor(v.size.height / 2)

// grid[row][col]: names from layout.yaml top/bottom rows; unlisted instances fill the shorter row, by index
const grid = rows.map(n => n.map(name => insts.find(r => r.name === name)).filter(Boolean))
insts.filter(r => !grid.flat().includes(r) && !right.includes(r.name)).forEach(r => grid[grid[0].length > grid[1].length ? 1 : 0].push(r))

const se = Application('System Events')
let x = v.origin.x
const place = (r, y, wh) => {
  const p = se.processes.whose({ unixId: r.pid })
  if (!p.length || !p[0].windows.length) { console.log(`${r.name}: no window`); return 0 }
  const w = p[0].windows[0]
  w.size = [Math.round(wh * 9 / 16), wh]   // MuMu may snap width to its aspect; we read it back below
  w.position = [x, y]
  console.log(`${r.name}: ${w.position()} ${w.size()}`)
  return w.size()[0]
}
for (let c = 0; c < Math.max(grid[0].length, grid[1].length); c++) {
  let colW = 0
  grid.forEach((row, i) => { if (row[c]) colW = Math.max(colW, place(row[c], top + i * h, h)) })
  x += colW
}
// layout.yaml `right`: full usable height, after the grid
right.map(n => insts.find(r => r.name === n)).filter(Boolean).forEach(r => { x += place(r, top, v.size.height) })
undefined   // osascript prints the last value otherwise
