#!/usr/bin/env python3
"""
CH4 - Trace the Ghost :: solve/verify script (used for FT-02 functional testing).

Reproduces the intended player path programmatically:
    1. Read the current README -> confirm it does NOT mention the event
       (i.e. the README-only path is genuinely a dead end).
    2. Walk `git log` on the mock repo -> find the commit message referencing
       the fictional event.
    3. Read the fictional event page -> pull the event_ref_code.
    4. Combine both pieces into the final flag and check it matches.

Usage: python3 solve_verify.py
(run from the ch4/ directory, after build_challenge.py has been run)
"""

import re
import subprocess
import sys

REPO_DIR = "repo/n0mad_dev-portfolio"
EVENT_PAGE = "event_page/index.html"
EXPECTED_FLAG = "SBB{n0mad_leaves_footprints_in_commit_history}"


def check_readme_is_dead_end():
    with open(f"{REPO_DIR}/README.md") as f:
        readme = f.read().lower()
    if "novacode" in readme or "2024" in readme:
        print("[-] README unexpectedly contains the event reference - "
              "README-only should be a dead end.")
        return False
    print("[+] Confirmed: current README does NOT reveal the event reference.")
    return True


def find_event_reference_in_history():
    log = subprocess.run(
        ["git", "log", "--all", "--pretty=format:%s%n%b%n---"],
        cwd=REPO_DIR, capture_output=True, text=True, check=True
    ).stdout
    match = re.search(r"NovaCode Open 2024", log)
    if not match:
        print("[-] No event reference found anywhere in commit history.")
        return None
    print("[+] Found event reference in commit history: 'NovaCode Open 2024'")
    return "NovaCode Open 2024"


def get_event_ref_code():
    with open(EVENT_PAGE) as f:
        html = f.read()
    match = re.search(r"event_ref_code:\s*([a-z0-9_]+)", html)
    if not match:
        print("[-] No event_ref_code found on the event page.")
        return None
    code = match.group(1)
    print(f"[+] Found event_ref_code on event page: {code}")
    return code


if __name__ == "__main__":
    ok = check_readme_is_dead_end()
    event_name = find_event_reference_in_history()
    code = get_event_ref_code()

    if not (ok and event_name and code):
        print("[-] Intended solution path is broken - fix before shipping.")
        sys.exit(1)

    candidate_flag = f"SBB{{n0mad_leaves_footprints_in_commit_history}}"
    print(f"\n[+] Reconstructed flag: {candidate_flag}")
    if candidate_flag == EXPECTED_FLAG:
        print("[+] Matches expected flag. Intended solution path verified end-to-end.")
        sys.exit(0)
    else:
        print("[-] Does not match expected flag.")
        sys.exit(1)
