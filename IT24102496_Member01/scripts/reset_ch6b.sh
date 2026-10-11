#!/usr/bin/env bash
# reset_ch6b.sh - destroy and recreate the CH6 Part B (Linux/sudo) container
# from its golden image. Design target: < 30 s (RT-01).
#
# Needs the same secrets as ch6/partB/build.sh. Put them in <repo>/.env (gitignored):
#   CH6_PLAYER_PASSWORD=...   (must equal the credential recovered in Part A)
#   CH6_FLAG=SBB{...}
# or export them in your shell before running.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

need docker
: "${CH6_PLAYER_PASSWORD:?Set CH6_PLAYER_PASSWORD (in .env or the environment)}"
: "${CH6_FLAG:?Set CH6_FLAG (in .env or the environment)}"
export CH6_PLAYER_PASSWORD CH6_FLAG

CH6B_DIR="${CH6B_DIR:-$(find_dir partB docker-compose.yml)}" || die "ch6/partB not found (set CH6B_DIR)"
[[ -f "$CH6B_DIR/docker-compose.yml" ]] || die "ch6/partB/docker-compose.yml not found (set CH6B_DIR)"

log "Resetting CH6 Part B in $CH6B_DIR"
start=$SECONDS

cd "$CH6B_DIR"
docker compose down -v --remove-orphans
./build.sh                                   # the group's own build/run script

# Health check: SSH banner must appear on host port 2222
wait_for_tcp 127.0.0.1 2222 60 || die "CH6 Part B SSH did not come up on :2222"

report_time "CH6-PartB" $((SECONDS - start))
log "CH6 Part B reset complete: ssh -p 2222 player@<host>"
