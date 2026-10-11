# SentinelBreach — integrated CTF platform

This package integrates all six challenges into one portal.

- CH1: Docker web challenge (`challenges/ch1`, launched separately)
- CH2: LSB steganography file challenge (`ch2/suspicious_image.png`)
- CH3: AES file challenge (`ch3/message.enc` + `ch3/note.txt`)
- CH4: OSINT challenge (`ch4/starting_clue.txt`, `ch4/event_page/`, `ch4/n0mad_dev-portfolio.zip`)
- CH5: PCAP forensics challenge (`ch5/capture.pcapng`)
- CH6: two-part capstone — Part A RE binary (`ch6/partA`), Part B live Docker/SSH
  container (`challenges/ch6/partB`, launched separately, only its flag is scored)
- Platform: Python standard library + SQLite
- Organizer scripts (build/solve/verify tooling, source files, secrets): under
  `organizer/original_challenges` — do not publish

See `platform/README.md` for setup, including how to bring up CH1 and CH6 Part B.
