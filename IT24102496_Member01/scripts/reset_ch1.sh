#!/usr/bin/env bash
# reset_ch1.sh - destroy and recreate the CH1 (The Forgotten Endpoint) container stack
# from its pinned image/compose definition. Design target: < 30 s (RT-01).
#
# Usage: ./scripts/reset_ch1.sh
# Override location with CH1_DIR=/path/to/ch1 if auto-detection fails.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

need docker; need curl
CH1_DIR="${CH1_DIR:-$(find_dir ch1 docker-compose.yml)}" || die "ch1/docker-compose.yml not found (set CH1_DIR)"

log "Resetting CH1 in $CH1_DIR"
start=$SECONDS

cd "$CH1_DIR"
docker compose down -v --remove-orphans      # -v wipes the DB volume => clean initial state
docker compose up --build -d

# Health check: the portal must serve robots.txt (the intended disclosure vector)
wait_for_http "http://localhost:8080/robots.txt" 60 || die "CH1 did not become healthy on :8080"

report_time "CH1" $((SECONDS - start))
log "CH1 reset complete: http://localhost:8080/"
