#!/usr/bin/env bash
# deploy.sh - deploy the SentinelBreach box from scratch on an Ubuntu 22.04 host.
#
# Steps (each can be skipped with the SKIP_* variables below):
#   1. preflight checks (docker, compose, ports free)
#   2. optional host firewall (default-deny + the Table 15 ports)   APPLY_FIREWALL=1
#   3. CTFd platform stack (platform/docker-compose.yml)
#   4. CH1 live container
#   5. CH6 Part B live container
#   6. smoke tests
#
# Usage: sudo ./scripts/deploy.sh            (firewall step needs root)
#        SKIP_PLATFORM=1 ./scripts/deploy.sh (deploy only the challenge containers)
#
# Secrets go in <repo>/.env (gitignored): CH6_PLAYER_PASSWORD, CH6_FLAG
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

APPLY_FIREWALL="${APPLY_FIREWALL:-0}"
SKIP_PLATFORM="${SKIP_PLATFORM:-0}"
PLAYER_NET="${PLAYER_NET:-10.20.0.0/24}"      # Player/VPN zone (Table 14)
PLATFORM_DIR="${PLATFORM_DIR:-$ROOT/platform}"

start=$SECONDS
log "=== SentinelBreach deployment starting ==="

# ---- 1. preflight -----------------------------------------------------------
need docker; need curl
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 plugin is required"
docker info >/dev/null 2>&1 || die "Docker daemon not reachable (is it running / are you in the docker group?)"
: "${CH6_PLAYER_PASSWORD:?Set CH6_PLAYER_PASSWORD in .env (must equal the Part A credential)}"
: "${CH6_FLAG:?Set CH6_FLAG in .env}"

for p in 8080 2222; do
  if ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":$p\$"; then
    log "Port $p already in use - assuming a previous deployment (it will be recreated)"
  fi
done
log "Preflight OK: $(docker --version)"

# ---- 2. host firewall (optional) -------------------------------------------
if [[ "$APPLY_FIREWALL" == "1" ]]; then
  (( EUID == 0 )) || die "APPLY_FIREWALL=1 needs root (run with sudo)"
  need ufw; need iptables
  log "Applying default-deny host firewall (Table 15 ports)"
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow 80/tcp   comment 'Nginx redirect'
  ufw allow 443/tcp  comment 'CTFd portal (TLS)'
  ufw allow 51820/udp comment 'WireGuard'
  # Management SSH (22) only from the management zone
  ufw allow from 10.10.0.0/24 to any port 22 proto tcp comment 'Mgmt SSH'
  ufw --force enable

  # Docker-published ports bypass ufw, so restrict them in DOCKER-USER:
  # CH1 (8080) and CH6-B (2222) reachable only from the Player/VPN zone.
  for p in 8080 2222; do
    iptables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport "$p" --ctdir ORIGINAL ! -s "$PLAYER_NET" -j DROP 2>/dev/null \
      || iptables -I DOCKER-USER -p tcp -m conntrack --ctorigdstport "$p" --ctdir ORIGINAL ! -s "$PLAYER_NET" -j DROP
  done
  log "Firewall applied (note: iptables rules are not persistent across reboot - use iptables-persistent if needed)"
else
  log "Skipping firewall (set APPLY_FIREWALL=1 with sudo to apply)"
fi

# ---- 3. CTFd platform -------------------------------------------------------
if [[ "$SKIP_PLATFORM" != "1" ]]; then
  if [[ -f "$PLATFORM_DIR/docker-compose.yml" ]]; then
    log "Starting CTFd platform from $PLATFORM_DIR"
    (cd "$PLATFORM_DIR" && docker compose up -d)
    log "Waiting for CTFd..."
    wait_for_http "http://127.0.0.1:8000/" 120 || log "WARNING: CTFd did not answer on 127.0.0.1:8000 within 120s"
  else
    log "No $PLATFORM_DIR/docker-compose.yml found - skipping CTFd (set PLATFORM_DIR or SKIP_PLATFORM=1)"
  fi
fi

# ---- 4 & 5. live challenge containers --------------------------------------
"$SCRIPT_DIR/reset_ch1.sh"
"$SCRIPT_DIR/reset_ch6b.sh"

# ---- 6. smoke tests ---------------------------------------------------------
log "=== Smoke tests ==="
curl -fsS http://localhost:8080/robots.txt | grep -qi 'Disallow' \
  && log "CH1: robots.txt reachable and discloses a Disallow entry -> PASS" \
  || die "CH1 smoke test failed"
wait_for_tcp 127.0.0.1 2222 5 \
  && log "CH6-B: SSH listening on :2222 -> PASS" \
  || die "CH6 Part B smoke test failed"

# Isolation spot-check: challenge containers must have no outbound internet (NT-03)
for c in $(docker ps --format '{{.Names}}' | grep -Ei 'ch1|ch6' || true); do
  if docker exec "$c" sh -c 'timeout 3 wget -q -O- http://1.1.1.1 >/dev/null 2>&1 || timeout 3 curl -s http://1.1.1.1 >/dev/null 2>&1'; then
    log "NT-03 WARNING: $c has outbound internet access"
  else
    log "NT-03: $c has no outbound access -> PASS"
  fi
done

log "=== Deployment finished in $((SECONDS - start))s ==="
