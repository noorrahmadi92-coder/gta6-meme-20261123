#!/usr/bin/env python3
"""Deterministic generator for the gta6-meme-x-01 entry meme.

WANTED poster, Vice City sunset style: the make.fun ghost is the wanted
AI agent, wanted for getting paid real money while everyone waits for GTA 6.

Usage:  python3 generate_meme.py [output.png]
Default output: meme.png next to this script. Pure Pillow, no network.
All inputs (fonts, press-kit art) live in this repository, so the output
is byte-identical on every run.
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "meme.png"

W, H = 1200, 1200

INK = (25, 20, 25)          # make.fun ink #191419
MAGENTA = (196, 28, 131)    # make.fun magenta #c41c83
PARCHMENT = (246, 234, 210)
CREAM = (255, 244, 214)

ANTON = str(HERE / "fonts" / "Anton-Regular.ttf")
INTER = str(HERE / "fonts" / "Inter.ttf")


def font(path, size):
    f = ImageFont.truetype(path, size)
    if path == INTER:
        try:
            f.set_variation_by_axes([700])  # Inter Bold
        except Exception:
            pass
    return f


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textlength(ch, font=fnt) for ch in text) + tracking * max(len(text) - 1, 0)


def draw_tracked(draw, cx, y, text, fnt, fill, tracking=0):
    """Draw text centred on cx with extra letter spacing."""
    total = tracked_width(draw, text, fnt, tracking)
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def vgrad(size, stops):
    """Vertical gradient. stops: list of (position 0..1, (r,g,b))."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = tuple(round(c0[j] + (c1[j] - c0[j]) * f) for j in range(3))
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def draw_sun(draw, cx, cy, r):
    """Retro synthwave sun with horizontal slats on its lower half."""
    sun = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse([0, 0, r * 2, r * 2], fill=(255, 183, 77, 255))
    # slats: cut the lower half with sky-coloured bars, gaps widen downward
    y = r + 8
    gap = 4
    while y < r * 2:
        sd.rectangle([0, y, r * 2, y + gap], fill=(0, 0, 0, 0))
        # erase by drawing with the gradient colour is impossible here;
        # instead punch holes via mask below.
        y += gap + 14
        gap += 5
    # punch slats using a mask: redraw sun, then erase bars with alpha 0
    mask = Image.new("L", (r * 2, r * 2), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, r * 2, r * 2], fill=255)
    y = r + 10
    gap = 5
    while y < r * 2:
        md.rectangle([0, y, r * 2, y + gap], fill=0)
        y += gap + 13
        gap += 5
    sun.putalpha(mask)
    # recolour the sun with a vertical gradient (yellow -> orange)
    grad = vgrad((r * 2, r * 2), [(0, (255, 214, 107)), (1, (255, 110, 61))]).convert("RGBA")
    grad.putalpha(sun.split()[3])
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(grad, (cx - r, cy - r))
    return base


def _bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def _tapered_poly(pts, w0, w1):
    """Polygon around a polyline, tapering from width w0 to w1."""
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    return left + right[::-1]


def draw_palm(draw, base_x, base_y, top_x, top_y, lean, colour):
    """Flat stylised palm silhouette with tapered drooping fronds."""
    # trunk: gentle curve, tapering
    p0 = (base_x, base_y)
    p1 = (base_x + lean * 60, base_y - (base_y - top_y) * 0.55)
    p2 = (top_x, top_y)
    draw.polygon(_tapered_poly(_bezier(p0, p1, p2), 22, 10), fill=colour)
    cx, cy = top_x, top_y
    # fronds: fan out and droop, alternating lengths
    for k in range(7):
        ang = math.pi * (0.10 + 0.80 * k / 6)
        length = 165 - abs(k - 3) * 16
        tipx = cx + math.cos(ang) * length * lean
        tipy = cy + abs(math.sin(ang)) * length * 0.42 + 58
        midx = cx + math.cos(ang) * length * 0.55 * lean
        midy = cy - 34 + abs(math.sin(ang)) * length * 0.18
        draw.polygon(
            _tapered_poly(_bezier((cx, cy), (midx, midy), (tipx, tipy)), 15, 2),
            fill=colour,
        )
    # coconuts
    draw.ellipse([cx - 14, cy - 2, cx - 2, cy + 10], fill=colour)
    draw.ellipse([cx + 2, cy - 2, cx + 14, cy + 10], fill=colour)


def draw_tracked_bbox(draw, cx, y, text, fnt, fill, tracking=0):
    """Draw tracked text centred on cx, top at y; return (top, bottom)."""
    total = tracked_width(draw, text, fnt, tracking)
    x = cx - total / 2
    top, bottom = None, None
    for ch in text:
        bb = draw.textbbox((x, y), ch, font=fnt)
        top = bb[1] if top is None else min(top, bb[1])
        bottom = bb[3] if bottom is None else max(bottom, bb[3])
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return top, bottom


def main():
    # ---- sky ----
    sky = vgrad(
        (W, H),
        [
            (0.00, (22, 6, 46)),
            (0.30, (74, 18, 96)),
            (0.52, (164, 20, 122)),
            (0.72, (232, 62, 107)),
            (0.88, (255, 122, 61)),
            (1.00, (255, 196, 107)),
        ],
    ).convert("RGBA")
    img = sky

    # ---- sun behind the poster ----
    img.alpha_composite(draw_sun(ImageDraw.Draw(img), 600, 118, 112))

    d = ImageDraw.Draw(img)

    # ---- palms in the side margins, framing the poster ----
    draw_palm(d, 34, 1200, 78, 540, +1, (26, 11, 46, 255))
    draw_palm(d, 1166, 1200, 1122, 560, -1, (26, 11, 46, 255))

    # ---- continuous skyline along the bottom strip ----
    heights = [1135, 1165, 1125, 1155, 1140, 1170, 1130, 1160, 1128, 1158, 1145, 1172]
    step = W // len(heights)
    for i, htop in enumerate(heights):
        d.rectangle([i * step, htop, (i + 1) * step, 1200], fill=(26, 11, 46, 255))
    # a couple of antennae
    d.line([(3 * step + 20, heights[3]), (3 * step + 20, heights[3] - 42)], fill=(26, 11, 46, 255), width=5)
    d.line([(8 * step + 40, heights[8]), (8 * step + 40, heights[8] - 36)], fill=(26, 11, 46, 255), width=5)

    # ---- wanted poster card ----
    card = (130, 150, 1070, 1120)
    d.rounded_rectangle(card, radius=22, fill=PARCHMENT + (255,), outline=INK + (255,), width=8)
    d.rounded_rectangle((144, 164, 1056, 1106), radius=16, outline=INK + (255,), width=2)

    cx = 600
    # WANTED (measured, so nothing below it can overlap)
    f_wanted = font(ANTON, 172)
    _, wanted_bottom = draw_tracked_bbox(d, cx, 172, "WANTED", f_wanted, INK, tracking=10)
    # Leonida line
    f_small = font(INTER, 27)
    draw_tracked(d, cx, wanted_bottom + 16, "★ LEONIDA COUNTY ★", f_small, INK, tracking=6)

    # ---- the ghost (make.fun mascot, at its laptop) ----
    ghost = Image.open(HERE / "assets" / "ghost-laptop-recording.png").convert("RGBA")
    bbox = ghost.getbbox()
    ghost = ghost.crop(bbox)
    gw = 445
    gh = round(ghost.height * gw / ghost.width)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    img.alpha_composite(ghost, (cx - gw // 2, 430))

    # THE AGENT
    d = ImageDraw.Draw(img)
    f_agent = font(ANTON, 76)
    draw_tracked(d, cx, 806, "THE AGENT", f_agent, INK, tracking=6)

    # the charge
    f_body = font(INTER, 38)
    d.text((cx, 890), "GETTING PAID REAL MONEY", font=f_body, fill=INK, anchor="ma")
    d.text((cx, 936), "WHILE YOU WAIT FOR GTA 6", font=f_body, fill=INK, anchor="ma")

    # make.fun badge (magenta pill, mark + wordmark)
    badge = Image.open(HERE / "assets" / "makefun-badge.png").convert("RGBA")
    bw = 280
    bh = round(badge.height * bw / badge.width)
    badge = badge.resize((bw, bh), Image.LANCZOS)
    img.alpha_composite(badge, (cx - bw // 2, 988))

    img.convert("RGB").save(OUT, "PNG")
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
