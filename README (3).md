# SentinelBreach CTF Platform

## Run the central portal

Requires Python 3.10+ and no third-party Python package.

```bash
cd platform
python app.py
```

Open `http://localhost:8000`, register a player account, and use the Challenges page.

## Run CH1

In a second terminal, with Docker installed:

```bash
cd challenges/ch1
docker compose up --build -d
```

CH1 is then available at `http://localhost:8080/`.

## Run CH6 Part B (live container)

CH6's flag is only scored on Part B, a live Linux/sudo-misconfiguration challenge. The
player SSH password must equal the credential recovered from CH6 Part A (the `lock`
binary players download from the portal):

```bash
cd challenges/ch6/partB
CH6_PLAYER_PASSWORD="<same credential as the lock binary>" \
CH6_FLAG="SBB{sudo_wildcard_is_not_a_sandbox}" \
./build.sh
```

Players then connect with `ssh player@localhost -p 2222`.

## Architecture

The portal owns accounts, flag submission, solve tracking and the scoreboard.

- **CH1** — isolated Docker web challenge (`challenges/ch1`), launched separately.
- **CH2** — downloadable steganography image (`ch2/`).
- **CH3** — downloadable crypto file challenge (`ch3/`).
- **CH4** — downloadable OSINT challenge: a starting clue, a static event page, and a
  zipped Git repo with the real clue buried in its commit history (`ch4/`).
- **CH5** — downloadable PCAP forensics challenge (`ch5/`).
- **CH6** — two-part capstone: Part A is a downloadable RE binary (`ch6/partA/`); Part B
  is a live Docker/SSH container (`challenges/ch6/partB`) that must be started separately,
  the same way CH1 is. Only the Part B flag is scored.

All six challenges are now integrated and enabled.

Do not publish the `organizer/` directory; it contains build/verification scripts and organizer material.
