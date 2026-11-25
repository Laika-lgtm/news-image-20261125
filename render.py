#!/usr/bin/env python3
"""Render the Wednesday 25 November 2026 world-news front page.

Reads stories.json (36 date-audited stories) and draws one 1024x1024
newspaper-style PNG with three illustrated heroes, a 10-card grid, a
dotted world map, a 23-item 'also on' strip, a day-in-numbers box and a
DATE CHECK footer. Deterministic: fixed fonts, no randomness, no network.
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
M = 22                      # outer margin
CW = W - 2 * M              # content width

PAPER = (247, 243, 234)
INK = (26, 26, 26)
MUTED = (110, 104, 92)
RED = (163, 22, 33)
RULE = (200, 192, 176)
PANEL = (255, 255, 255)
PANEL_EDGE = (214, 206, 190)

REGION_COLORS = {
    "ASIA-PACIFIC": (31, 122, 140),
    "EUROPE": (43, 94, 167),
    "MIDDLE EAST": (179, 64, 42),
    "AFRICA": (63, 125, 58),
    "AMERICAS": (107, 79, 161),
    "OCEANIA": (0, 120, 110),
    "WORLD": (85, 85, 85),
}
TAG_COLORS = {
    "REPORTED": (30, 107, 58),
    "ONGOING": (194, 87, 11),
    "AHEAD": (43, 94, 167),
    "CLAIM": (107, 79, 161),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    for base in (FONT_DIR, "/usr/share/fonts/truetype/noto"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(name)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "NotoSerif-Italic.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap text; if it overflows max_lines, shrink the font until it fits."""
    size = fnt.size
    while size > 8:
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return lines, fnt
        size -= 1
        fnt = font(os.path.basename(fnt.path), size)
    return wrap(draw, text, fnt, max_w)[:max_lines], fnt


def tag_chip(draw, x, y, label):
    """Draw a small filled certainty tag; returns its width."""
    fnt = font(SANS_B, 10)
    tw = draw.textlength(label, font=fnt)
    w = int(tw) + 12
    h = 15
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3,
                           fill=TAG_COLORS[label])
    draw.text((x + 6, y + 2), label, font=fnt, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- illustrations
def draw_selloff(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(22, 35, 63))
    for gy in range(y0 + 18, y1, 22):
        draw.line([(x0, gy), (x1, gy)], fill=(48, 64, 100), width=1)
    # candlesticks falling left to right
    tops = [0.30, 0.34, 0.42, 0.40, 0.52, 0.50, 0.62, 0.60, 0.72]
    bw = (x1 - x0) / len(tops)
    for i, t in enumerate(tops):
        cx = x0 + i * bw + bw / 2
        top = y0 + (y1 - y0) * t
        bot = top + 16
        col = (214, 48, 49) if i % 2 == 0 else (220, 90, 70)
        draw.line([(cx, top - 8), (cx, bot + 8)], fill=col, width=2)
        draw.rectangle([cx - 7, top, cx + 7, bot], fill=col)
    pts = []
    for i, t in enumerate(tops):
        pts.append((x0 + i * bw + bw / 2, y0 + (y1 - y0) * t))
    draw.line(pts, fill=(255, 214, 90), width=3, joint="curve")
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 214, 90))
    draw.text((x0 + 8, y0 + 6), "-6.2%", font=font(SANS_B, 22),
              fill=(255, 214, 90))
    # small closing-index table along the bottom (like the winning pages)
    f_tab = font(SANS_B, 10)
    draw.text((x0 + 8, y1 - 26), "KOSPI -6.2  ·  TAIEX -4.8  ·  NIKKEI -2.8",
              font=f_tab, fill=(255, 255, 255))
    draw.text((x0 + 8, y1 - 13), "HSI -1.1  ·  HYNIX -11.1  ·  SAMSUNG -9.9",
              font=f_tab, fill=(255, 214, 90))


def draw_breach(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(30, 34, 44))
    # server racks
    for r in range(3):
        rx = x0 + 14 + r * 62
        draw.rectangle([rx, y0 + 24, rx + 50, y1 - 8], fill=(52, 60, 76),
                       outline=(90, 100, 120))
        for s in range(3):
            sy = y0 + 34 + s * 26
            draw.rectangle([rx + 7, sy, rx + 43, sy + 14], fill=(38, 46, 60))
            draw.ellipse([rx + 11, sy + 4, rx + 17, sy + 10],
                         fill=(76, 200, 120) if s % 2 == 0 else (240, 170, 60))
            draw.line([(rx + 22, sy + 7), (rx + 38, sy + 7)],
                      fill=(120, 130, 150), width=2)
    # warning triangle
    cx, cy = x1 - 62, y0 + 62
    draw.polygon([(cx, cy - 34), (cx + 34, cy + 24), (cx - 34, cy + 24)],
                 fill=(214, 48, 49), outline=(255, 255, 255))
    draw.text((cx - 3, cy - 18), "!", font=font(SANS_B, 30), fill=(255, 255, 255))
    draw.text((x0 + 8, y0 + 6), "UNCLASSIFIED SYSTEMS",
              font=font(SANS_B, 11), fill=(200, 210, 225))


def draw_fire(draw, box):
    x0, y0, x1, y1 = box
    # sky bands
    bands = [(214, 90, 40), (226, 120, 50), (238, 160, 70), (244, 190, 100)]
    bh = (y1 - y0) // len(bands)
    for i, col in enumerate(bands):
        draw.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=col)
    # smoke (kept clear of the "10,130 ha" label at top-left)
    for sx, sy, sr in [(x0 + 80, y0 + 46, 24), (x0 + 140, y0 + 38, 30),
                       (x0 + 200, y0 + 48, 22)]:
        draw.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2],
                     fill=(120, 110, 105))
    # hills
    draw.polygon([(x0, y1), (x0, y1 - 46), (x0 + 90, y1 - 78),
                  (x0 + 180, y1 - 52), (x0 + 260, y1 - 66), (x1, y1 - 40),
                  (x1, y1)], fill=(74, 52, 36))
    draw.polygon([(x0, y1), (x0, y1 - 22), (x0 + 120, y1 - 40),
                  (x0 + 240, y1 - 18), (x1, y1 - 30), (x1, y1)],
                 fill=(48, 34, 24))
    # flames
    for fx, fh in [(x0 + 70, 34), (x0 + 130, 44), (x0 + 200, 36),
                   (x0 + 250, 28)]:
        fy = y1 - 20
        draw.polygon([(fx - 14, fy), (fx - 4, fy - fh), (fx + 2, fy - fh // 2),
                      (fx + 8, fy - fh - 8), (fx + 14, fy)],
                     fill=(255, 200, 60))
        draw.polygon([(fx - 8, fy), (fx - 2, fy - fh // 2),
                      (fx + 4, fy - fh // 2 - 6), (fx + 8, fy)],
                     fill=(255, 120, 30))
    draw.text((x0 + 8, y0 + 6), "10,130 ha", font=font(SANS_B, 22),
              fill=(255, 255, 255))


def draw_rocket(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(16, 22, 48))
    # stars
    for sx, sy, sr in [(0.08, 0.18, 2), (0.22, 0.10, 1), (0.38, 0.22, 2),
                       (0.55, 0.08, 1), (0.72, 0.16, 2), (0.88, 0.10, 1),
                       (0.93, 0.30, 2), (0.05, 0.42, 1)]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr,
                      x0 + w * sx + sr, y0 + h * sy + sr],
                     fill=(255, 255, 255))
    # launch pad + tower
    draw.rectangle([x0 + w * 0.06, y0 + h * 0.82, x0 + w * 0.94, y0 + h * 0.88],
                   fill=(70, 76, 92))
    draw.rectangle([x0 + w * 0.68, y0 + h * 0.30, x0 + w * 0.72, y0 + h * 0.82],
                   fill=(120, 126, 140))
    # rocket body
    rx0, rx1 = x0 + w * 0.44, x0 + w * 0.56
    draw.polygon([(rx0, y0 + h * 0.34), (x0 + w * 0.50, y0 + h * 0.14),
                  (rx1, y0 + h * 0.34)], fill=(214, 48, 49))
    draw.rectangle([rx0, y0 + h * 0.34, rx1, y0 + h * 0.72],
                   fill=(240, 240, 235))
    draw.rectangle([rx0, y0 + h * 0.44, rx1, y0 + h * 0.50],
                   fill=(214, 48, 49))
    # fins + flame
    draw.polygon([(rx0, y0 + h * 0.72), (rx0 - w * 0.04, y0 + h * 0.82),
                  (rx0, y0 + h * 0.80)], fill=(214, 48, 49))
    draw.polygon([(rx1, y0 + h * 0.72), (rx1 + w * 0.04, y0 + h * 0.82),
                  (rx1, y0 + h * 0.80)], fill=(214, 48, 49))
    draw.polygon([(x0 + w * 0.47, y0 + h * 0.72), (x0 + w * 0.50, y0 + h * 0.98),
                  (x0 + w * 0.53, y0 + h * 0.72)], fill=(255, 190, 60))
    draw.text((x0 + 8, y0 + 6), "00:18 UTC", font=font(SANS_B, 20),
              fill=(255, 255, 255))


def draw_hospital(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(214, 206, 188))
    # sky + ground
    draw.rectangle([x0, y0, x1, y0 + h * 0.62], fill=(168, 196, 214))
    draw.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(120, 110, 96))
    # hospital building
    bx0, bx1 = x0 + w * 0.08, x0 + w * 0.58
    draw.rectangle([bx0, y0 + h * 0.24, bx1, y0 + h * 0.82],
                   fill=(245, 242, 234))
    draw.rectangle([bx0, y0 + h * 0.24, bx1, y0 + h * 0.30],
                   fill=(163, 22, 33))
    for r in range(2):
        for c in range(4):
            draw.rectangle([bx0 + w * 0.03 + c * w * 0.115,
                            y0 + h * (0.38 + r * 0.18),
                            bx0 + w * 0.10 + c * w * 0.115,
                            y0 + h * (0.50 + r * 0.18)],
                           fill=(90, 120, 150))
    # red cross sign
    cx, cy = x0 + w * 0.66, y0 + h * 0.30
    draw.rectangle([cx - 4, cy - 14, cx + 4, cy + 14], fill=(214, 48, 49))
    draw.rectangle([cx - 14, cy - 4, cx + 14, cy + 4], fill=(214, 48, 49))
    # ambulance
    ax0 = x0 + w * 0.62
    draw.rectangle([ax0, y0 + h * 0.62, ax0 + w * 0.30, y0 + h * 0.80],
                   fill=(255, 255, 255))
    draw.rectangle([ax0 + w * 0.22, y0 + h * 0.55, ax0 + w * 0.30,
                    y0 + h * 0.80], fill=(240, 240, 235))
    draw.rectangle([ax0 + w * 0.10, y0 + h * 0.67, ax0 + w * 0.16,
                    y0 + h * 0.73], fill=(214, 48, 49))
    for wx in (0.05, 0.24):
        draw.ellipse([ax0 + w * wx, y0 + h * 0.80, ax0 + w * (wx + 0.05),
                      y0 + h * 0.88], fill=(26, 26, 26))
    draw.text((x0 + 8, y0 + 6), "SHELTERED 3 DAYS", font=font(SANS_B, 11),
              fill=(26, 26, 26))


def draw_tankers(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # dusk sky bands over a dark strait
    bands = [(58, 32, 54), (122, 54, 44), (198, 96, 44), (238, 150, 70)]
    bh = h // len(bands)
    for i, col in enumerate(bands):
        draw.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=col)
    # low sun
    draw.ellipse([x0 + w * 0.68, y0 + h * 0.30, x0 + w * 0.80, y0 + h * 0.48],
                 fill=(255, 220, 140))
    # sea
    draw.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(24, 38, 62))
    for wy in (0.70, 0.80, 0.90):
        draw.line([(x0 + 6, y0 + h * wy), (x1 - 6, y0 + h * wy)],
                  fill=(52, 74, 106), width=1)
    # two burning tankers (hulls low in the frame, flames + smoke above)
    for sx, sw in [(0.06, 0.40), (0.52, 0.38)]:
        hx0, hx1 = x0 + w * sx, x0 + w * (sx + sw)
        hy = y0 + h * 0.66
        draw.rectangle([hx0, hy, hx1, hy + h * 0.12], fill=(32, 32, 36))
        draw.rectangle([hx0 + w * 0.05, hy - h * 0.07, hx0 + w * 0.12,
                        hy], fill=(200, 200, 190))
        # deck containers
        for cx in (0.16, 0.24, 0.32):
            draw.rectangle([hx0 + w * cx, hy - h * 0.06,
                            hx0 + w * (cx + 0.06), hy], fill=(150, 60, 50))
        # flame plume + smoke column
        fx = (hx0 + hx1) / 2
        for fxi, fh in [(fx - 14, 30), (fx, 42), (fx + 14, 28)]:
            draw.polygon([(fxi - 10, hy), (fxi - 3, hy - fh),
                          (fxi + 2, hy - fh // 2), (fxi + 6, hy - fh - 6),
                          (fxi + 10, hy)], fill=(255, 190, 60))
            draw.polygon([(fxi - 5, hy), (fxi, hy - fh // 2),
                          (fxi + 5, hy)], fill=(255, 110, 30))
        for sxi, syi, sr in [(fx - 8, hy - 52, 12), (fx + 4, hy - 66, 15),
                             (fx + 12, hy - 80, 10)]:
            draw.ellipse([sxi - sr, syi - sr // 2, sxi + sr, syi + sr // 2],
                         fill=(70, 66, 62))
    # floating mine markers (spiked circles) between the ships
    for mx, my in [(0.47, 0.78), (0.44, 0.88)]:
        cx, cy = x0 + w * mx, y0 + h * my
        for ang in range(0, 360, 45):
            import math as _m
            x2 = cx + 8 * _m.cos(_m.radians(ang))
            y2 = cy + 8 * _m.sin(_m.radians(ang))
            draw.line([(cx, cy), (x2, y2)], fill=(200, 200, 190), width=2)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(40, 40, 44),
                     outline=(200, 200, 190))
    draw.text((x0 + 8, y0 + 6), "BRENT $91.08", font=font(SANS_B, 16),
              fill=(255, 255, 255))


ART = {"selloff": draw_selloff, "breach": draw_breach, "fire": draw_fire,
       "rocket": draw_rocket, "tankers": draw_tankers}

# ---------------------------------------------------------------- small scenes
# Compact illustrations for the 2x5 card grid (boxes ~189x52). Every
# function draws only inside its box, using fractions of the box size.
def _frac(box):
    x0, y0, x1, y1 = box
    return x0, y0, x1, y1, x1 - x0, y1 - y0


def draw_cricket(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(18, 28, 66))
    for sx, sy in [(0.08, 0.2), (0.3, 0.12), (0.85, 0.18), (0.95, 0.35)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=(255, 255, 255))
    # floodlight pole + pitch
    draw.line([(x0 + w * 0.92, y0 + h * 0.05), (x0 + w * 0.92, y0 + h * 0.42)],
              fill=(120, 126, 140), width=2)
    draw.ellipse([x0 + w * 0.89, y0 + h * 0.02, x0 + w * 0.95, y0 + h * 0.14],
                 fill=(255, 240, 180))
    draw.rectangle([x0, y0 + h * 0.72, x1, y1], fill=(46, 125, 62))
    draw.rectangle([x0 + w * 0.30, y0 + h * 0.72, x0 + w * 0.62, y1],
                   fill=(196, 164, 110))
    # stumps
    for i in range(3):
        sx = x0 + w * (0.66 + i * 0.03)
        draw.line([(sx, y0 + h * 0.52), (sx, y0 + h * 0.74)],
                  fill=(255, 220, 130), width=2)
    # batsman silhouette
    bx, by = x0 + w * 0.42, y0 + h * 0.60
    draw.ellipse([bx - 4, by - 16, bx + 4, by - 8], fill=(20, 20, 20))
    draw.line([(bx, by - 8), (bx + 2, by + 8)], fill=(20, 20, 20), width=3)
    draw.line([(bx + 2, by + 8), (bx - 6, by + 16)], fill=(20, 20, 20), width=2)
    draw.line([(bx + 2, by + 8), (bx + 8, by + 16)], fill=(20, 20, 20), width=2)
    draw.line([(bx, by - 4), (bx + 14, by - 14)], fill=(150, 100, 50), width=3)
    # ball trail
    for i, t in enumerate([0.0, 0.25, 0.5, 0.75]):
        draw.ellipse([x0 + w * (0.55 + t * 0.3) - 2, y0 + h * (0.30 - t * 0.12) - 2,
                      x0 + w * (0.55 + t * 0.3) + 2, y0 + h * (0.30 - t * 0.12) + 2],
                     fill=(255, 255, 255))


def draw_breach_small(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(30, 34, 44))
    for r in range(3):
        rx = x0 + w * (0.06 + r * 0.30)
        draw.rectangle([rx, y0 + h * 0.14, rx + w * 0.24, y0 + h * 0.92],
                       fill=(52, 60, 76), outline=(90, 100, 120))
        for s in range(2):
            sy = y0 + h * (0.26 + s * 0.32)
            draw.ellipse([rx + 4, sy, rx + 10, sy + 6],
                         fill=(76, 200, 120) if s == 0 else (240, 170, 60))
            draw.line([(rx + 14, sy + 3), (rx + w * 0.20, sy + 3)],
                      fill=(120, 130, 150), width=2)
    cx, cy = x0 + w * 0.90, y0 + h * 0.42
    draw.polygon([(cx, cy - 12), (cx + 12, cy + 9), (cx - 12, cy + 9)],
                 fill=(214, 48, 49))
    draw.text((cx - 2, cy - 8), "!", font=font(SANS_B, 13),
              fill=(255, 255, 255))


def draw_leak(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(38, 38, 44))
    # stacked documents
    for i, dx in enumerate([0.06, 0.16, 0.26]):
        px = x0 + w * dx
        draw.rectangle([px, y0 + h * (0.16 + i * 0.06),
                        px + w * 0.30, y0 + h * (0.88 - i * 0.04)],
                       fill=(235, 232, 222))
        for li in range(3):
            ly = y0 + h * (0.30 + i * 0.06 + li * 0.16)
            draw.line([(px + 6, ly), (px + w * 0.30 - 6, ly)],
                      fill=(120, 116, 104), width=2)
    # red bar chart of the toll
    for i, bh in enumerate([0.30, 0.45, 0.62, 0.80]):
        bx = x0 + w * (0.62 + i * 0.09)
        draw.rectangle([bx, y0 + h * (0.92 - bh), bx + w * 0.06, y0 + h * 0.92],
                       fill=(214, 48, 49))


def draw_pact(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(140, 190, 210))
    draw.rectangle([x0, y0 + h * 0.58, x1, y1], fill=(40, 110, 150))
    # island
    draw.polygon([(x0 + w * 0.30, y0 + h * 0.62), (x0 + w * 0.50, y0 + h * 0.34),
                  (x0 + w * 0.70, y0 + h * 0.62)], fill=(63, 125, 58))
    # two flags
    for fx, col in [(0.18, (31, 58, 138)), (0.78, (0, 120, 90))]:
        draw.line([(x0 + w * fx, y0 + h * 0.30), (x0 + w * fx, y0 + h * 0.62)],
                  fill=(60, 58, 52), width=2)
        draw.polygon([(x0 + w * fx, y0 + h * 0.30),
                      (x0 + w * (fx + 0.13), y0 + h * 0.38),
                      (x0 + w * fx, y0 + h * 0.46)], fill=col)
        draw.ellipse([x0 + w * (fx + 0.04) - 1, y0 + h * 0.35 - 1,
                      x0 + w * (fx + 0.04) + 1, y0 + h * 0.35 + 1],
                     fill=(255, 255, 255))
    draw.ellipse([x0 + w * 0.86, y0 + h * 0.10, x0 + w * 0.94, y0 + h * 0.26],
                 fill=(255, 220, 120))


def draw_apology(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(52, 74, 110))
    # parliament building
    draw.polygon([(x0 + w * 0.30, y0 + h * 0.30), (x0 + w * 0.50, y0 + h * 0.12),
                  (x0 + w * 0.70, y0 + h * 0.30)], fill=(235, 232, 222))
    draw.rectangle([x0 + w * 0.30, y0 + h * 0.30, x0 + w * 0.70, y0 + h * 0.88],
                   fill=(225, 222, 210))
    for i in range(4):
        cx = x0 + w * (0.36 + i * 0.10)
        draw.rectangle([cx - 3, y0 + h * 0.36, cx + 3, y0 + h * 0.82],
                       fill=(120, 116, 104))
    # flag
    draw.rectangle([x0 + w * 0.78, y0 + h * 0.18, x0 + w * 0.94, y0 + h * 0.44],
                   fill=(31, 58, 138))
    for sx, sy in [(0.82, 0.24), (0.88, 0.34), (0.92, 0.26)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=(255, 255, 255))
    draw.line([(x0 + w * 0.86, y0 + h * 0.18), (x0 + w * 0.86, y0 + h * 0.88)],
              fill=(60, 58, 52), width=2)


def draw_skyline(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(64, 48, 78))
    draw.ellipse([x0 + w * 0.84, y0 + h * 0.08, x0 + w * 0.94, y0 + h * 0.28],
                 fill=(255, 220, 120))
    for bx, bw, bh, col in [(0.06, 0.18, 0.55, (40, 40, 52)),
                            (0.28, 0.22, 0.80, (30, 30, 42)),
                            (0.54, 0.16, 0.62, (40, 40, 52)),
                            (0.74, 0.20, 0.72, (30, 30, 42))]:
        draw.rectangle([x0 + w * bx, y0 + h * (0.95 - bh),
                        x0 + w * (bx + bw), y0 + h * 0.95], fill=col)
        for wy in (0.30, 0.50, 0.70):
            draw.rectangle([x0 + w * (bx + 0.04), y0 + h * (0.95 - bh + wy * bh),
                            x0 + w * (bx + bw - 0.04),
                            y0 + h * (0.95 - bh + wy * bh) + 3],
                           fill=(255, 200, 90))
    draw.ellipse([x0 + w * 0.60, y0 + h * 0.55, x0 + w * 0.68, y0 + h * 0.71],
                 fill=(214, 48, 49))


def draw_heat(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(244, 190, 100))
    # sun
    cx, cy = x0 + w * 0.24, y0 + h * 0.50
    for ang in range(0, 360, 45):
        import math as _m
        x2 = cx + 26 * _m.cos(_m.radians(ang))
        y2 = cy + 26 * _m.sin(_m.radians(ang))
        draw.line([(cx, cy), (x2, y2)], fill=(226, 120, 50), width=3)
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(226, 90, 40))
    # thermometer
    tx = x0 + w * 0.68
    draw.rounded_rectangle([tx - 5, y0 + h * 0.14, tx + 5, y0 + h * 0.78],
                           radius=5, fill=(255, 255, 255),
                           outline=(163, 22, 33))
    draw.ellipse([tx - 10, y0 + h * 0.72, tx + 10, y0 + h * 0.94],
                 fill=(214, 48, 49))
    draw.rectangle([tx - 2, y0 + h * 0.30, tx + 2, y0 + h * 0.78],
                   fill=(214, 48, 49))
    draw.text((x0 + w * 0.82, y0 + h * 0.10), "35°C", font=font(SANS_B, 11),
              fill=(163, 22, 33))


def draw_court(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(58, 66, 84))
    draw.polygon([(x0 + w * 0.26, y0 + h * 0.34), (x0 + w * 0.50, y0 + h * 0.12),
                  (x0 + w * 0.74, y0 + h * 0.34)], fill=(200, 194, 178))
    draw.rectangle([x0 + w * 0.26, y0 + h * 0.34, x0 + w * 0.74, y0 + h * 0.88],
                   fill=(225, 222, 210))
    for i in range(4):
        cx = x0 + w * (0.32 + i * 0.12)
        draw.rectangle([cx - 3, y0 + h * 0.40, cx + 3, y0 + h * 0.82],
                       fill=(120, 116, 104))
    draw.rectangle([x0 + w * 0.20, y0 + h * 0.88, x0 + w * 0.80, y0 + h * 0.95],
                   fill=(120, 116, 104))
    # gavel
    draw.line([(x0 + w * 0.84, y0 + h * 0.55), (x0 + w * 0.96, y0 + h * 0.35)],
              fill=(150, 100, 50), width=3)
    draw.rectangle([x0 + w * 0.82, y0 + h * 0.30, x0 + w * 0.94, y0 + h * 0.42],
                   fill=(90, 60, 30))


def draw_fire_small(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    bands = [(214, 90, 40), (226, 120, 50), (238, 160, 70)]
    bh = h / len(bands)
    for i, col in enumerate(bands):
        draw.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=col)
    draw.polygon([(x0, y1), (x0, y0 + h * 0.62), (x0 + w * 0.45, y0 + h * 0.42),
                  (x0 + w * 0.75, y0 + h * 0.58), (x1, y0 + h * 0.48), (x1, y1)],
                 fill=(74, 52, 36))
    for fx, fh in [(0.22, 0.30), (0.45, 0.42), (0.68, 0.34), (0.86, 0.26)]:
        px = x0 + w * fx
        fy = y1 - 4
        draw.polygon([(px - 8, fy), (px - 2, fy - h * fh), (px + 8, fy)],
                     fill=(255, 200, 60))
        draw.polygon([(px - 4, fy), (px, fy - h * fh * 0.6), (px + 4, fy)],
                     fill=(255, 120, 30))


def draw_ships(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(24, 42, 72))
    for sx, sy in [(0.1, 0.15), (0.4, 0.1), (0.7, 0.2), (0.9, 0.12)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=(255, 255, 255))
    draw.rectangle([x0, y0 + h * 0.60, x1, y1], fill=(16, 60, 100))
    # cargo ship
    draw.rectangle([x0 + w * 0.10, y0 + h * 0.52, x0 + w * 0.52, y0 + h * 0.66],
                   fill=(60, 60, 66))
    draw.rectangle([x0 + w * 0.16, y0 + h * 0.42, x0 + w * 0.24, y0 + h * 0.52],
                   fill=(200, 200, 190))
    for cx in (0.14, 0.26, 0.38):
        draw.rectangle([x0 + w * cx, y0 + h * 0.44, x0 + w * (cx + 0.08),
                        y0 + h * 0.52], fill=(214, 48, 49))
    # explosion burst
    ex, ey = x0 + w * 0.78, y0 + h * 0.44
    for ang in range(0, 360, 30):
        import math as _m
        x2 = ex + 16 * _m.cos(_m.radians(ang))
        y2 = ey + 16 * _m.sin(_m.radians(ang))
        draw.line([(ex, ey), (x2, y2)], fill=(255, 190, 60), width=3)
    draw.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(255, 220, 120))


def draw_port(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(64, 84, 110))
    draw.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(22, 52, 84))
    # pier + containers
    draw.rectangle([x0, y0 + h * 0.58, x1, y0 + h * 0.66], fill=(90, 86, 76))
    for i, col in enumerate([(214, 48, 49), (240, 170, 60), (31, 122, 140)]):
        cx = x0 + w * (0.10 + i * 0.20)
        draw.rectangle([cx, y0 + h * 0.38, cx + w * 0.16, y0 + h * 0.58],
                       fill=col)
    # crane
    draw.line([(x0 + w * 0.72, y0 + h * 0.10), (x0 + w * 0.72, y0 + h * 0.62)],
              fill=(220, 220, 210), width=3)
    draw.line([(x0 + w * 0.72, y0 + h * 0.10), (x0 + w * 0.95, y0 + h * 0.22)],
              fill=(220, 220, 210), width=2)
    # smoke plume + jet silhouette
    for sx, sy, sr in [(0.24, 0.22, 10), (0.30, 0.12, 13), (0.38, 0.20, 9)]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr // 2,
                      x0 + w * sx + sr, y0 + h * sy + sr // 2],
                     fill=(120, 116, 110))
    draw.polygon([(x0 + w * 0.86, y0 + h * 0.30), (x0 + w * 0.97, y0 + h * 0.34),
                  (x0 + w * 0.86, y0 + h * 0.38)], fill=(30, 30, 34))


def draw_garment(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(18, 90, 96))
    # fabric rolls on the wall
    for i, col in enumerate([(214, 48, 90), (255, 214, 90), (90, 200, 170),
                             (240, 240, 235)]):
        rx = x0 + w * (0.06 + i * 0.12)
        draw.rectangle([rx, y0 + h * 0.10, rx + w * 0.08, y0 + h * 0.42],
                       fill=col)
    # sewing machine silhouettes on a table
    draw.rectangle([x0, y0 + h * 0.72, x1, y0 + h * 0.80], fill=(120, 90, 60))
    for mx in (0.30, 0.62):
        bx = x0 + w * mx
        draw.rectangle([bx, y0 + h * 0.44, bx + w * 0.20, y0 + h * 0.52],
                       fill=(40, 40, 44))
        draw.rectangle([bx + w * 0.16, y0 + h * 0.52, bx + w * 0.20,
                        y0 + h * 0.72], fill=(40, 40, 44))
        draw.ellipse([bx + w * 0.02, y0 + h * 0.52, bx + w * 0.08,
                      y0 + h * 0.64], fill=(200, 200, 190))
    draw.text((x0 + w * 0.80, y0 + h * 0.08), "+36%", font=font(SANS_B, 13),
              fill=(255, 255, 255))


def draw_mine(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(38, 28, 22))
    # tunnel mouth
    draw.pieslice([x0 + w * 0.30, y0 + h * 0.10, x0 + w * 0.70, y0 + h * 1.30],
                  180, 360, fill=(12, 10, 8))
    draw.arc([x0 + w * 0.30, y0 + h * 0.10, x0 + w * 0.70, y0 + h * 1.30],
             180, 360, fill=(150, 120, 80), width=2)
    # headlamp glows inside the dark
    for lx, ly in [(0.42, 0.45), (0.52, 0.60), (0.60, 0.42)]:
        cx, cy = x0 + w * lx, y0 + h * ly
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 220, 120))
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    # rescue cage + cable
    draw.line([(x0 + w * 0.86, y0), (x0 + w * 0.86, y0 + h * 0.55)],
              fill=(180, 180, 170), width=2)
    draw.rectangle([x0 + w * 0.80, y0 + h * 0.55, x0 + w * 0.92, y0 + h * 0.78],
                   outline=(255, 220, 120), width=2)


def draw_refinery(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(16, 18, 34))
    for sx, sy in [(0.08, 0.12), (0.35, 0.08), (0.9, 0.15)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=(255, 255, 255))
    # distillation towers
    for tx, th in [(0.14, 0.55), (0.38, 0.72), (0.60, 0.60)]:
        bx = x0 + w * tx
        draw.rectangle([bx, y0 + h * (0.95 - th), bx + w * 0.10, y0 + h * 0.95],
                       fill=(70, 74, 88))
        draw.rectangle([bx - 2, y0 + h * (0.95 - th) - 4, bx + w * 0.10 + 2,
                        y0 + h * (0.95 - th)], fill=(120, 126, 140))
    # flames on two stacks + smoke
    for fx, fh in [(0.43, 0.30), (0.65, 0.38)]:
        px = x0 + w * fx
        fy = y0 + h * 0.32
        draw.polygon([(px - 8, fy), (px - 2, fy - h * fh), (px + 8, fy)],
                     fill=(255, 200, 60))
        draw.polygon([(px - 4, fy), (px, fy - h * fh * 0.6), (px + 4, fy)],
                     fill=(255, 120, 30))
    for sx, sy, sr in [(0.44, 0.12, 9), (0.50, 0.06, 11), (0.66, 0.10, 8)]:
        draw.ellipse([x0 + w * sx - sr, y0 + h * sy - sr // 2,
                      x0 + w * sx + sr, y0 + h * sy + sr // 2],
                     fill=(90, 86, 80))


def draw_energy(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(43, 94, 167))
    # house silhouette
    draw.polygon([(x0 + w * 0.10, y0 + h * 0.52), (x0 + w * 0.30, y0 + h * 0.30),
                  (x0 + w * 0.50, y0 + h * 0.52)], fill=(235, 232, 222))
    draw.rectangle([x0 + w * 0.12, y0 + h * 0.52, x0 + w * 0.48, y0 + h * 0.88],
                   fill=(225, 222, 210))
    draw.rectangle([x0 + w * 0.26, y0 + h * 0.62, x0 + w * 0.34, y0 + h * 0.88],
                   fill=(90, 60, 30))
    # bill with the new cap figure
    draw.rectangle([x0 + w * 0.58, y0 + h * 0.16, x0 + w * 0.94, y0 + h * 0.84],
                   fill=(255, 255, 255))
    draw.text((x0 + w * 0.62, y0 + h * 0.24), "£2,166",
              font=font(SANS_B, 13), fill=(163, 22, 33))
    for li in range(3):
        ly = y0 + h * (0.52 + li * 0.12)
        draw.line([(x0 + w * 0.62, ly), (x0 + w * 0.90, ly)],
                  fill=(180, 176, 164), width=2)
    # lightning bolt
    draw.polygon([(x0 + w * 0.56, y0 + h * 0.10), (x0 + w * 0.50, y0 + h * 0.34),
                  (x0 + w * 0.56, y0 + h * 0.34), (x0 + w * 0.52, y0 + h * 0.52),
                  (x0 + w * 0.62, y0 + h * 0.28), (x0 + w * 0.56, y0 + h * 0.28)],
                 fill=(255, 214, 90))


def draw_market(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(30, 34, 44))
    # supermarket facade
    draw.rectangle([x0 + w * 0.06, y0 + h * 0.30, x0 + w * 0.72, y0 + h * 0.88],
                   fill=(240, 200, 60))
    draw.rectangle([x0 + w * 0.06, y0 + h * 0.30, x0 + w * 0.72, y0 + h * 0.44],
                   fill=(31, 58, 138))
    draw.text((x0 + w * 0.10, y0 + h * 0.32), "SUPER",
              font=font(SANS_B, 10), fill=(255, 255, 255))
    for i in range(3):
        wx = x0 + w * (0.12 + i * 0.20)
        draw.rectangle([wx, y0 + h * 0.52, wx + w * 0.14, y0 + h * 0.80],
                       fill=(90, 120, 150))
    # police tape + light bar
    draw.rectangle([x0, y0 + h * 0.86, x1, y0 + h * 0.94], fill=(255, 214, 90))
    for tx in range(0, int(w), 14):
        draw.line([(x0 + tx, y0 + h * 0.94), (x0 + tx + 7, y0 + h * 0.86)],
                  fill=(26, 26, 26), width=2)
    draw.rectangle([x0 + w * 0.80, y0 + h * 0.55, x0 + w * 0.86, y0 + h * 0.60],
                   fill=(214, 48, 49))
    draw.rectangle([x0 + w * 0.88, y0 + h * 0.55, x0 + w * 0.94, y0 + h * 0.60],
                   fill=(43, 94, 167))


def draw_women(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(74, 32, 86))
    # bar chart of the toll
    for i, bh in enumerate([0.30, 0.42, 0.55, 0.72]):
        bx = x0 + w * (0.10 + i * 0.16)
        draw.rectangle([bx, y0 + h * (0.92 - bh), bx + w * 0.11,
                        y0 + h * 0.92], fill=(214, 120, 200))
    # three figures holding hands
    for fx in (0.74, 0.82, 0.90):
        cx, cy = x0 + w * fx, y0 + h * 0.55
        draw.ellipse([cx - 4, cy - 16, cx + 4, cy - 8], fill=(255, 220, 190))
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(255, 220, 190), width=3)
        draw.line([(cx, cy + 8), (cx - 5, cy + 16)], fill=(255, 220, 190),
                  width=2)
        draw.line([(cx, cy + 8), (cx + 5, cy + 16)], fill=(255, 220, 190),
                  width=2)
    draw.text((x0 + w * 0.08, y0 + h * 0.06), "47,000",
              font=font(SANS_B, 13), fill=(255, 255, 255))


def draw_met(draw, box):
    x0, y0, x1, y1, w, h = _frac(box)
    draw.rectangle(box, fill=(24, 42, 72))
    # skyline
    for bx, bw, bh in [(0.06, 0.14, 0.45), (0.24, 0.18, 0.65),
                       (0.46, 0.12, 0.50)]:
        draw.rectangle([x0 + w * bx, y0 + h * (0.95 - bh),
                        x0 + w * (bx + bw), y0 + h * 0.95], fill=(52, 64, 92))
        for wy in (0.30, 0.60):
            draw.rectangle([x0 + w * (bx + 0.03),
                            y0 + h * (0.95 - bh + wy * bh),
                            x0 + w * (bx + bw - 0.03),
                            y0 + h * (0.95 - bh + wy * bh) + 3],
                           fill=(255, 200, 90))
    # police badge shield
    cx, cy = x0 + w * 0.80, y0 + h * 0.48
    draw.polygon([(cx - 14, cy - 16), (cx + 14, cy - 16), (cx + 12, cy + 4),
                  (cx, cy + 18), (cx - 12, cy + 4)], fill=(255, 214, 90),
                 outline=(255, 255, 255))
    draw.text((cx - 7, cy - 10), "MET", font=font(SANS_B, 10),
              fill=(26, 26, 26))


ART_SMALL = {"port": draw_port, "garment": draw_garment,
             "mine": draw_mine, "refinery": draw_refinery,
             "energy": draw_energy, "market": draw_market,
             "women": draw_women, "met": draw_met,
             "pact": draw_pact, "apology": draw_apology}

# ---------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-65, 60), (-55, 47), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 24),
     (-115, 30), (-120, 34), (-125, 40), (-125, 48), (-135, 58),
     (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
     (-30, 76), (-45, 76), (-58, 70), (-58, 64)],
    [(-80, 10), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-52, -33), (-58, -38),
     (-65, -42), (-68, -50), (-70, -54), (-73, -50), (-73, -40),
     (-72, -30), (-70, -18), (-77, -12), (-81, -6), (-80, 2)],
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (48, 11), (51, 10), (44, 0), (40, -10),
     (35, -18), (32, -26), (28, -33), (20, -35), (15, -30), (12, -18),
     (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68),
     (55, 69), (70, 72), (90, 75), (110, 76), (130, 72), (150, 70),
     (170, 66), (178, 65), (170, 60), (162, 56), (158, 52), (142, 50),
     (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
     (115, 23), (108, 18), (105, 10), (100, 8), (98, 12), (95, 16),
     (92, 21), (88, 22), (80, 15), (77, 8), (73, 16), (66, 25), (60, 25),
     (57, 26), (52, 26), (48, 29), (44, 29), (40, 32), (36, 36), (30, 36),
     (26, 38), (22, 37), (18, 40), (12, 44), (8, 44), (3, 43), (-2, 37),
     (-6, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (136, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -9),
     (125, -9), (130, -3), (135, -2), (140, -4), (141, -8)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (140, 36), (141, 39),
     (141, 42), (143, 44), (145, 44), (142, 42), (140, 38), (138, 35),
     (135, 33), (131, 32)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (174, -41), (171, -43), (168, -46)],
]


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                inside = not inside
        j = i
    return inside


def draw_map(draw, box, pins):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 236, 226))
    mw, mh = x1 - x0, y1 - y0
    # dotted continents
    step_lon, step_lat = 4.0, 3.2
    lon = -170.0
    while lon <= 180:
        lat = -56.0
        while lat <= 76:
            if any(point_in_poly(lon, lat, p) for p in CONTINENTS):
                px = x0 + (lon + 170) / 350 * mw
                py = y0 + (76 - lat) / 132 * mh
                draw.ellipse([px - 1.4, py - 1.4, px + 1.4, py + 1.4],
                             fill=(140, 150, 128))
            lat += step_lat
        lon += step_lon
    # numbered pins
    for num, (plon, plat) in pins:
        px = x0 + (plon + 170) / 350 * mw
        py = y0 + (76 - plat) / 132 * mh
        r = 10
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        fnt = font(SANS_B, 11)
        tw = draw.textlength(str(num), font=fnt)
        draw.text((px - tw / 2, py - 7), str(num), font=fnt,
                  fill=(255, 255, 255))


# ---------------------------------------------------------------- page
def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    heroes = data["heroes"]
    cards = data["cards"]
    also = data["also_on"]

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top strip
    y = 10
    f_top = font(SANS_B, 12)
    d.text((M, y), "THE WORLD IN ONE DAY", font=f_top, fill=INK)
    mid = "36 STORIES  ·  7 REGIONS  ·  ONE DAY"
    d.text((W / 2 - d.textlength(mid, font=f_top) / 2, y), mid,
           font=f_top, fill=RED)
    right = "WEDNESDAY 25 NOVEMBER 2026"
    d.text((W - M - d.textlength(right, font=f_top), y), right,
           font=f_top, fill=INK)
    d.line([(M, 30), (W - M, 30)], fill=RULE, width=1)

    # ---- masthead
    f_mast = font(SERIF_B, 52)
    title = data["masthead"]
    d.text((W / 2 - d.textlength(title, font=f_mast) / 2, 34), title,
           font=f_mast, fill=INK)
    f_sub = font(SERIF_I, 17)
    sub = data["subhead"]
    d.text((W / 2 - d.textlength(sub, font=f_sub) / 2, 96), sub,
           font=f_sub, fill=RED)

    # ---- numbers strip (under the masthead, like the winning front pages)
    y = 116
    f_num = font(SERIF_B, 22)
    f_lab = font(SANS, 9)
    col_w = CW // 6
    for i, (val, label) in enumerate(data["numbers"]):
        nx = M + i * col_w
        d.text((nx, y), val, font=f_num, fill=RED)
        for li, ln in enumerate(wrap(d, label, f_lab, col_w - 12)):
            d.text((nx, y + 26 + li * 11), ln, font=f_lab,
                   fill=(60, 58, 52))
        if i:
            d.line([(nx - 6, y + 2), (nx - 6, y + 46)], fill=RULE, width=1)
    d.line([(M, 168), (W - M, 168)], fill=RULE, width=1)

    # ---- region bar
    y = 174
    x = M
    f_reg = font(SANS_B, 11)
    for name, count in data["regions"]:
        label = f"{name} {count}"
        w = int(d.textlength(label, font=f_reg)) + 16
        d.rounded_rectangle([x, y, x + w, y + 20], radius=3,
                            fill=REGION_COLORS[name])
        d.text((x + 8, y + 4), label, font=f_reg, fill=(255, 255, 255))
        x += w + 6
    d.line([(M, 200), (W - M, 200)], fill=RULE, width=1)

    # ---- UTC timeline strip
    y = 206
    f_tl = font(SANS, 11)
    f_tlb = font(SANS_B, 11)
    x = M
    for t, label in data["timeline"]:
        d.text((x, y), t, font=f_tlb, fill=RED)
        x += d.textlength(t, font=f_tlb) + 5
        d.text((x, y), label, font=f_tl, fill=INK)
        x += d.textlength(label, font=f_tl) + 10
    d.line([(M, 222), (W - M, 222)], fill=RULE, width=1)

    # ---- heroes
    hy, hh = 230, 264
    hw = (CW - 20) // 3
    for i, hero in enumerate(heroes):
        hx = M + i * (hw + 10)
        col = REGION_COLORS[hero["region"]]
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=PANEL,
                    outline=PANEL_EDGE)
        d.rectangle([hx, hy, hx + hw, hy + 4], fill=col)
        ART[hero["art"]](d, (hx + 1, hy + 5, hx + hw - 1, hy + 112))
        d.text((hx + 10, hy + 114), str(hero["n"]), font=font(SERIF_B, 18),
               fill=col)
        # kicker
        f_kick = font(SANS_B, 10)
        d.text((hx + 10, hy + 138), hero["kicker"], font=f_kick, fill=col)
        # headline (max 2 lines)
        lines, f_head = fit_lines(d, hero["headline"], font(SERIF_B, 20),
                                  hw - 20, 2)
        ly = hy + 154
        for ln in lines:
            d.text((hx + 10, ly), ln, font=f_head, fill=INK)
            ly += f_head.size + 2
        # deck (max 2 lines)
        f_deck = font(SANS, 12)
        dlines = wrap(d, hero["deck"], f_deck, hw - 20)
        ly = hy + 202
        for ln in dlines[:2]:
            d.text((hx + 10, ly), ln, font=f_deck, fill=(60, 58, 52))
            ly += 15
        # tag + source at bottom
        by = hy + hh - 22
        tw = tag_chip(d, hx + 10, by, hero["tag"])
        d.text((hx + 14 + tw, by + 2), hero["source"], font=font(SANS, 10),
               fill=MUTED)

    # ---- 10-card grid, every card illustrated (2 rows x 5)
    gy = hy + hh + 8
    cw = (CW - 32) // 5
    ch, gap = 140, 8
    for i, card in enumerate(cards):
        r, c = divmod(i, 5)
        cx = M + c * (cw + gap)
        cy = gy + r * (ch + 6)
        col = REGION_COLORS[card["region"]]
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=PANEL,
                    outline=PANEL_EDGE)
        d.rectangle([cx, cy, cx + cw, cy + 3], fill=col)
        ART_SMALL[card["art"]](d, (cx + 1, cy + 4, cx + cw - 1, cy + 50))
        # story number chip over the art
        d.rectangle([cx + 5, cy + 7, cx + 23, cy + 22], fill=RED)
        d.text((cx + 8, cy + 8), str(card["n"]), font=font(SANS_B, 11),
               fill=(255, 255, 255))
        f_kick = font(SANS_B, 9)
        d.text((cx + 8, cy + 54), card["kicker"], font=f_kick, fill=col)
        lines, f_head = fit_lines(d, card["headline"], font(SERIF_B, 13),
                                  cw - 16, 2)
        ly = cy + 68
        for ln in lines:
            d.text((cx + 8, ly), ln, font=f_head, fill=INK)
            ly += f_head.size + 1
        f_deck = font(SANS, 10)
        dlines = wrap(d, card["deck"], f_deck, cw - 16)
        ly = cy + 98
        for ln in dlines[:2]:
            d.text((cx + 8, ly), ln, font=f_deck, fill=(60, 58, 52))
            ly += 12
        by = cy + ch - 17
        tw = tag_chip(d, cx + 8, by, card["tag"])
        d.text((cx + 12 + tw, by + 2), card["source"], font=font(SANS, 9),
               fill=MUTED)

    # ---- bottom band: map | also on
    by0 = gy + 2 * ch + 6 + 8
    bh = 152
    # map panel (wider than r2, pins clearly numbered)
    mx, mw = M, 360
    d.rectangle([mx, by0, mx + mw, by0 + bh], fill=PANEL, outline=PANEL_EDGE)
    f_sec = font(SANS_B, 11)
    d.text((mx + 10, by0 + 8), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((mx + 10, by0 + 24), "PINS = STORY NUMBERS", font=font(SANS, 9),
           fill=MUTED)
    pins = []
    seen = set()
    for story in heroes + cards:
        lon, lat = story["pin"]
        if (lon, lat) not in seen:
            seen.add((lon, lat))
            pins.append((story["n"], (lon, lat)))
    draw_map(d, (mx + 8, by0 + 40, mx + mw - 8, by0 + bh - 36), pins)
    d.text((mx + 10, by0 + bh - 30),
           "1 Jiuquan  ·  2 Seoul  ·  3 Hormuz  ·  4 Hodeidah  ·  5 Dhaka  ·  6 Pongkor",
           font=font(SANS, 9), fill=MUTED)
    d.text((mx + 10, by0 + bh - 18),
           "7 Samara  ·  8 London  ·  9 Cartagena  ·  10 NYC  ·  11 Honiara  ·  12 Canberra  ·  13 London",
           font=font(SANS, 9), fill=MUTED)

    # also-on panel (23 stories, 3 columns)
    ax, aw = mx + mw + 8, W - M - (mx + mw + 8)
    d.rectangle([ax, by0, ax + aw, by0 + bh], fill=PANEL, outline=PANEL_EDGE)
    d.text((ax + 10, by0 + 8),
           "ALSO ON 25 NOVEMBER 2026  ·  23 MORE STORIES",
           font=f_sec, fill=INK)
    f_item = font(SANS, 9)
    f_num = font(SANS_B, 9)
    col_w = (aw - 20) // 3
    for i, (num, text, src) in enumerate(also):
        col_i, row_i = divmod(i, 8)
        ix = ax + 10 + col_i * col_w
        iy = by0 + 28 + row_i * 13
        d.text((ix, iy), str(num), font=f_num, fill=RED)
        nw = d.textlength(str(num), font=f_num) + 4
        if d.textlength(text, font=f_item) > col_w - nw - 4:
            raise ValueError(f"also-on item {num} too long: {text!r}")
        d.text((ix + nw, iy), text, font=f_item, fill=INK)

    # ---- date check (3 lines: honest exclusions + "Not yet")
    dy = by0 + bh + 8
    d.rectangle([M, dy, W - M, dy + 46], fill=(238, 232, 218),
                outline=PANEL_EDGE)
    f_dc = font(SANS_B, 10)
    d.text((M + 10, dy + 4), "DATE CHECK", font=f_dc, fill=RED)
    f_dct = font(SANS, 10)
    lines = wrap(d, data["date_check"], f_dct, CW - 20)
    ly = dy + 15
    for ln in lines[:3]:
        d.text((M + 10, ly), ln, font=f_dct, fill=(60, 58, 52))
        ly += 10

    # ---- footer
    fy = dy + 50
    f_f = font(SANS, 9)
    d.text((M, fy), data["sources"], font=f_f, fill=MUTED)
    d.text((M, fy + 12), data["legend"], font=f_f, fill=MUTED)
    tail = "Featured stories dated 25 Nov 2026 (UTC)  ·  Illustrations are drawings"
    d.text((W - M - d.textlength(tail, font=f_f), fy + 12), tail,
           font=f_f, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
