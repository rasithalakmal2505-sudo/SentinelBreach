#!/usr/bin/env python3
"""
CH5 - The Silent Capture :: organizer-only, build-time-only PCAP generator.

Runs ONLY during challenge preparation (per Section 10.5: "the traffic-generation
service is used only during challenge preparation/build-time and is not exposed
to players at any point"). The output capture.pcapng is the single player-facing
artefact.

Design (per Section 10.5 / Figure 1):
  - Background noise: assorted DNS lookups + unrelated HTTP sessions.
  - Relevant session 1 (TCP port 4444, 10.30.1.10 -> 10.30.4.50): a lateral-movement
    "C2-style" session whose payload carries the FIRST half of the flag.
  - Relevant session 2 (HTTP, same destination host 10.30.4.50): a request carrying
    the SECOND half of the flag in a custom header - correlated to session 1 only
    because it targets the same internal host, so a single stream is not enough.

Full flag = SBB{halfway_through_the_wire_and_found_in_headers}
"""

import random
from scapy.all import (
    Ether, IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap, PacketList
)

random.seed(1337)  # reproducible build

FLAG_PART1 = "halfway_through_the_wire_and_"   # in the TCP C2 stream payload
FLAG_PART2 = "found_in_headers"                 # in the HTTP header
FULL_FLAG = f"SBB{{{FLAG_PART1}{FLAG_PART2}}}"

ATTACKER_MAC = "02:00:00:00:01:0a"
INTERNAL_MAC = "02:00:00:00:04:32"

WEB_HOST = "10.30.1.10"       # CH1's compromised web server - origin of lateral movement
INTERNAL_HOST = "10.30.4.50"  # the internal host being reached (fictional "ghost host")

packets = []
base_time = 1000000.0


def next_time():
    global base_time
    base_time += random.uniform(0.05, 1.5)
    return base_time


def tcp_session(src, dst, sport, dport, payload_client=b"", payload_server=b"",
                 src_mac=ATTACKER_MAC, dst_mac=INTERNAL_MAC):
    """Build a full, stream-reconstructable TCP session: SYN, SYN-ACK, ACK,
    optional PSH+ACK payloads each way, then FIN/ACK teardown."""
    seq_c = random.randint(1000, 50000)
    seq_s = random.randint(1000, 50000)

    eth_cs = Ether(src=src_mac, dst=dst_mac)
    eth_sc = Ether(src=dst_mac, dst=src_mac)

    pkts = []
    # 3-way handshake
    pkts.append(eth_cs / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags="S", seq=seq_c))
    seq_c += 1
    pkts.append(eth_sc / IP(src=dst, dst=src) / TCP(sport=dport, dport=sport, flags="SA", seq=seq_s, ack=seq_c))
    seq_s += 1
    pkts.append(eth_cs / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags="A", seq=seq_c, ack=seq_s))

    if payload_client:
        pkts.append(eth_cs / IP(src=src, dst=dst) /
                     TCP(sport=sport, dport=dport, flags="PA", seq=seq_c, ack=seq_s) /
                     Raw(load=payload_client))
        pkts.append(eth_sc / IP(src=dst, dst=src) /
                     TCP(sport=dport, dport=sport, flags="A", seq=seq_s, ack=seq_c + len(payload_client)))
        seq_c += len(payload_client)

    if payload_server:
        pkts.append(eth_sc / IP(src=dst, dst=src) /
                     TCP(sport=dport, dport=sport, flags="PA", seq=seq_s, ack=seq_c) /
                     Raw(load=payload_server))
        pkts.append(eth_cs / IP(src=src, dst=dst) /
                     TCP(sport=sport, dport=dport, flags="A", seq=seq_c, ack=seq_s + len(payload_server)))
        seq_s += len(payload_server)

    # Teardown
    pkts.append(eth_cs / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags="FA", seq=seq_c, ack=seq_s))
    seq_c += 1
    pkts.append(eth_sc / IP(src=dst, dst=src) / TCP(sport=dport, dport=sport, flags="FA", seq=seq_s, ack=seq_c))
    seq_s += 1
    pkts.append(eth_cs / IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags="A", seq=seq_c, ack=seq_s))

    for p in pkts:
        p.time = next_time()
    return pkts


def dns_query(qname, src="10.30.1.20"):
    p = (Ether(src="02:00:00:00:01:14", dst="02:00:00:00:00:01") /
         IP(src=src, dst="10.30.1.1") /
         UDP(sport=random.randint(1024, 60000), dport=53) /
         DNS(rd=1, qd=DNSQR(qname=qname)))
    p.time = next_time()
    return p


# --- 1. Background noise: unrelated DNS lookups ---
noise_domains = [
    "ntp.ubuntu.com", "pool.ntp.org", "novagrid-status.example",
    "cdn.fontprovider.example", "telemetry.novagrid-internal.example",
    "mail.novagrid-utilities.example", "updates.novagrid-utilities.example",
]
for d in noise_domains:
    packets.append(dns_query(d, src=f"10.30.1.{random.randint(20,40)}"))

# --- 2. Background noise: unrelated HTTP sessions between random internal hosts ---
for i in range(4):
    src_ip = f"10.30.1.{random.randint(20,40)}"
    dst_ip = f"10.30.1.{random.randint(50,60)}"
    req = f"GET /status HTTP/1.1\r\nHost: {dst_ip}\r\nUser-Agent: internal-healthcheck/1.0\r\n\r\n".encode()
    resp = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
    packets.extend(tcp_session(src_ip, dst_ip, random.randint(40000, 60000), 80, req, resp,
                                src_mac=f"02:00:00:00:01:{i:02x}", dst_mac=f"02:00:00:00:01:{i+50:02x}"))

# --- 3. RELEVANT SESSION 1: lateral-movement C2-style TCP session on port 4444 ---
# WEB_HOST (compromised in CH1) reaches out to INTERNAL_HOST on an unusual port.
c2_client_msg = b"AUTH_TOKEN_PART1=" + FLAG_PART1.encode() + b"\n"
c2_server_msg = b"ACK: session established. awaiting further instructions.\n"
packets.extend(tcp_session(WEB_HOST, INTERNAL_HOST, 51555, 4444, c2_client_msg, c2_server_msg))

# --- more noise between the two relevant sessions, so they aren't adjacent ---
for d in ["backup.novagrid-utilities.example", "logs.novagrid-internal.example"]:
    packets.append(dns_query(d, src="10.30.1.22"))

# --- 4. RELEVANT SESSION 2: HTTP request to the SAME internal host, custom header ---
http_req = (
    f"GET /internal/diag HTTP/1.1\r\n"
    f"Host: {INTERNAL_HOST}\r\n"
    f"User-Agent: novagrid-diag-tool/2.3\r\n"
    f"X-Debug-Flag-Part2: {FLAG_PART2}\r\n"
    f"\r\n"
).encode()
http_resp = b"HTTP/1.1 200 OK\r\nContent-Length: 15\r\n\r\ndiagnostics: ok"
packets.extend(tcp_session(WEB_HOST, INTERNAL_HOST, 51600, 80, http_req, http_resp))

# --- a bit more trailing noise ---
for d in ["metrics.novagrid-utilities.example"]:
    packets.append(dns_query(d, src="10.30.1.25"))

# Sort by timestamp so the capture reads chronologically
packets.sort(key=lambda p: p.time)

wrpcap("capture.pcapng", PacketList(packets))
print(f"Wrote capture.pcapng with {len(packets)} packets.")
print(f"[organizer-only] Full flag: {FULL_FLAG}")
print("This script and the printed flag must NOT be shipped to players - only capture.pcapng.")
