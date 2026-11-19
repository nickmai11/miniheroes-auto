// Tile running MuMu instance windows on the main screen. Layout 1 (default): each 1/2 of the usable height,
// `right` instances at full height against the screen's right edge, then 2 rows (accounts/layout.yaml `top`/`bottom`) to their left - fixed slots per listed name, running or not (Nick 2026-11-19); skipping names in accounts/layout.yaml `exclude`.
// usage: [LAYOUT=dynamic|2|ct] osascript -l JavaScript scripts/layout.js   (default = layout 1: 2 rows + right column, pinned slots — Nick, 2026-11-13/19; LAYOUT=dynamic = layout 1 packed from the running instances only (Nick 2026-11-19); LAYOUT=2 = one row, all evenly wide; LAYOUT=ct = 1 row, every running instance 1/10 of the screen width)
// Needs Accessibility permission for the terminal app (System Settings > Privacy & Security > Accessibility).
ObjC.import('AppKit')
const app = Application.currentApplication(); app.includeStandardAdditions = true
const dir = app.doShellScript('dirname "$(dirname ' + JSON.stringify($.NSProcessInfo.processInfo.arguments.js.map(a => a.js).pop()) + ')"')
const list = k => ((app.doShellScript(`grep '^${k}:' "${dir}/accounts/layout.yaml" || true`).match(/\[(.*)\]/) || [, ''])[1]).split(',').map(s => s.trim()).filter(Boolean)
const L = $.NSProcessInfo.processInfo.environment.objectForKey('LAYOUT').js || '1'   // default layout 1 (Nick 2026-11-13: every task; was layout 2 since 11-07)
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

const se = Application('System Events')
let x = v.origin.x
const place = (r, y, wh, edge) => {
  // right after boot.sh, the first ask returns 0 windows for every instance; a few s later all are there
  // (Poseidon + stabilize 2026-11-17) -> poll up to 15 s instead of giving up
  let p
  for (let t = 0; t < 30; t++) { p = se.processes.whose({ unixId: r.pid }); if (p.length && p[0].windows.length) break; delay(0.5) }
  if (!p.length || !p[0].windows.length) { console.log(`${r.name}: no window`); return 0 }
  const w = p[0].windows[0]
  w.position = [x, y]   // move first: a bottom-row window grown in place ran off-screen and macOS clamped its size (LAYOUT=2 first try)
  w.size = [Math.round(wh * 9 / 16), wh]   // MuMu may snap width to its aspect; we read it back below
  if (edge) w.position = [edge - w.size()[0], y]   // flush against `edge` once the snapped width is known
  console.log(`${r.name}: ${w.position()} ${w.size()}`)
  return w.size()[0]
}
// Layout 2 (LAYOUT=2; the default 2026-11-07..11-13): all instances in 1 row, each 1/n of the usable width
if (L !== '1' && L !== 'dynamic') {
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
}
// Layout 1 = fixed slots (Nick 2026-11-19: "remember or calculate the position based on the accounts predefined", was
// packed from whatever ran): every layout.yaml `right` / `top` / `bottom` name owns its slot, running or not, so a
// stopped instance leaves a gap instead of shifting the others. Unlisted running instances go left of the shorter row.
// MuMu keeps the height we set and snaps the width to 9:16 of the area under its title bar -> width(h) = (h - bar) * 9/16,
// bar measured once on the first window we move.
// LAYOUT=dynamic (Nick 2026-11-19, "layout dynamic"): same shape, but only running instances get a slot, packed right-aligned.
else if (insts.length) {
  if (L === 'dynamic') { const on = n => running.some(r => r.name === n); rows.forEach((r, i) => { rows[i] = r.filter(on) }); right.splice(0, right.length, ...right.filter(on)) }
  const H = v.size.height
  x = v.origin.x
  const bar = H - place(insts[0], top, H) * 16 / 9
  const W = hh => Math.ceil((hh - bar) * 9 / 16), Wr = W(H), Wh = W(h)   // ceil: round() gave 374 for a 375 window -> 1 px overlaps
  let edge = v.origin.x + v.size.width
  right.slice().reverse().forEach(n => { const r = insts.find(q => q.name === n); if (r) { x = edge - Wr; place(r, top, H, edge) } edge -= Wr })
  const listed = [...rows.flat(), ...right]
  running.filter(r => !listed.includes(r.name)).forEach(r => rows[rows[0].length > rows[1].length ? 1 : 0].unshift(r.name))
  rows.forEach((row, i) => row.forEach((n, j) => {
    const r = insts.find(q => q.name === n), slotEdge = edge - (row.length - 1 - j) * Wh   // columns counted from the row's end
    if (r) { x = slotEdge - Wh; place(r, top + i * h, h, slotEdge) }
  }))
}
undefined   // osascript prints the last value otherwise
