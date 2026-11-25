#!/usr/bin/env python3
"""Render the Wednesday 25 November 2026 world-news front page.

Reads stories.json (35 date-audited stories) and draws one 1024x1024
newspaper-style PNG with three illustrated heroes, a 12-card grid, a
dotted world map, a 20-item 'also on' strip, a day-in-numbers box and a
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
    "EAST ASIA": (155, 44, 95),
    "OCEANIA": (31, 122, 140),
    "SOUTH ASIA": (183, 121, 31),
    "EUROPE": (43, 94, 167),
    "AMERICAS": (107, 79, 161),
    "MIDDLE EAST": (179, 64, 42),
    "AFRICA": (63, 125, 58),
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
    draw.text((x0 + 8, y0 + 6), "-5.3%", font=font(SANS_B, 22),
              fill=(255, 214, 90))


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


ART = {"selloff": draw_selloff, "breach": draw_breach, "fire": draw_fire}

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
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        fnt = font(SANS_B, 9)
        tw = draw.textlength(str(num), font=fnt)
        draw.text((px - tw / 2, py - 6), str(num), font=fnt,
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
    mid = "35 STORIES  ·  8 REGIONS  ·  ONE DAY"
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

    # ---- region bar
    y = 120
    x = M
    f_reg = font(SANS_B, 11)
    for name, count in data["regions"]:
        label = f"{name} {count}"
        w = int(d.textlength(label, font=f_reg)) + 16
        d.rounded_rectangle([x, y, x + w, y + 20], radius=3,
                            fill=REGION_COLORS[name])
        d.text((x + 8, y + 4), label, font=f_reg, fill=(255, 255, 255))
        x += w + 6
    d.line([(M, 146), (W - M, 146)], fill=RULE, width=1)

    # ---- UTC timeline strip
    y = 152
    f_tl = font(SANS, 11)
    f_tlb = font(SANS_B, 11)
    x = M
    for t, label in data["timeline"]:
        d.text((x, y), t, font=f_tlb, fill=RED)
        x += d.textlength(t, font=f_tlb) + 5
        d.text((x, y), label, font=f_tl, fill=INK)
        x += d.textlength(label, font=f_tl) + 10
    d.line([(M, 172), (W - M, 172)], fill=RULE, width=1)

    # ---- heroes
    hy, hh = 180, 272
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
        ill = "illustration"
        f_ill = font(SANS, 9)
        d.text((hx + hw - 10 - d.textlength(ill, font=f_ill), hy + 120),
               ill, font=f_ill, fill=MUTED)
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
        # deck (max 3 lines)
        f_deck = font(SANS, 12)
        dlines = wrap(d, hero["deck"], f_deck, hw - 20)
        ly = hy + 202
        for ln in dlines[:3]:
            d.text((hx + 10, ly), ln, font=f_deck, fill=(60, 58, 52))
            ly += 15
        # tag + source at bottom
        by = hy + hh - 22
        tw = tag_chip(d, hx + 10, by, hero["tag"])
        d.text((hx + 14 + tw, by + 2), hero["source"], font=font(SANS, 10),
               fill=MUTED)

    # ---- 12-card grid
    gy = hy + hh + 8
    cw = (CW - 24) // 4
    ch, gap = 96, 8
    for i, card in enumerate(cards):
        r, c = divmod(i, 4)
        cx = M + c * (cw + gap)
        cy = gy + r * (ch + 6)
        col = REGION_COLORS[card["region"]]
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=PANEL,
                    outline=PANEL_EDGE)
        d.rectangle([cx, cy, cx + cw, cy + 3], fill=col)
        f_kick = font(SANS_B, 9)
        d.text((cx + 8, cy + 7), card["kicker"], font=f_kick, fill=col)
        lines, f_head = fit_lines(d, card["headline"], font(SERIF_B, 14),
                                  cw - 16, 2)
        ly = cy + 21
        for ln in lines:
            d.text((cx + 8, ly), ln, font=f_head, fill=INK)
            ly += f_head.size + 1
        f_deck = font(SANS, 10)
        dlines = wrap(d, card["deck"], f_deck, cw - 16)
        ly = cy + 53
        for ln in dlines[:2]:
            d.text((cx + 8, ly), ln, font=f_deck, fill=(60, 58, 52))
            ly += 12
        by = cy + ch - 17
        tw = tag_chip(d, cx + 8, by, card["tag"])
        d.text((cx + 12 + tw, by + 2), card["source"], font=font(SANS, 9),
               fill=MUTED)

    # ---- bottom band: map | also on | numbers
    by0 = gy + 3 * ch + 2 * 6 + 8
    bh = 180
    # map panel
    mx, mw = M, 300
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
    draw_map(d, (mx + 8, by0 + 40, mx + mw - 8, by0 + bh - 24), pins)
    d.text((mx + 10, by0 + bh - 18),
           "1 Seoul  ·  2 Washington  ·  3 Flinders Is.  ·  5 Canberra",
           font=font(SANS, 9), fill=MUTED)

    # also-on panel
    ax, aw = mx + mw + 8, 400
    d.rectangle([ax, by0, ax + aw, by0 + bh], fill=PANEL, outline=PANEL_EDGE)
    d.text((ax + 10, by0 + 8),
           "ALSO ON 25 NOVEMBER 2026  ·  20 MORE STORIES",
           font=f_sec, fill=INK)
    f_item = font(SANS, 9)
    f_num = font(SANS_B, 9)
    col_w = (aw - 20) // 2
    for i, (num, text, src) in enumerate(also):
        col_i, row_i = divmod(i, 10)
        ix = ax + 10 + col_i * col_w
        iy = by0 + 30 + row_i * 15
        d.text((ix, iy), str(num), font=f_num, fill=RED)
        nw = d.textlength(str(num), font=f_num) + 4
        if d.textlength(text, font=f_item) > col_w - nw - 4:
            raise ValueError(f"also-on item {num} too long: {text!r}")
        d.text((ix + nw, iy), text, font=f_item, fill=INK)

    # numbers panel
    nx, nw = ax + aw + 8, W - M - (ax + aw + 8)
    d.rectangle([nx, by0, nx + nw, by0 + bh], fill=PANEL, outline=PANEL_EDGE)
    d.text((nx + 10, by0 + 8), "THE DAY IN NUMBERS", font=f_sec, fill=INK)
    f_big = font(SERIF_B, 14)
    f_lab = font(SANS, 9)
    ny = by0 + 28
    for val, label in data["numbers"]:
        d.text((nx + 10, ny), val, font=f_big, fill=RED)
        vw = d.textlength(val, font=f_big)
        d.text((nx + 14 + vw, ny + 3), label, font=f_lab,
               fill=(60, 58, 52))
        ny += 25

    # ---- date check
    dy = by0 + bh + 8
    d.rectangle([M, dy, W - M, dy + 38], fill=(238, 232, 218),
                outline=PANEL_EDGE)
    f_dc = font(SANS_B, 10)
    d.text((M + 10, dy + 4), "DATE CHECK", font=f_dc, fill=RED)
    f_dct = font(SANS, 10)
    lines = wrap(d, data["date_check"], f_dct, CW - 20)
    ly = dy + 17
    for ln in lines[:2]:
        d.text((M + 10, ly), ln, font=f_dct, fill=(60, 58, 52))
        ly += 11

    # ---- footer
    fy = dy + 44
    f_f = font(SANS, 9)
    d.text((M, fy), data["sources"], font=f_f, fill=MUTED)
    d.text((M, fy + 12), data["legend"], font=f_f, fill=MUTED)
    tail = "Every story dated 25 Nov 2026 (UTC)  ·  Illustrations are drawings"
    d.text((W - M - d.textlength(tail, font=f_f), fy + 12), tail,
           font=f_f, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
