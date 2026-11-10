// Tile running MuMu instance windows on the main screen. Layout 1 (LAYOUT=1): each 1/2 of the usable height,
// packed in 2 rows from the left edge (accounts/layout.yaml `top`/`bottom`), then `right` instances at full height; skipping names in accounts/layout.yaml `exclude`.
// usage: [LAYOUT=1|ct] osascript -l JavaScript scripts/layout.js   (default = layout 2: one row, all evenly wide — Nick, 2026-11-07; LAYOUT=1 = 2 rows + right column; LAYOUT=ct = 1 row, every running instance 1/10 of the screen width)
// Needs Accessibility permission for the terminal app (System Settings > Privacy & Security > Accessibility).
ObjC.import('AppKit')
const app = Application.currentApplication(); app.includeStandardAdditions = true
const dir = app.doShellScript('dirname "$(dirname ' + JSON.stringify($.NSProcessInfo.processInfo.arguments.js.map(a => a.js).pop()) + ')"')
const list = k => ((app.doShellScript(`grep '^${k}:' "${dir}/accounts/layout.yaml" || true`).match(/\[(.*)\]/) || [, ''])[1]).split(',').map(s => s.trim()).filter(Boolean)
const L = $.NSProcessInfo.processInfo.environment.objectForKey('LAYOUT').js || ''
const exclude = list('exclude'), rows = [list('top'), list('bottom')], right = list('right')
const info = JSON.parse(app.doShellScript('"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" info all'))
// ONLY="0 2 4" (set by boot.sh) = tile just these MuMu indices — booting 8 accounts once moved Aminor's window too
const only = ($.NSProcessInfo.processInfo.environment.objectForKey('ONLY').js || '').split(' ').filter(Boolean).map(Number)
const mine = r => !only.length || only.includes(Number(r.index))
const running = info.return.results.filter(r => r.state === 'running' && r.pid && !exclude.includes(r.name)).sort((a, b) => a.index - b.index)
const insts = running.filter(mine)

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
  w.position = [x, y]   // move first: a bottom-row window grown in place ran off-screen and macOS clamped its size (LAYOUT=2 first try)
  w.size = [Math.round(wh * 9 / 16), wh]   // MuMu may snap width to its aspect; we read it back below
  console.log(`${r.name}: ${w.position()} ${w.size()}`)
  return w.size()[0]
}
// Layout 2 (default since 2026-11-07, Nick: every task): all instances in 1 row, each 1/n of the usable width; LAYOUT=1 = the old 2-row layout
if (L !== '1') {
  // One slot per layout.yaml `row` name, running or not (Nick 2026-11-07: an account keeps its place and width whatever
  // is open); unlisted running instances get extra slots after it, by MuMu index. ONLY (boot.sh) just limits which
  // windows move (a 6-of-9 boot gave the 6 1/6 width each, on top of the other 3 - 2026-11-07).
  // LAYOUT=ct (Crystal Throne, Nick 2026-11-08): running instances only, no empty slots, each exactly 1/10 of the screen width
  const order = list('row'), all = L === 'ct' ? [] : order.map(n => running.find(r => r.name === n) || null)
  running.sort((a, b) => (order.indexOf(a.name) + 1 || 99) - (order.indexOf(b.name) + 1 || 99)).forEach(r => { if (!all.includes(r)) all.push(r) })
  // MuMu snaps the window to its own w/h ratio (title bar included, ~547x1010 for a 569 target) -> size the first
  // window we move, read its real ratio back, then height = (width / n) / ratio so the row fills the screen width
  const cw = v.size.width / (L === 'ct' ? 10 : all.length)
  let wh = Math.min(v.size.height, Math.floor(cw * 16 / 9))
  const i0 = all.findIndex(r => r && mine(r))
  if (i0 >= 0) { x += i0 * cw; const w0 = place(all[i0], top, wh); wh = Math.min(v.size.height, Math.floor(cw * wh / w0)); x = v.origin.x }
  let ww = cw                                            // a skipped slot = the width of the windows we placed
  all.forEach(r => { if (r && mine(r)) ww = place(r, top, wh); x += ww })
  grid.length = 0; right.length = 0
}
for (let c = 0; grid.length && c < Math.max(grid[0].length, grid[1].length); c++) {
  let colW = 0
  grid.forEach((row, i) => { if (row[c]) colW = Math.max(colW, place(row[c], top + i * h, h)) })
  x += colW
}
// layout.yaml `right`: full usable height, after the grid
right.map(n => insts.find(r => r.name === n)).filter(Boolean).forEach(r => { x += place(r, top, v.size.height) })
undefined   // osascript prints the last value otherwise
