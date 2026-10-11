#!/usr/bin/env python3
"""
CH3 - Cracked Seal :: solve/verify script (used for FT-02 functional testing).

Brute-forces every second in the 20-minute window stated in note.txt,
derives a candidate AES key from each timestamp, attempts decryption,
and validates PKCS#7 padding + expected plaintext structure - exactly
the intended player solution path from Section 10.3.

Usage: python3 solve_verify.py message.enc
"""

import hashlib
import sys
from datetime import datetime, timedelta, timezone
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

WINDOW_START = datetime(2026, 3, 14, 9, 30, 0, tzinfo=timezone.utc)
WINDOW_MINUTES = 20


def try_decrypt(enc_path):
    with open(enc_path, "rb") as f:
        blob = f.read()
    iv, ciphertext = blob[:16], blob[16:]

    for offset in range(WINDOW_MINUTES * 60):
        ts = WINDOW_START + timedelta(seconds=offset)
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        key = hashlib.sha256(ts_str.encode()).digest()[:16]

        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        except (ValueError, KeyError):
            continue  # bad padding -> wrong candidate

        if b"FLAG: SBB{" in plaintext:
            print(f"[+] Candidate timestamp found: {ts_str}")
            print(f"[+] Derived key: {key.hex()}")
            print("[+] Recovered plaintext:\n")
            print(plaintext.decode(errors="replace"))
            return True

    print("[-] No valid candidate found in the search window.")
    return False


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "message.enc"
    ok = try_decrypt(path)
    sys.exit(0 if ok else 1)
