# SentinelBreach: Operation Blackwire — CH2, CH4, CH6 Implementation

This folder contains working builds of the three stages you're implementing:
**CH2 – Pixels Don't Lie**, **CH4 – Trace the Ghost**, and **CH6 – Break the
Lock (Capstone)**, matching the specs in Sections 10.2, 10.4 and 10.6 of the
report. Everything here has been tested end-to-end (see "How each was
verified" below). Layout matches your teammate's CH1/CH3/CH5 package so the
two folders can be merged directly into one repo.

```
sentinelbreach/
├── ch2/                        # Static steganography challenge
│   ├── build_challenge.py      # organizer-only: generates suspicious_image.png
│   └── solve_verify.py         # extracts the hidden flag, used for FT-02 testing
├── ch4/                        # Static OSINT challenge
│   ├── build_challenge.py      # organizer-only: builds mock repo + event page + clue
│   └── solve_verify.py         # reproduces the intended path, used for FT-02 testing
└── ch6/                         # Capstone: RE (static) + Linux (live Docker)
    ├── partA/                   # Reverse engineering
    │   ├── build_challenge.py  # organizer-only: generates lock.c + compiles ./lock
    │   ├── README.txt          # player-facing, ships with the binary
    │   └── solve_verify.py     # confirms the intended solution + no plaintext leak
    └── partB/                   # Live Linux/System Security container
        ├── Dockerfile
        ├── docker-compose.yml
        ├── logrotate_check.sh  # the intentionally vulnerable admin script
        ├── novagrid.sudoers    # the intentional sudo misconfiguration
        ├── build.sh            # builds/runs the container with the right creds
        └── solve_verify.sh     # FT-02/ST-03 style end-to-end check over SSH
```

---

## CH2 — Pixels Don't Lie

**To generate the challenge artefact (organizer-only):**
```bash
cd ch2
pip install pillow
python3 build_challenge.py
```
This writes:
- `cover_raw.png` — build intermediate, **not player-facing** (no hidden data)
- `suspicious_image.png` — **the only player-facing artefact**

The cover photo is generated synthetically (gradient sky + skyline silhouette
+ light noise) so there's no external image licensing to worry about. The
flag `SBB{pixels_never_lie_lsb_reveals_all}` is embedded exactly per Section
10.2's scheme: LSB of R, G, B in that order, MSB-first per character,
terminated by a `#####` delimiter. Nothing is in EXIF metadata or appended
after the image data.

**To verify it's solvable (for FT-01/FT-02 testing):**
```bash
python3 solve_verify.py suspicious_image.png
```

**Sanity-check the "wrong lead" doesn't work either** (should return nothing):
```bash
exiftool suspicious_image.png | grep -i flag
strings suspicious_image.png | grep "SBB{"
```

---

## CH4 — Trace the Ghost

**To generate the challenge artefacts (organizer-only):**
```bash
cd ch4
python3 build_challenge.py
```
This writes:
- `starting_clue.txt` — **player-facing**
- `repo/n0mad_dev-portfolio/` — a real, browsable Git repo — **player-facing**
- `event_page/index.html` — the fictional event page — **player-facing**

Design, matching Section 10.4 exactly:
- Username `n0mad_dev` and every resource here is fictional, created only
  for this exercise — no real accounts, repos, or events anywhere.
- The README (both at commit 1 and again after it's updated at commit 5)
  never mentions the event — reading only the current README is a genuine
  dead end.
- The real clue — a reference to **"NovaCode Open 2024"** — is buried in the
  **commit message** of the 3rd commit, findable via `git log`.
- The fictional event page lists results for that event and gives an
  `event_ref_code`, which the player combines with the commit-history find
  to complete the flag: `SBB{n0mad_leaves_footprints_in_commit_history}`.

**To verify the intended path actually works (for FT-01/FT-02 testing):**
```bash
python3 solve_verify.py
```
This checks the README is a dead end, walks `git log` for the event
reference, pulls the `event_ref_code` from the event page, and confirms the
reconstructed flag matches.

**To deploy for players:** push `repo/n0mad_dev-portfolio/` to a throwaway
Git host (a dedicated GitHub account made only for this CTF, or a
self-hosted Gitea container on the CH4/CH6-A reserved segment,
`10.30.5.0/24`), and serve `event_page/index.html` as a static page (e.g. via
the same Nginx that fronts the platform, or another CTFd file/link
challenge). Upload `starting_clue.txt` as the CH4 challenge description or
attached file in CTFd.

---

## CH6 — Break the Lock (Capstone)

### Part A — Reverse Engineering

**To generate the binary (organizer-only):**
```bash
cd ch6/partA
python3 build_challenge.py
```
This writes:
- `lock.c` — organizer-only source, **do not ship**
- `lock` — the compiled, statically-linked, stripped binary — **player-facing**
- `README.txt` — already player-facing, ships alongside `lock`

The credential is stored in the binary only after a single-byte XOR
transform (key `0x5a`), matching Section 10.6's "reversible transformation
before comparison" — recoverable in Ghidra by finding the comparison buffer
and the XOR key used against user input.

**To verify (for FT-01/FT-02 testing):**
```bash
python3 solve_verify.py "gh0st_1n_th3_w1r3"
```
Confirms the credential never appears in plain `strings` output, the correct
credential returns "Access granted.", and a wrong one returns "Access
denied."

### Part B — Linux/System Security (live container)

**To build and run** (needs Docker + Docker Compose):
```bash
cd ch6/partB
CH6_PLAYER_PASSWORD="gh0st_1n_th3_w1r3" \
CH6_FLAG="SBB{sudo_wildcard_is_not_a_sandbox}" \
./build.sh
```
`CH6_PLAYER_PASSWORD` **must** equal the credential Part A's build script
printed, so the two parts connect correctly. Container comes up on
`10.30.6.0/24` (internal-only bridge, no outbound internet), host `2222` →
container `22`, matching Section 14/Table 15.

The intentional misconfiguration: `player` can run
`/opt/novagrid/logrotate_check.sh` as root, passwordless, with no argument
restriction (`novagrid.sudoers`). The script passes its argument straight
into `bash -c`, so anything a player supplies runs as root — a realistic
"overly broad sudo rule" finding rather than a kernel exploit, fully
contained inside the disposable container.

**To verify end-to-end (for FT-01/FT-02/ST-03 testing)**, once the
container is up:
```bash
CH6_PLAYER_PASSWORD="gh0st_1n_th3_w1r3" ./solve_verify.sh
```
(needs `sshpass`; `apt install sshpass` if you don't have it). This SSHes in,
runs `sudo -l`, exploits the rule to read `/root/flag.txt`, and confirms the
container has no outbound connectivity — i.e. the escalation can't reach
anything outside its own network segment.

**Only the Part B flag is scored** — recovering the Part A credential alone
does not award points, per Section 10.6.

---

## How each was verified before delivery

- **CH2**: Ran `build_challenge.py`, then `solve_verify.py` against the
  output — the exact embedded flag is recovered. Confirmed separately with
  `exiftool` and `strings` that neither reveals anything, so LSB extraction
  is genuinely the only route.
- **CH4**: Ran `build_challenge.py`, then `solve_verify.py` — confirms the
  README is a dead end, the commit-history reference is discoverable via
  `git log`, the event page's `event_ref_code` is present, and the
  reconstructed flag matches exactly.
- **CH6 Part A**: Ran `build_challenge.py`, then `solve_verify.py` — confirms
  no plaintext credential leak via `strings`, correct credential grants
  access, wrong credential is rejected.
- **CH6 Part B**: Validated the vulnerable script's argument-injection logic
  directly (`./logrotate_check.sh "id && echo EXPLOIT_WORKED"` executes both
  commands, confirming arbitrary command execution through the unsanitised
  parameter) and checked `novagrid.sudoers` syntax. Full container
  build/SSH/`sudo -l`/exploit flow should be re-run with `build.sh` +
  `solve_verify.sh` on a machine with Docker before the live event, since
  this was built in an environment without a Docker daemon available.

## Before you submit / deploy

- Change the flag values if you want unique ones per stage:
  `SBB{pixels_never_lie_lsb_reveals_all}` (CH2),
  `SBB{n0mad_leaves_footprints_in_commit_history}` (CH4),
  `SBB{sudo_wildcard_is_not_a_sandbox}` (CH6 Part B) — then keep every
  `build_challenge.py` / `solve_verify.*` script in your organizer-only
  solution guide, never handed to players.
- CH6: rotate `CH6_PLAYER_PASSWORD`/the Part A `CREDENTIAL` together if you
  regenerate either — they must always match.
- Run the full CH6 Part B build/verify flow on a Docker-capable host before
  the live event (see note above).
- Upload `suspicious_image.png` (CH2) and `starting_clue.txt` + the pushed
  repo link + event page link (CH4) to CTFd as file-bundle / resource-index
  challenges; deploy CH6 Part B via `docker compose` on the host described
  in Section 13/15 of the report, and distribute `lock` + `README.txt`
  (CH6 Part A) as a file-bundle challenge.
