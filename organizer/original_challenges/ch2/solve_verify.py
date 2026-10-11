#!/usr/bin/env python3
"""
CH2 - Pixels Don't Lie :: solve/verify script (used for FT-02 functional testing).

Extracts the LSB-embedded message from a PNG using the exact scheme from
Section 10.2 - LSB of R,G,B, MSB-first, terminated by a fixed delimiter -
exactly the intended player solution path (after ruling out metadata/strings).

Usage: python3 solve_verify.py suspicious_image.png
"""

import sys
from PIL import Image

DELIMITER = "#####"


def extract_lsb(path):
    img = Image.open(path).convert("RGB")
    bits = []
    for (r, g, b) in img.getdata():
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
    bits = "".join(bits)

    chars = []
    for i in range(0, len(bits) - 8 + 1, 8):
        byte = bits[i:i + 8]
        chars.append(chr(int(byte, 2)))
        if "".join(chars[-len(DELIMITER):]) == DELIMITER:
            return "".join(chars[:-len(DELIMITER)])
    return None  # delimiter never found


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "suspicious_image.png"
    result = extract_lsb(path)
    if result and result.startswith("SBB{"):
        print(f"[+] Recovered hidden message: {result}")
        sys.exit(0)
    else:
        print("[-] No valid flag recovered.")
        sys.exit(1)
