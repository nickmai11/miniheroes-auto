# Kong II (S288 on Kong's instance; CLAUDE.md "Kong II"): sourced by the batch scripts.
# with_kong_ii <cmd...>: switch Kong's instance ($D) to Kong II, run <cmd> (a function or command), switch back to Kong.
# stabilize.py exit 0 = that account's ID read on screen; switch.txt in the current dir keeps both switch outputs.
with_kong_ii() {
  if ACCOUNT=kong_ii python3 "$HERE/stabilize.py" > switch.txt 2>&1; then "$@"
  else echo "kong_ii SKIPPED (switch: $(tail -1 switch.txt))"; fi
  ACCOUNT=kong python3 "$HERE/stabilize.py" >> switch.txt 2>&1 || echo "kong: switch back from Kong II failed ($(tail -1 switch.txt))"
}
