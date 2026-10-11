#!/usr/bin/env python3
"""
CH6 Part A - Break the Lock :: organizer-only build script.

Generates lock.c with the CREDENTIAL already XOR-encoded against KEY and
baked in as a byte array, then compiles the static player-facing binary.

Design (per Section 10.6):
    - Reversible transformation: single-byte XOR.
    - Player recovers CREDENTIAL by reversing the XOR in Ghidra (or by
      writing a quick script once they've identified the key byte).
    - CREDENTIAL becomes the SSH password for Part B - Part A alone does not
      award points (only the Part B flag does, per Section 10.6).

KEEP THIS SCRIPT IN THE ORGANIZER-ONLY SOLUTION GUIDE. Never ship it, and
never ship CREDENTIAL/KEY anywhere player-visible except embedded (XORed)
inside the compiled binary itself.
"""

import subprocess

CREDENTIAL = "gh0st_1n_th3_w1r3"     # becomes the Part B SSH password
KEY = 0x5A                            # single-byte XOR key

C_TEMPLATE = """#include <stdio.h>
#include <string.h>

/* Legacy access-check utility recovered from a ShadowTrace-linked host.
 * "asks for a key" - per the README given to players. */

static const unsigned char stored[] = {{{stored_bytes}}};
static const unsigned char xor_key = {key:#04x};

int main(void) {{
    char input[128];

    printf("Enter key: ");
    if (!fgets(input, sizeof(input), stdin)) {{
        return 1;
    }}
    input[strcspn(input, "\\n")] = '\\0';

    size_t len = strlen(input);
    if (len != sizeof(stored)) {{
        printf("Access denied.\\n");
        return 1;
    }}

    unsigned char transformed[128];
    for (size_t i = 0; i < len; i++) {{
        transformed[i] = (unsigned char)input[i] ^ xor_key;
    }}

    if (memcmp(transformed, stored, len) == 0) {{
        printf("Access granted.\\n");
        return 0;
    }}

    printf("Access denied.\\n");
    return 1;
}}
"""


def build_stored_bytes(credential, key):
    return [ord(c) ^ key for c in credential]


if __name__ == "__main__":
    stored = build_stored_bytes(CREDENTIAL, KEY)
    stored_bytes_str = ", ".join(f"{b:#04x}" for b in stored)

    c_source = C_TEMPLATE.format(stored_bytes=stored_bytes_str, key=KEY)
    with open("lock.c", "w") as f:
        f.write(c_source)

    subprocess.run(
        ["gcc", "-static", "-O0", "-o", "lock", "lock.c"],
        check=True,
    )
    subprocess.run(["strip", "--strip-unneeded", "lock"], check=True)

    print(f"[organizer-only] CREDENTIAL (= Part B SSH password): {CREDENTIAL}")
    print(f"[organizer-only] XOR key: {KEY:#04x}")
    print("Wrote lock.c (organizer-only source) and compiled ./lock (player-facing binary).")
    print("Ship ONLY the compiled 'lock' binary and README.txt to players - never lock.c.")
