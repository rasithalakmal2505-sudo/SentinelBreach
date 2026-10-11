#!/usr/bin/env python3
"""
CH6 Part A - Break the Lock :: solve/verify script (used for FT-02 testing).

1. Confirms the credential does NOT leak in `strings` output (it shouldn't -
   it's only ever present XORed).
2. Feeds the correct credential to ./lock and confirms "Access granted."
3. Feeds a wrong credential and confirms "Access denied."

This does not "reverse" the binary itself (that's the player's job in
Ghidra) - it just proves the intended solution, once found, actually works.

Usage: python3 solve_verify.py <credential>
"""

import subprocess
import sys


def strings_leak_check(binary_path, credential):
    out = subprocess.run(["strings", binary_path], capture_output=True, text=True).stdout
    if credential in out:
        print(f"[-] LEAK: credential '{credential}' found in plain strings output!")
        return False
    print("[+] Confirmed: credential does not appear in plain `strings` output.")
    return True


def run_lock(binary_path, candidate):
    result = subprocess.run(
        [binary_path], input=candidate + "\n",
        capture_output=True, text=True
    )
    return result.stdout.strip(), result.returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 solve_verify.py <credential>")
        sys.exit(1)

    credential = sys.argv[1]
    binary = "./lock"

    ok = strings_leak_check(binary, credential)

    out, rc = run_lock(binary, credential)
    print(f"[correct credential] output: {out!r} (exit {rc})")
    correct_pass = "Access granted" in out and rc == 0

    out2, rc2 = run_lock(binary, "definitely_wrong_key")
    print(f"[wrong credential]   output: {out2!r} (exit {rc2})")
    wrong_pass = "Access denied" in out2 and rc2 != 0

    if ok and correct_pass and wrong_pass:
        print("[+] Part A verified: intended solution path works, no plaintext leak.")
        sys.exit(0)
    else:
        print("[-] Part A verification FAILED - fix before shipping.")
        sys.exit(1)
