# SentinelBreach: Operation Blackwire — CH1, CH3, CH5 Implementation

This folder contains working builds of the three stages assigned to you
(Member 2): **CH1 – The Forgotten Endpoint**, **CH3 – Cracked Seal**, and
**CH5 – The Silent Capture**, matching the specs in Sections 10.1, 10.3 and
10.5 of the report. Everything here has been tested end-to-end (see
"How each was verified" below).

```
sentinelbreach/
├── ch1/                    # Live Docker web challenge
│   ├── docker-compose.yml
│   ├── web/
│   │   ├── Dockerfile
│   │   └── public/
│   │       ├── index.php               # decoy portal login
│   │       ├── robots.txt              # the disclosure vector
│   │       └── admin_console_2019/
│   │           └── index.php           # forgotten endpoint + flag
│   └── db/
│       └── init.sql                    # dummy employee records
├── ch3/                     # Static crypto challenge
│   ├── build_challenge.py  # organizer-only: generates message.enc + note.txt
│   └── solve_verify.py     # brute-force solver, used for FT-02 testing
└── ch5/                     # Static PCAP forensics challenge
    └── generate_pcap.py    # organizer-only, build-time-only: generates capture.pcapng
```

---

## CH1 — The Forgotten Endpoint

**To run locally (needs Docker + Docker Compose):**
```bash
cd ch1
docker compose up --build -d
```
- Portal: `http://localhost:8080/`
- The vulnerability: `http://localhost:8080/robots.txt` discloses
  `Disallow: /admin_console_2019/`, which is not linked anywhere else on the
  site. Browsing directly to it returns the internal incident note containing
  the flag.
- Change `FLAG` in `web/public/admin_console_2019/index.php` before a real
  deployment, and change the DB passwords in `docker-compose.yml`.

**To tear down:** `docker compose down -v`

Matches Table 4: PHP 8.2/Apache + MySQL 8, isolated bridge network
`10.30.1.0/24`, host `8080` → container `80`.

---

## CH3 — Cracked Seal

**To generate the challenge artefacts (organizer-only):**
```bash
cd ch3
pip install pycryptodome
python3 build_challenge.py
```
This writes:
- `message.enc` — 16-byte IV + AES-128-CBC ciphertext (**player-facing**)
- `note.txt` — the narrowed 20-minute time window (**player-facing**)

The script prints the true timestamp and derived key to the terminal for your
own records — **do not** give this output, or `build_challenge.py` itself, to
players. Only ship `message.enc` and `note.txt`.

**To verify it's solvable (for FT-01/FT-02 testing):**
```bash
python3 solve_verify.py message.enc
```
This brute-forces every second in the stated 20-minute window (1,200
candidates), which completes in well under a second and confirms the
intended solution path in Section 10.3 actually works.

To pin a specific timestamp instead of a random one inside the window:
```bash
python3 build_challenge.py "2026-03-14T09:41:00Z"
```

---

## CH5 — The Silent Capture

**To generate the PCAP (organizer/build-time only — never run this where
players can reach it):**
```bash
cd ch5
pip install scapy
python3 generate_pcap.py
```
This writes `capture.pcapng` (**the only player-facing artefact** — do not
distribute `generate_pcap.py`).

The capture contains:
- Background noise: unrelated DNS lookups and HTTP health-check sessions.
- **Artefact 1** — a TCP session on the unusual port **4444** between the
  CH1 web host (`10.30.1.10`) and an internal host (`10.30.4.50`), carrying
  the first half of the flag in its payload.
- **Artefact 2** — a normal-looking HTTP request from the same web host to
  the *same* internal host (`10.30.4.50`), carrying the second half of the
  flag in a custom `X-Debug-Flag-Part2` header.

Both must be found and combined — following only one stream is not enough,
matching the "two correlated artefacts" design in Section 10.5.

**To verify with tshark** (what a player would effectively do in Wireshark):
```bash
tshark -r capture.pcapng -q -z conv,tcp        # spot the odd port/host
tshark -r capture.pcapng -q -z "follow,tcp,ascii,<stream#>"
```

---

## How each was verified before delivery

- **CH1**: Served with PHP's built-in server; confirmed `robots.txt` discloses
  the path, the hidden endpoint returns HTTP 200 with the flag string, and the
  decoy login page renders without error.
- **CH3**: Ran `build_challenge.py` then `solve_verify.py` against the output
  — the brute-force recovers the exact timestamp, key, and flag.
- **CH5**: Ran `generate_pcap.py`, then used `tshark` to reproduce a player's
  workflow (protocol hierarchy → conversations → filter by host → follow
  both streams) and confirmed both flag halves are recoverable and combine
  correctly.

## Before you submit / deploy

- Change the flag values (`SBB{robots_txt_never_lies}`,
  `SBB{time_based_keys_are_not_random}`,
  `SBB{halfway_through_the_wire_and_found_in_headers}`) if you want unique
  ones, then keep the *_verify/build scripts in your organizer-only solution
  guide, not in anything handed to players.
- Change all default passwords in `ch1/docker-compose.yml`.
- Upload `message.enc` + `note.txt` (CH3) and `capture.pcapng` (CH5) to CTFd
  as file-bundle challenges; deploy CH1 via `docker compose` on the host
  described in Section 13/15 of the report.
