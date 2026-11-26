#!/usr/bin/env python3
"""Render 'The World in One Day' — Wednesday 25 November 2026.

Fresh renderer for news-image-20261125 round 4. Reads stories.json (50
stories, all first reported on Wed 25 Nov 2026, verified one by one) and
draws a 1024x1024 newspaper front page with PIL. Deterministic: no
randomness, no timestamps, fixed fonts.
"""
import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")
SANS_O = os.path.join(FD, "DejaVuSans-Oblique.ttf")
if not os.path.exists(SANS_O):
    SANS_O = SANS

W, H = 1024, 1024
PAPER = (247, 242, 231)
NAVY = (20, 36, 62)
RED = (163, 22, 33)
INK = (26, 26, 26)
MUTED = (90, 90, 90)
RULE = (201, 194, 178)
SEA = (220, 232, 240)
LAND = (230, 223, 201)
LAND_LINE = (168, 159, 131)

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(d, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def trunc(d, text, font, max_w):
    if text_w(d, text, font) <= max_w:
        return text
    ell = "…"
    while text and text_w(d, text + ell, font) > max_w:
        text = text[:-1]
    return text + ell


def fit_font(d, text, path, start, max_w, minimum=7):
    size = start
    while size > minimum and text_w(d, text, F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def draw_wrapped(d, x, y, text, font, max_w, fill, lh=None, max_lines=None):
    lines = wrap(d, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = trunc(d, lines[-1], font, max_w)
    if lh is None:
        lh = font.size + 3
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=font, fill=fill)
    return len(lines)


# ---------------------------------------------------------------- scenes
def _sky(d, box, color):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=color)


def scene_tariff(d, box):
    x, y, w, h = box
    _sky(d, box, (188, 211, 230))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(46, 95, 122))
    d.polygon([(x + w * 0.08, y + h * 0.62), (x + w * 0.92, y + h * 0.62),
               (x + w * 0.84, y + h * 0.80), (x + w * 0.16, y + h * 0.80)],
              fill=(20, 36, 62))
    cols = [(192, 57, 43), (230, 126, 34), (46, 134, 193), (39, 174, 96)]
    for i, c in enumerate(cols):
        cx = x + w * (0.14 + i * 0.19)
        d.rectangle([cx, y + h * 0.30, cx + w * 0.16, y + h * 0.60], fill=c)
        d.rectangle([cx, y + h * 0.44, cx + w * 0.16, y + h * 0.60], fill=c)
    d.ellipse([x + w * 0.72, y + h * 0.04, x + w * 0.97, y + h * 0.29],
              fill=(255, 255, 255), outline=RED, width=3)
    d.text((x + w * 0.775, y + h * 0.10), "20%", font=F(SANS_B, max(10, int(h * 0.16))),
           fill=RED)


def scene_ai(d, box):
    x, y, w, h = box
    _sky(d, box, (26, 26, 46))
    cw, ch = w * 0.34, h * 0.52
    cx, cy = x + w * 0.33, y + h * 0.24
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=(232, 232, 232))
    d.rectangle([cx + cw * 0.28, cy + ch * 0.28, cx + cw * 0.72, cy + ch * 0.72],
                fill=(26, 26, 46))
    for i in range(3):
        d.line([cx + cw * (0.15 + i * 0.35), cy, cx + cw * (0.15 + i * 0.35), cy - h * 0.10],
               fill=(232, 232, 232), width=3)
        d.line([cx + cw * (0.15 + i * 0.35), cy + ch, cx + cw * (0.15 + i * 0.35), cy + ch + h * 0.10],
               fill=(232, 232, 232), width=3)
    pts = [(x + w * 0.55, y + h * 0.18), (x + w * 0.65, y + h * 0.34),
           (x + w * 0.72, y + h * 0.28), (x + w * 0.82, y + h * 0.52),
           (x + w * 0.90, y + h * 0.44), (x + w * 0.97, y + h * 0.72)]
    d.line(pts, fill=(220, 40, 50), width=4)
    d.polygon([(x + w * 0.93, y + h * 0.62), (x + w * 0.99, y + h * 0.78),
               (x + w * 0.90, y + h * 0.76)], fill=(220, 40, 50))


def scene_shenzhou(d, box):
    x, y, w, h = box
    _sky(d, box, (11, 30, 58))
    for sx, sy in [(0.08, 0.12), (0.22, 0.06), (0.85, 0.10), (0.93, 0.30),
                   (0.05, 0.55), (0.90, 0.62), (0.70, 0.08), (0.38, 0.18)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * sx + 3, y + h * sy + 3],
                  fill=(255, 255, 255))
    d.polygon([(x + w * 0.20, y + h * 0.30), (x + w * 0.28, y + h * 0.30),
               (x + w * 0.24, y + h * 0.12)], fill=(255, 255, 255))
    d.rectangle([x + w * 0.20, y + h * 0.30, x + w * 0.28, y + h * 0.62],
                fill=(240, 240, 240))
    d.polygon([(x + w * 0.20, y + h * 0.62), (x + w * 0.28, y + h * 0.62),
               (x + w * 0.24, y + h * 0.82)], fill=(255, 140, 40))
    d.rectangle([x + w * 0.16, y + h * 0.52, x + w * 0.20, y + h * 0.60],
                fill=(200, 60, 40))
    d.rectangle([x + w * 0.28, y + h * 0.52, x + w * 0.32, y + h * 0.60],
                fill=(200, 60, 40))
    for cx, cy, r in [(0.62, 0.30, 0.11), (0.78, 0.42, 0.09), (0.60, 0.55, 0.08)]:
        d.ellipse([x + w * (cx - r), y + h * (cy - r), x + w * (cx + r), y + h * (cy + r)],
                  fill=(180, 190, 205), outline=(255, 255, 255), width=2)
    d.line([x + w * 0.62, y + h * 0.30, x + w * 0.78, y + h * 0.42], fill=(255, 255, 255), width=2)
    d.line([x + w * 0.62, y + h * 0.30, x + w * 0.60, y + h * 0.55], fill=(255, 255, 255), width=2)


def scene_hodeidah(d, box):
    x, y, w, h = box
    _sky(d, box, (232, 168, 124))
    d.rectangle([x, y + int(h * 0.72), x + w, y + h], fill=(90, 110, 130))
    for cx in (0.12, 0.45, 0.78):
        d.rectangle([x + w * cx, y + h * 0.30, x + w * (cx + 0.03), y + h * 0.72],
                    fill=(40, 40, 50))
        d.rectangle([x + w * cx, y + h * 0.30, x + w * (cx + 0.22), y + h * 0.36],
                    fill=(40, 40, 50))
    for bx, by, r in [(0.30, 0.28, 0.14), (0.62, 0.20, 0.11), (0.85, 0.34, 0.09)]:
        d.ellipse([x + w * (bx - r), y + h * (by - r), x + w * (bx + r), y + h * (by + r)],
                  fill=(255, 140, 30))
        d.ellipse([x + w * (bx - r * 0.55), y + h * (by - r * 0.55),
                   x + w * (bx + r * 0.55), y + h * (by + r * 0.55)], fill=(255, 220, 90))


def scene_dhaka(d, box):
    x, y, w, h = box
    _sky(d, box, (242, 216, 167))
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.92, y + h * 0.22], fill=(255, 200, 80))
    d.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.55, y + h * 0.85], fill=(120, 120, 125))
    d.rectangle([x + w * 0.60, y + h * 0.55, x + w * 0.90, y + h * 0.85], fill=(150, 150, 155))
    for cx in (0.14, 0.30, 0.46):
        d.rectangle([x + w * cx, y + h * 0.25, x + w * (cx + 0.05), y + h * 0.45],
                    fill=(90, 90, 95))
    for wx in (0.16, 0.28, 0.40, 0.66, 0.78):
        d.rectangle([x + w * wx, y + h * 0.55, x + w * (wx + 0.06), y + h * 0.65],
                    fill=(255, 240, 180))
    d.ellipse([x + w * 0.16, y + h * 0.16, x + w * 0.24, y + h * 0.24], fill=(220, 220, 220))
    d.ellipse([x + w * 0.33, y + h * 0.14, x + w * 0.41, y + h * 0.22], fill=(220, 220, 220))


def scene_pongkor(d, box):
    x, y, w, h = box
    _sky(d, box, (58, 42, 26))
    d.pieslice([x + w * 0.22, y + h * 0.15, x + w * 0.78, y + h * 0.95], 180, 360,
               fill=(12, 10, 8))
    d.rectangle([x + w * 0.24, y + h * 0.45, x + w * 0.29, y + h * 0.95], fill=(120, 85, 50))
    d.rectangle([x + w * 0.71, y + h * 0.45, x + w * 0.76, y + h * 0.95], fill=(120, 85, 50))
    d.rectangle([x + w * 0.24, y + h * 0.42, x + w * 0.76, y + h * 0.48], fill=(120, 85, 50))
    d.rectangle([x, y + int(h * 0.72), x + w, y + h], fill=(40, 110, 160))
    for i in range(3):
        yy = y + h * (0.76 + i * 0.07)
        d.arc([x + w * 0.05, yy, x + w * 0.95, yy + h * 0.10], 0, 180, fill=(180, 220, 245), width=2)
    d.ellipse([x + w * 0.44, y + h * 0.38, x + w * 0.56, y + h * 0.50], fill=(255, 220, 90))
    d.ellipse([x + w * 0.34, y + h * 0.62, x + w * 0.66, y + h * 0.70], fill=(255, 220, 90))


def scene_refinery(d, box):
    x, y, w, h = box
    _sky(d, box, (223, 232, 240))
    for cx, cw in [(0.12, 0.10), (0.30, 0.12), (0.52, 0.10), (0.70, 0.13)]:
        d.rectangle([x + w * cx, y + h * 0.30, x + w * (cx + cw), y + h * 0.85],
                    fill=(90, 100, 110))
        d.line([x + w * cx, y + h * 0.45, x + w * (cx + cw), y + h * 0.45],
               fill=(60, 70, 80), width=2)
        d.line([x + w * cx, y + h * 0.62, x + w * (cx + cw), y + h * 0.62],
               fill=(60, 70, 80), width=2)
    d.rectangle([x + w * 0.86, y + h * 0.18, x + w * 0.92, y + h * 0.85], fill=(70, 80, 90))
    d.polygon([(x + w * 0.87, y + h * 0.18), (x + w * 0.91, y + h * 0.18),
               (x + w * 0.89, y + h * 0.02)], fill=(255, 140, 30))
    d.ellipse([x + w * 0.36, y + h * 0.10, x + w * 0.50, y + h * 0.24], fill=(255, 170, 60))
    d.ellipse([x + w * 0.40, y + h * 0.14, x + w * 0.46, y + h * 0.20], fill=(255, 220, 90))


def scene_ukcap(d, box):
    x, y, w, h = box
    _sky(d, box, (207, 224, 240))
    d.rectangle([x + w * 0.14, y + h * 0.45, x + w * 0.52, y + h * 0.85], fill=(180, 120, 80))
    d.polygon([(x + w * 0.10, y + h * 0.46), (x + w * 0.33, y + h * 0.20),
               (x + w * 0.56, y + h * 0.46)], fill=(120, 50, 40))
    d.rectangle([x + w * 0.28, y + h * 0.62, x + w * 0.38, y + h * 0.85], fill=(60, 40, 30))
    d.rectangle([x + w * 0.18, y + h * 0.52, x + w * 0.24, y + h * 0.60], fill=(255, 240, 180))
    d.polygon([(x + w * 0.74, y + h * 0.10), (x + w * 0.62, y + h * 0.48),
               (x + w * 0.72, y + h * 0.48), (x + w * 0.60, y + h * 0.85),
               (x + w * 0.82, y + h * 0.42), (x + w * 0.72, y + h * 0.42)],
              fill=(255, 210, 40))


def scene_cartagena(d, box):
    x, y, w, h = box
    _sky(d, box, (240, 217, 181))
    d.rectangle([x + w * 0.12, y + h * 0.25, x + w * 0.88, y + h * 0.85], fill=(214, 178, 128))
    d.rectangle([x + w * 0.12, y + h * 0.25, x + w * 0.88, y + h * 0.33], fill=(160, 90, 60))
    for wx in (0.20, 0.38, 0.56, 0.74):
        d.rectangle([x + w * wx, y + h * 0.42, x + w * (wx + 0.08), y + h * 0.56],
                    fill=(60, 50, 40))
    d.pieslice([x + w * 0.40, y + h * 0.55, x + w * 0.60, y + h * 0.88], 180, 360,
               fill=(50, 35, 25))
    d.ellipse([x + w * 0.74, y + h * 0.08, x + w * 0.90, y + h * 0.24], fill=(255, 255, 255),
              outline=(163, 22, 33), width=3)
    d.text((x + w * 0.775, y + h * 0.115), "20", font=F(SANS_B, max(9, int(h * 0.12))),
           fill=(163, 22, 33))


def scene_unwomen(d, box):
    x, y, w, h = box
    _sky(d, box, (246, 232, 232))
    txt = "47,000"
    fs = max(11, int(h * 0.30))
    while fs > 8 and text_w(d, txt, F(SANS_B, fs)) > w * 0.92:
        fs -= 1
    tw = text_w(d, txt, F(SANS_B, fs))
    d.text((x + (w - tw) / 2, y + h * 0.10), txt, font=F(SANS_B, fs), fill=(140, 20, 30))
    for i, cx in enumerate((0.28, 0.50, 0.72)):
        d.ellipse([x + w * (cx - 0.055), y + h * 0.52, x + w * (cx + 0.055), y + h * 0.63],
                  fill=(90, 60, 70))
        d.polygon([(x + w * (cx - 0.11), y + h * 0.88), (x + w * (cx + 0.11), y + h * 0.88),
                   (x + w * (cx + 0.07), y + h * 0.64), (x + w * (cx - 0.07), y + h * 0.64)],
                  fill=(90, 60, 70))


def scene_solomons(d, box):
    x, y, w, h = box
    _sky(d, box, (127, 179, 213))
    d.rectangle([x, y + int(h * 0.68), x + w, y + h], fill=(46, 110, 160))
    d.ellipse([x + w * 0.08, y + h * 0.55, x + w * 0.92, y + h * 0.85], fill=(84, 160, 90))
    d.line([x + w * 0.62, y + h * 0.58, x + w * 0.62, y + h * 0.30], fill=(90, 60, 30), width=4)
    tx, ty = x + w * 0.62, y + h * 0.30
    for ex, ey in [(-0.18, -0.08), (-0.12, -0.16), (0.0, -0.18), (0.12, -0.16),
                   (0.18, -0.08)]:
        d.line([tx, ty, tx + w * ex, ty + h * ey], fill=(40, 120, 50), width=3)
    d.ellipse([x + w * 0.10, y + h * 0.08, x + w * 0.22, y + h * 0.20], fill=(255, 210, 90))


def scene_lgbtq(d, box):
    x, y, w, h = box
    _sky(d, box, (255, 255, 255))
    cols = [(228, 0, 40), (255, 140, 0), (255, 235, 0), (0, 150, 70),
            (0, 90, 200), (140, 60, 180)]
    cx, cy, r0 = x + w * 0.50, y + h * 0.95, w * 0.42
    for i, c in enumerate(cols):
        r = r0 - i * h * 0.075
        d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=c, width=max(2, int(h * 0.07)))


def scene_met(d, box):
    x, y, w, h = box
    _sky(d, box, (223, 232, 240))
    d.pieslice([x + w * 0.25, y + h * 0.22, x + w * 0.75, y + h * 0.78], 180, 360,
               fill=(20, 50, 110))
    d.rectangle([x + w * 0.18, y + h * 0.68, x + w * 0.82, y + h * 0.76], fill=(10, 20, 40))
    d.ellipse([x + w * 0.44, y + h * 0.30, x + w * 0.56, y + h * 0.44], fill=(220, 220, 230),
              outline=(163, 22, 33), width=2)
    d.rectangle([x + w * 0.25, y + h * 0.55, x + w * 0.75, y + h * 0.62], fill=(10, 20, 40))


def scene_hormuz(d, box):
    x, y, w, h = box
    _sky(d, box, (207, 224, 234))
    d.rectangle([x, y + int(h * 0.70), x + w, y + h], fill=(60, 100, 130))
    d.polygon([(x + w * 0.10, y + h * 0.62), (x + w * 0.90, y + h * 0.62),
               (x + w * 0.82, y + h * 0.78), (x + w * 0.18, y + h * 0.78)],
              fill=(30, 30, 40))
    d.rectangle([x + w * 0.68, y + h * 0.42, x + w * 0.88, y + h * 0.62], fill=(200, 200, 205))
    for bx, by, r in [(0.30, 0.40, 0.10), (0.45, 0.32, 0.08)]:
        d.ellipse([x + w * (bx - r), y + h * (by - r), x + w * (bx + r), y + h * (by + r)],
                  fill=(255, 140, 30))
    d.ellipse([x + w * 0.74, y + h * 0.05, x + w * 0.96, y + h * 0.27], fill=(163, 22, 33))
    d.text((x + w * 0.825, y + h * 0.075), "?", font=F(SANS_B, max(10, int(h * 0.16))),
           fill=(255, 255, 255))


def scene_cairo(d, box):
    x, y, w, h = box
    _sky(d, box, (232, 201, 160))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(110, 110, 115))
    d.polygon([(x + w * 0.30, y + h * 0.70), (x + w * 0.72, y + h * 0.52),
               (x + w * 0.76, y + h * 0.62), (x + w * 0.34, y + h * 0.80)],
              fill=(180, 60, 40))
    d.ellipse([x + w * 0.36, y + h * 0.52, x + w * 0.42, y + h * 0.58], fill=(30, 30, 30))
    d.ellipse([x + w * 0.62, y + h * 0.46, x + w * 0.68, y + h * 0.52], fill=(30, 30, 30))
    for bx, by, r in [(0.18, 0.38, 0.11), (0.26, 0.28, 0.08)]:
        d.ellipse([x + w * (bx - r), y + h * (by - r), x + w * (bx + r), y + h * (by + r)],
                  fill=(255, 150, 40))
        d.ellipse([x + w * (bx - r * 0.5), y + h * (by - r * 0.5),
                   x + w * (bx + r * 0.5), y + h * (by + r * 0.5)], fill=(255, 220, 90))


SCENES = {"tariff": scene_tariff, "ai": scene_ai, "shenzhou": scene_shenzhou,
          "hodeidah": scene_hodeidah, "dhaka": scene_dhaka, "pongkor": scene_pongkor,
          "refinery": scene_refinery, "ukcap": scene_ukcap, "cartagena": scene_cartagena,
          "unwomen": scene_unwomen, "solomons": scene_solomons, "lgbtq": scene_lgbtq,
          "met": scene_met, "hormuz": scene_hormuz, "cairo": scene_cairo}

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-75, 62),
     (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 38), (-80, 32), (-85, 30),
     (-90, 21), (-95, 19), (-100, 23), (-110, 28), (-115, 32), (-120, 38),
     (-125, 48), (-135, 58), (-155, 60), (-165, 60)],
    [(-80, 10), (-75, 7), (-70, 12), (-60, 8), (-52, 5), (-50, 0), (-40, -5),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-73, -53), (-70, -45), (-72, -35), (-75, -25), (-80, -15), (-80, -5), (-80, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 70), (40, 68),
     (44, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (22, 37),
     (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    [(-17, 15), (-16, 20), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (32, 30), (35, 28), (38, 22), (40, 15), (43, 12), (48, 11), (51, 10),
     (46, 5), (42, 0), (40, -5), (38, -10), (35, -18), (32, -25), (28, -32),
     (20, -35), (15, -30), (12, -18), (12, -8), (9, 4), (4, 6), (-8, 5),
     (-13, 8), (-17, 12)],
    [(30, 36), (35, 36), (40, 38), (44, 40), (48, 42), (52, 44), (55, 46),
     (60, 50), (65, 55), (70, 60), (75, 65), (80, 70), (90, 72), (100, 75),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 68),
     (170, 66), (178, 65), (170, 60), (162, 58), (158, 52), (150, 60),
     (142, 55), (140, 48), (135, 45), (130, 40), (127, 38), (122, 38),
     (120, 32), (115, 25), (110, 20), (108, 15), (105, 10), (100, 8),
     (98, 12), (95, 16), (92, 20), (90, 22), (86, 20), (82, 16), (80, 13),
     (78, 8), (76, 10), (72, 20), (68, 23), (66, 25), (62, 25), (58, 26),
     (56, 28), (52, 28), (50, 30), (48, 30), (44, 29), (40, 28), (38, 25),
     (35, 30), (33, 32), (30, 35)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -33), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (114, -21)],
    [(-55, 60), (-45, 60), (-40, 65), (-35, 68), (-25, 70), (-20, 74), (-30, 76),
     (-45, 78), (-58, 76), (-60, 70), (-58, 64)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (140, 38), (141, 41), (143, 43),
     (145, 44), (142, 42), (140, 39), (137, 37), (133, 35), (131, 33)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -3), (135, -4), (140, -8), (138, -2), (132, 0), (128, 2), (124, 1),
     (120, 1), (116, 0), (112, 0), (108, -2), (104, -3), (100, -1), (97, 3)],
]


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    featured = data["featured"]
    also = data["also"]
    meta = data["meta"]
    assert len(featured) == 15, len(featured)
    assert len(also) == 35, len(also)
    all_stories = featured + also
    assert [s["n"] for s in all_stories] == list(range(1, 51))
    region_color = {name: color for name, _, color in data["regions"]}
    assert sum(c for _, c, _ in data["regions"]) == 50

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top bar
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((16, 5), "THE WORLD IN ONE DAY", font=F(SANS_B, 13), fill=(255, 255, 255))
    right = ("%d STORIES · %d REGIONS · %d FIELDS · ALL FIRST REPORTED ON %s"
             % (meta["stories"], meta["regions"], meta["fields"], meta["date"].upper()))
    rf = fit_font(d, right, SANS_B, 10, 780)
    d.text((W - 16 - text_w(d, right, rf), 7), right, font=rf, fill=(255, 255, 255))

    # ---- title
    title = meta["date"]
    tf = F(SERIF_B, 42)
    d.text(((W - text_w(d, title, tf)) / 2, 32), title, font=tf, fill=NAVY)
    d.line([16, 92, W - 16, 92], fill=RULE, width=1)

    # ---- ticker
    tick = data["ticker"]
    tkf = fit_font(d, tick, SANS_O, 15, W - 32)
    d.text(((W - text_w(d, tick, tkf)) / 2, 97), tick, font=tkf, fill=RED)

    # ---- region chips
    chips = []
    cf = F(SANS_B, 10)
    total = 0
    for name, count, color in data["regions"]:
        label = "%s %d" % (name, count)
        cw = int(text_w(d, label, cf)) + 14
        chips.append((label, color, cw))
        total += cw
    total += 6 * (len(chips) - 1)
    cx = (W - total) / 2
    for label, color, cw in chips:
        d.rounded_rectangle([cx, 116, cx + cw, 136], radius=4, fill=color)
        d.text((cx + 7, 121), label, font=cf, fill=(255, 255, 255))
        cx += cw + 6

    # ---- fields lines
    ff = F(SANS, 10)
    for i, line in enumerate((data["fields_line1"], data["fields_line2"])):
        d.text(((W - text_w(d, line, ff)) / 2, 140 + i * 13), line, font=ff, fill=MUTED)

    # ---- stat strip
    y0, y1 = 168, 200
    d.line([16, y0, W - 16, y0], fill=RULE, width=1)
    d.line([16, y1, W - 16, y1], fill=RULE, width=1)
    cell_w = (W - 32) / 6
    for i, (val, label) in enumerate(data["stats"]):
        x0 = 16 + i * cell_w
        vf = fit_font(d, val, SANS_B, 15, cell_w - 12, minimum=10)
        d.text((x0 + 6, y0 + 4), val, font=vf, fill=RED)
        draw_wrapped(d, x0 + 6, y0 + 22, label, F(SANS, 9), cell_w - 12, MUTED,
                     lh=11, max_lines=1)
        if i:
            d.line([x0, y0 + 3, x0, y1 - 3], fill=RULE, width=1)

    # ---- timeline
    items = [s.strip() for s in data["timeline"].split("·")]
    tfont = F(SANS, 11)
    tfont_b = F(SANS_B, 11)
    total_w = sum(text_w(d, it.strip(), tfont) for it in items) + 10 * (len(items) - 1)
    while total_w > W - 32 and tfont.size > 8:
        tfont = F(SANS, tfont.size - 1)
        tfont_b = F(SANS_B, tfont_b.size - 1)
        total_w = sum(text_w(d, it.strip(), tfont) for it in items) + 10 * (len(items) - 1)
    tx = (W - total_w) / 2
    ty = 204
    for j, it in enumerate(items):
        it = it.strip()
        sp = it.find(" ")
        tm, rest = it[:sp], it[sp:]
        d.text((tx, ty), tm, font=tfont_b, fill=RED)
        tx += text_w(d, tm, tfont_b)
        d.text((tx, ty), rest, font=tfont, fill=INK)
        tx += text_w(d, rest, tfont)
        if j < len(items) - 1:
            d.text((tx, ty), " · ", font=tfont, fill=MUTED)
            tx += text_w(d, " · ", tfont)
    d.line([16, 218, W - 16, 218], fill=RULE, width=1)

    # ---- heroes
    hero_w = 325
    for i, s in enumerate(featured[:3]):
        x0 = 16 + i * (hero_w + 8)
        SCENES[s["scene"]](d, (x0, 222, hero_w, 96))
        d.rectangle([x0, 222, x0 + hero_w, 318], outline=(120, 110, 90), width=1)
        d.text((x0, 322), s["kicker"], font=F(SANS_B, 11),
               fill=region_color[s["region"]])
        draw_wrapped(d, x0, 338, s["headline"], F(SERIF_B, 16), hero_w, NAVY,
                     lh=19, max_lines=2)
        draw_wrapped(d, x0, 376, s["deck"], F(SANS, 11), hero_w, INK, lh=13, max_lines=2)
        why = trunc(d, s["why"], F(SANS_O, 10), hero_w)
        d.text((x0, 402), why, font=F(SANS_O, 10), fill=MUTED)

    # ---- cards
    card_w = 242
    for i, s in enumerate(featured[3:]):
        row, col = divmod(i, 4)
        x0 = 16 + col * (card_w + 8)
        y0 = 420 + row * 82
        SCENES[s["scene"]](d, (x0, y0 + 4, 72, 72))
        d.rectangle([x0, y0 + 4, x0 + 72, y0 + 76], outline=(120, 110, 90), width=1)
        tx0 = x0 + 80
        tw = card_w - 80 - 4
        kick = s["kicker"]
        kf = F(SANS_B, 9)
        d.text((tx0, y0 + 4), kick, font=kf, fill=region_color[s["region"]])
        if s["tag"] in ("CLAIM", "OFFICIAL"):
            tag_col = RED if s["tag"] == "CLAIM" else NAVY
            d.text((tx0 + text_w(d, kick, kf) + 3, y0 + 4), "· " + s["tag"],
                   font=kf, fill=tag_col)
        draw_wrapped(d, tx0, y0 + 18, s["headline"], F(SANS_B, 12), tw, NAVY,
                     lh=14, max_lines=2)
        draw_wrapped(d, tx0, y0 + 48, s["deck"], F(SANS, 10), tw, INK, lh=12, max_lines=2)

    d.line([16, 666, W - 16, 666], fill=RULE, width=1)

    # ---- map + also-on
    map_x0, map_y0, map_x1, map_y1 = 16, 686, 408, 920
    d.text((16, 668), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=NAVY)
    d.rectangle([map_x0, map_y0, map_x1, map_y1], fill=SEA)
    d.rectangle([map_x0, map_y0, map_x1, map_y1], outline=RULE, width=1)

    def proj(lon, lat):
        px = map_x0 + (lon + 170) / 360.0 * (map_x1 - map_x0)
        py = map_y0 + (75 - lat) / 130.0 * (map_y1 - map_y0)
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    pin_f = F(SANS_B, 7)
    for s in all_stories:
        px, py = proj(s["lon"], s["lat"])
        px += s.get("dx", 0)
        py += s.get("dy", 0)
        r = 6.5
        d.ellipse([px - r, py - r, px + r, py + r], fill=region_color[s["region"]],
                  outline=(255, 255, 255), width=1)
        num = str(s["n"])
        d.text((px - text_w(d, num, pin_f) / 2, py - 5), num, font=pin_f,
               fill=(255, 255, 255))

    ax0 = 424
    d.text((ax0, 668), "ALSO ON WEDNESDAY 25 NOVEMBER", font=F(SANS_B, 11), fill=NAVY)
    col_w = 288
    af = F(SANS, 9)
    abf = F(SANS_B, 9)
    for ci, col_items in enumerate((also[:18], also[18:])):
        cx0 = ax0 + ci * (col_w + 8)
        for ri, s in enumerate(col_items):
            ry = 686 + ri * 13
            num = "%d · " % s["n"]
            d.text((cx0, ry), num, font=abf, fill=RED)
            nx = cx0 + text_w(d, num, abf)
            line = trunc(d, s["line"], af, col_w - (nx - cx0))
            d.text((nx, ry), line, font=af, fill=INK)

    # ---- DATE CHECK
    d.rectangle([16, 926, W - 16, 982], fill=(239, 233, 216))
    d.rectangle([16, 926, 20, 982], fill=RED)
    dcf = F(SANS, 9)
    cy = 929
    for line in data["datecheck"]:
        n = draw_wrapped(d, 28, cy, line, dcf, W - 44, INK, lh=11)
        cy += n * 11

    # ---- footer
    d.line([16, 988, W - 16, 988], fill=RULE, width=1)
    ff1 = F(SANS, 10)
    d.text(((W - text_w(d, data["footer"], ff1)) / 2, 992), data["footer"],
           font=ff1, fill=MUTED)
    ff2 = F(SANS, 9)
    d.text(((W - text_w(d, data["sources"], ff2)) / 2, 1007), data["sources"],
           font=ff2, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    raw = open(out, "rb").read()
    print("saved", out, len(raw), "bytes sha256",
          hashlib.sha256(raw).hexdigest())
    print("stories", len(all_stories), "featured", len(featured), "also", len(also))
    print("regions", {n: c for n, c, _ in data["regions"]})
    fields = {}
    for s in all_stories:
        fields[s["field"]] = fields.get(s["field"], 0) + 1
    print("fields", len(fields), fields)


if __name__ == "__main__":
    main()
