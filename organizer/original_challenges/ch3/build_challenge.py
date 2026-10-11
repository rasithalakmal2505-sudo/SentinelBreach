#!/usr/bin/env python3
"""
CH3 - Cracked Seal :: organizer-only build script.

Produces the player-facing artefacts:
    message.enc   - 16-byte IV || AES-128-CBC ciphertext
    note.txt      - contextual note narrowing the timestamp window (player-facing)

Key derivation (per Section 10.3 of the report):
    key = SHA256(timestamp_string)[:16]
    timestamp_string = ISO-8601 UTC, e.g. "2026-03-14T09:41:00Z"

KEEP THIS FILE AND THE CHOSEN TIMESTAMP IN THE ORGANIZER-ONLY SOLUTION GUIDE.
Do not ship this script or the true timestamp to players.
"""

import hashlib
import secrets
import sys
from datetime import datetime, timedelta, timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

FLAG = "SBB{time_based_keys_are_not_random}"
PLAINTEXT = (
    "Internal Msg - NovaGrid Engineering\n"
    "-----------------------------------\n"
    "Rotated the service account creds after the anomaly on the portal.\n"
    "Incident ref attached below for the SOC writeup.\n\n"
    f"FLAG: {FLAG}\n"
).encode()

# The "shift window" the note will describe to players (20 minutes).
WINDOW_START = datetime(2026, 3, 14, 9, 30, 0, tzinfo=timezone.utc)
WINDOW_MINUTES = 20

# --- Pick the true timestamp somewhere inside that window (organizer secret) ---
if len(sys.argv) > 1:
    # allow: python3 build_challenge.py "2026-03-14T09:41:00Z"
    true_ts_str = sys.argv[1]
    true_ts = datetime.strptime(true_ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
else:
    offset_seconds = secrets.randbelow(WINDOW_MINUTES * 60)
    true_ts = WINDOW_START + timedelta(seconds=offset_seconds)
    true_ts_str = true_ts.strftime("%Y-%m-%dT%H:%M:%SZ")

key = hashlib.sha256(true_ts_str.encode()).digest()[:16]
iv = secrets.token_bytes(16)

cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(PLAINTEXT, AES.block_size))

with open("message.enc", "wb") as f:
    f.write(iv + ciphertext)

note = (
    "Recovered alongside the ciphertext - handwritten, partially smudged:\n\n"
    '"...sent it right before I left. Sometime during my last shift, within about a\n'
    ' 20-minute window starting around 09:30 UTC on the 14th. Didn\'t think a\n'
    ' timestamp made a good password, but it was quick..."\n\n'
    "File: message.enc  (first 16 bytes are the IV, AES-128-CBC afterward)\n"
)
with open("note.txt", "w") as f:
    f.write(note)

print(f"[organizer-only] true timestamp used: {true_ts_str}")
print(f"[organizer-only] derived key (hex):   {key.hex()}")
print("Wrote message.enc and note.txt (note.txt is player-facing; message.enc is player-facing).")
print("Do NOT distribute this script or the printed timestamp/key to players.")
