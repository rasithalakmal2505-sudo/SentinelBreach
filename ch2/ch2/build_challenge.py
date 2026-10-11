#!/usr/bin/env python3
"""
CH2 - Pixels Don't Lie :: organizer-only build script.

Generates a synthetic "ordinary photograph" cover image (so no external
asset/licensing dependency) and embeds the flag using LSB steganography,
matching Section 10.2's defined scheme exactly:

    - LSB of each colour channel, in order R, G, B
    - Most-significant-bit-first per character
    - Terminated by a fixed delimiter sequence

Produces the ONLY player-facing artefact: suspicious_image.png
KEEP THIS SCRIPT IN THE ORGANIZER-ONLY SOLUTION GUIDE. Do not ship it to players.
"""

import random
from PIL import Image, ImageDraw, ImageFilter

FLAG = "SBB{pixels_never_lie_lsb_reveals_all}"
DELIMITER = "#####"          # marks end of embedded message
WIDTH, HEIGHT = 900, 600
SEED = 2026


def make_cover_image(path):
    """Builds a believable-looking synthetic photo (gradient sky + skyline
    silhouette + noise) so the file isn't obviously blank/synthetic when
    opened casually, and has enough pixel capacity for the payload."""
    random.seed(SEED)
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Sky gradient
    top = (25, 35, 70)
    bottom = (240, 150, 90)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Simple city skyline silhouette
    x = 0
    while x < WIDTH:
        w = random.randint(30, 70)
        h = random.randint(80, 260)
        draw.rectangle([x, HEIGHT - h, x + w, HEIGHT], fill=(15, 15, 25))
        x += w + random.randint(2, 10)

    # Light pixel noise so LSB planes aren't suspiciously uniform
    pixels = img.load()
    for _ in range(20000):
        px = random.randint(0, WIDTH - 1)
        py = random.randint(0, HEIGHT - 1)
        r, g, b = pixels[px, py]
        jitter = random.randint(-3, 3)
        pixels[px, py] = (
            max(0, min(255, r + jitter)),
            max(0, min(255, g + jitter)),
            max(0, min(255, b + jitter)),
        )

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    img.save(path)


def embed_lsb(input_path, output_path, secret_text):
    img = Image.open(input_path).convert("RGB")
    pixels = list(img.getdata())

    message = secret_text + DELIMITER
    bits = "".join(format(ord(c), "08b") for c in message)

    if len(bits) > len(pixels) * 3:
        raise ValueError("Cover image too small for payload.")

    new_pixels = []
    bit_idx = 0
    for (r, g, b) in pixels:
        channels = [r, g, b]
        for i in range(3):
            if bit_idx < len(bits):
                channels[i] = (channels[i] & ~1) | int(bits[bit_idx])
                bit_idx += 1
        new_pixels.append(tuple(channels))

    img.putdata(new_pixels)
    img.save(output_path)
    return len(message)


if __name__ == "__main__":
    make_cover_image("cover_raw.png")
    n_chars = embed_lsb("cover_raw.png", "suspicious_image.png", FLAG)
    print(f"[organizer-only] Flag embedded: {FLAG}")
    print(f"[organizer-only] {n_chars} characters ({n_chars * 8} bits) written into LSBs.")
    print("Wrote suspicious_image.png (player-facing).")
    print("cover_raw.png is a build intermediate only - do not ship it (it has no hidden data).")
