#!/usr/bin/env bash
# lib.sh - shared helpers for the SentinelBreach scripts (sourced, not run directly)

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${SB_ROOT:-$(dirname "$SCRIPT_DIR")}"

# Optional secrets/config file (keep it out of git: add .env to .gitignore)
if [[ -f "$ROOT/.env" ]]; then
  set -a; # shellcheck disable=SC1091
  source "$ROOT/.env"; set +a
fi

LOG_DIR="$ROOT/tests/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/ops.log"

log()  { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG_FILE"; }
die()  { log "ERROR: $*"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "'$1' is required but not installed"; }

# Find a challenge directory that contains a docker-compose.yml.
# Works with either layout: ch1/ or ch1-ch3-ch5/ch1/ (override with CH1_DIR / CH6B_DIR).
find_dir() {
  local name="$1" file="$2" c
  for c in "$ROOT/$name" "$ROOT"/*/"$name" "$ROOT"/*/*/"$name"; do
    [[ -f "$c/$file" ]] && { echo "$c"; return 0; }
  done
  return 1
}

# wait_for_http URL TIMEOUT_SECONDS
wait_for_http() {
  local url="$1" timeout="${2:-60}" i=0
  until curl -fsS -o /dev/null --max-time 2 "$url"; do
    ((i++ >= timeout)) && return 1
    sleep 1
  done
}

# wait_for_tcp HOST PORT TIMEOUT_SECONDS
wait_for_tcp() {
  local host="$1" port="$2" timeout="${3:-60}" i=0
  until (exec 3<>"/dev/tcp/$host/$port") 2>/dev/null; do
    ((i++ >= timeout)) && return 1
    sleep 1
  done
}

# The Assignment 01 design target is "under 30 seconds" (test RT-01)
RECOVERY_TARGET="${RECOVERY_TARGET:-30}"

report_time() {  # report_time LABEL SECONDS
  if (( $2 <= RECOVERY_TARGET )); then
    log "RT-01 $1: recovered in ${2}s (target <${RECOVERY_TARGET}s) -> PASS"
  else
    log "RT-01 $1: recovered in ${2}s (target <${RECOVERY_TARGET}s) -> OVER TARGET"
  fi
}
