#!/usr/bin/env bash
# reset_all.sh - return the whole box to its initial state.
#   - live stages (CH1, CH6 Part B): destroyed and recreated from golden images
#   - static stages (CH2, CH3, CH4, CH5, CH6 Part A): master files are verified
#     against a SHA-256 manifest so a tampered master is detected
#
# Usage: ./scripts/reset_all.sh [--verify-only]
#   --verify-only   only check static master files, don't touch containers
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

VERIFY_ONLY=0
[[ "${1:-}" == "--verify-only" ]] && VERIFY_ONLY=1

total_start=$SECONDS
failed=0

if (( ! VERIFY_ONLY )); then
  log "=== Resetting live stages ==="
  "$SCRIPT_DIR/reset_ch1.sh"  || { log "CH1 reset FAILED";        failed=1; }
  "$SCRIPT_DIR/reset_ch6b.sh" || { log "CH6 Part B reset FAILED"; failed=1; }
fi

log "=== Verifying static master files ==="
# Manifest format: output of  sha256sum <files>  run from the repo root.
# Create it once the masters are final:
#   sha256sum ch2/suspicious_image.png ch3/message.enc ch3/note.txt \
#             ch4/starting_clue.txt ch5/capture.pcapng ch6/partA/lock > static.sha256
MANIFEST="${MANIFEST:-$ROOT/static.sha256}"
if [[ -f "$MANIFEST" ]]; then
  if (cd "$ROOT" && sha256sum -c "$MANIFEST" 2>&1 | tee -a "$LOG_FILE"); then
    log "Static masters verified OK"
  else
    log "Static master verification FAILED - restore from backup / regenerate"
    failed=1
  fi
else
  log "No manifest at $MANIFEST - skipping static check (see comment in this script to create one)"
fi

log "reset_all finished in $((SECONDS - total_start))s"
(( failed == 0 )) || die "one or more reset steps failed - see $LOG_FILE"
log "Whole box is back in its initial state"
