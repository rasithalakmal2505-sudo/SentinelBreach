#!/usr/bin/env python3
"""
CH4 - Trace the Ghost :: organizer-only build script.

Generates the two fictional, organizer-hosted resources described in
Section 10.4, plus the player-facing starting clue:

    starting_clue.txt              - player-facing
    repo/n0mad_dev-portfolio/       - mock Git repo, player-facing (via `git log`)
    event_page/index.html          - fictional event page, player-facing (static HTML)

Design (per Section 10.4):
    - Username: n0mad_dev (fictional)
    - README gives only a surface-level clue.
    - The REAL clue (an event name/ID) is buried in commit history, not the
      current README - so reading only the latest README is a dead end.
    - The fictional event page confirms/completes the reference found in the
      commit history; both pieces must be combined to get the flag.

Every identity/resource here is entirely fictional and created for this
exercise - no real usernames, accounts, repos, or events are referenced.

KEEP THIS SCRIPT IN THE ORGANIZER-ONLY SOLUTION GUIDE. Do not ship it, and do
not ship the .git internals of any *other* throwaway/staging copy you make -
only the finished repo/event_page produced here.
"""

import os
import shutil
import subprocess

FLAG = "SBB{n0mad_leaves_footprints_in_commit_history}"
EVENT_NAME = "NovaCode Open 2024"
EVENT_CODE = "commit_history_never_forgets"   # combines with repo clue -> flag suffix
REPO_DIR = "repo/n0mad_dev-portfolio"
EVENT_DIR = "event_page"


def run(cmd, cwd=None, env=None):
    subprocess.run(cmd, cwd=cwd, env=env, check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def git_commit(cwd, message, date, files_to_stage=None):
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "n0mad_dev"
    env["GIT_AUTHOR_EMAIL"] = "n0mad.dev@example-mail.invalid"
    env["GIT_COMMITTER_NAME"] = "n0mad_dev"
    env["GIT_COMMITTER_EMAIL"] = "n0mad.dev@example-mail.invalid"
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    if files_to_stage:
        run(["git", "add"] + files_to_stage, cwd=cwd, env=env)
    else:
        run(["git", "add", "-A"], cwd=cwd, env=env)
    run(["git", "commit", "-m", message], cwd=cwd, env=env)


def build_repo():
    if os.path.exists(REPO_DIR):
        shutil.rmtree(REPO_DIR)
    os.makedirs(REPO_DIR)
    run(["git", "init", "-q", "-b", "main"], cwd=REPO_DIR)

    # --- Commit 1: initial scaffold ---
    write(f"{REPO_DIR}/README.md", (
        "# n0mad_dev's portfolio\n\n"
        "Hi, I'm n0mad_dev. I tinker with small security and scripting "
        "projects in my spare time.\n"
    ))
    git_commit(REPO_DIR, "initial commit: portfolio scaffold", "2024-01-08T10:15:00")

    # --- Commit 2: adds a project ---
    write(f"{REPO_DIR}/projects/port_scanner.py", (
        "# tiny multi-threaded TCP port scanner - practice project\n"
        "# TODO: add banner grabbing\n"
    ))
    git_commit(REPO_DIR, "add: simple port scanner practice project",
               "2024-02-14T19:40:00")

    # --- Commit 3: THIS is where the real clue is buried, in the message ---
    write(f"{REPO_DIR}/notes/prep.md", (
        "Prepping submissions this week - deadline is tight.\n"
        "Signed up for the CTF-style quals under my usual handle.\n"
    ))
    git_commit(
        REPO_DIR,
        (
            "prep: final polish before submitting to NovaCode Open 2024 quals\n\n"
            "Cutting it close on time this round. Using the same handle as "
            "always for the leaderboard - shouldn't be hard to find if anyone's "
            "looking."
        ),
        "2024-03-02T22:05:00",
    )

    # --- Commit 4: unrelated noise commit, README still doesn't mention the event ---
    write(f"{REPO_DIR}/projects/notes_app.py", (
        "# small CLI notes app, unfinished\n"
    ))
    git_commit(REPO_DIR, "wip: notes app skeleton", "2024-05-19T14:22:00")

    # --- Commit 5: README is updated LATER but the event reference is never re-added ---
    write(f"{REPO_DIR}/README.md", (
        "# n0mad_dev's portfolio\n\n"
        "Hi, I'm n0mad_dev. I tinker with small security and scripting "
        "projects in my spare time.\n\n"
        "## Projects\n"
        "- `projects/port_scanner.py` - simple TCP port scanner\n"
        "- `projects/notes_app.py` - unfinished CLI notes app\n"
    ))
    git_commit(REPO_DIR, "docs: update README project list", "2024-07-03T09:10:00")

    print(f"[organizer-only] Mock repo built at {REPO_DIR}/")
    print("[organizer-only] Real clue lives in the commit MESSAGE of the "
          "3rd commit (`git log`), not in any file content or the latest README.")


def build_event_page():
    if os.path.exists(EVENT_DIR):
        shutil.rmtree(EVENT_DIR)
    os.makedirs(EVENT_DIR)
    write(f"{EVENT_DIR}/index.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{EVENT_NAME} - Results Archive</title>
<style>
  body {{ font-family: Arial, sans-serif; background:#f4f4f4; color:#222; margin:0; padding:2rem; }}
  .wrap {{ max-width:720px; margin:0 auto; background:#fff; padding:2rem; border-radius:6px;
           box-shadow:0 2px 10px rgba(0,0,0,.08); }}
  h1 {{ color:#1b263b; }}
  table {{ width:100%; border-collapse:collapse; margin-top:1rem; }}
  th, td {{ text-align:left; padding:.5rem; border-bottom:1px solid #ddd; }}
  .footer-code {{ font-family: monospace; background:#eee; padding:.6rem; border-radius:4px;
                  margin-top:1.5rem; font-size:.9rem; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>{EVENT_NAME} &mdash; Results Archive</h1>
  <p>Fictional qualifier event archive, generated for a university CTF exercise.
     No real individuals, teams, or organisations are represented.</p>
  <table>
    <tr><th>Handle</th><th>Category</th><th>Placement</th></tr>
    <tr><td>voidwalker22</td><td>Web</td><td>4th</td></tr>
    <tr><td>n0mad_dev</td><td>Scripting / Automation</td><td>2nd</td></tr>
    <tr><td>kestrel.eth</td><td>Crypto</td><td>7th</td></tr>
    <tr><td>bramble_fox</td><td>OSINT</td><td>5th</td></tr>
  </table>
  <p>Archive note: results pages for this cycle use the reference code below
     instead of full write-ups (write-ups were never published for this
     season).</p>
  <div class="footer-code">event_ref_code: {EVENT_CODE}</div>
</div>
</body>
</html>
""")
    print(f"[organizer-only] Fictional event page built at {EVENT_DIR}/index.html")


def build_starting_clue():
    write("starting_clue.txt", (
        "Case file fragment - ShadowTrace attribution lead\n"
        "---------------------------------------------------\n"
        "Handle observed in intercepted infrastructure logs: n0mad_dev\n"
        "Known interest: cybersecurity / scripting side-projects.\n"
        "One partial reference recovered: \"...a programming competition in 2024...\"\n"
        "\n"
        "Trace this alias across whatever public footprint it has left behind.\n"
    ))
    print("[organizer-only] starting_clue.txt written (player-facing).")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    build_starting_clue()
    build_repo()
    build_event_page()
    print()
    print(f"[organizer-only] Full flag: {FLAG}")
    print("[organizer-only] Intended path: README (dead end) -> `git log` on the repo "
          "-> commit message mentions 'NovaCode Open 2024' -> event page -> "
          "event_ref_code confirms/completes the flag.")
    print("Ship ONLY: starting_clue.txt, repo/n0mad_dev-portfolio/ (as a browsable git "
          "repo, e.g. pushed to a throwaway host), and event_page/index.html.")
