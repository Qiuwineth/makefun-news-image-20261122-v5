#!/usr/bin/env python3
"""THE WORLD ON SUNDAY - one-picture summary of 22 November 2026.

Pure-stdlib renderer: no Pillow, no system fonts, no network.
Draws a cream broadsheet front page with its own stroke typeface
(every glyph is a set of polylines on a 12-unit cap grid, drawn with
round caps at a fixed advance - letters can never collide), then
writes entry.png next to this file or into MAKEFUN_OUTPUT_DIR.
Deterministic: same input, byte-identical PNG.
"""
import os
import struct
import zlib

# ---------------------------------------------------------------- font
# Glyph space: x grows right, y grows up, baseline y=0, cap height 12,
# x-height 8, descenders to about -3.5. Each glyph: (advance, strokes);
# a stroke is a polyline of (x, y) points.
FONT = {
    'A': (9, [[(0, 0), (4, 12), (8, 0)], [(1.4, 4.6), (6.6, 4.6)]]),
    'B': (9, [[(0, 0), (0, 12)], [(0, 12), (4, 12), (5.6, 10.6), (5.6, 8.2), (4, 6.6), (0, 6.6)], [(0, 6.6), (4.6, 6.6), (6.4, 5.2), (6.4, 2), (4.8, 0), (0, 0)]]),
    'C': (9, [[(7.6, 10.2), (5.2, 12), (2.4, 11.4), (0.8, 9), (0.5, 6), (0.8, 3), (2.4, 0.6), (5.2, 0), (7.6, 1.8)]]),
    'D': (9, [[(0, 0), (0, 12)], [(0, 12), (4.4, 12), (6.8, 9.6), (7.4, 6), (6.8, 2.4), (4.4, 0), (0, 0)]]),
    'E': (8.6, [[(7.4, 12), (0, 12), (0, 0), (7.4, 0)], [(0, 6.4), (5.4, 6.4)]]),
    'F': (8, [[(7.4, 12), (0, 12), (0, 0)], [(0, 6.4), (5, 6.4)]]),
    'G': (9.6, [[(7.6, 10.2), (5.2, 12), (2.4, 11.4), (0.8, 9), (0.5, 6), (0.8, 3), (2.4, 0.6), (5.2, 0), (7.8, 1.6), (7.8, 5.4), (4.4, 5.4)]]),
    'H': (9, [[(0, 0), (0, 12)], [(8, 0), (8, 12)], [(0, 6.2), (8, 6.2)]]),
    'I': (3, [[(1, 0), (1, 12)]]),
    'J': (7, [[(6.6, 12), (6.6, 2.2), (5.2, 0.2), (2.8, 0), (1, 1.4)]]),
    'K': (9, [[(0, 0), (0, 12)], [(7.6, 12), (0.6, 5.6)], [(1.8, 6.6), (8, 0)]]),
    'L': (8, [[(0, 12), (0, 0), (7.4, 0)]]),
    'M': (10.4, [[(0, 0), (0, 12), (4.2, 4.4), (8.4, 12), (8.4, 0)]]),
    'N': (9.6, [[(0, 0), (0, 12), (8, 0), (8, 12)]]),
    'O': (9.6, [[(4.3, 12), (7, 10.6), (8.2, 6), (7, 1.4), (4.3, 0), (1.6, 1.4), (0.4, 6), (1.6, 10.6), (4.3, 12)]]),
    'P': (8.6, [[(0, 0), (0, 12)], [(0, 12), (4.8, 12), (6.6, 10.2), (6.6, 7.6), (4.8, 6), (0, 6)]]),
    'Q': (9.6, [[(4.3, 12), (7, 10.6), (8.2, 6), (7, 1.4), (4.3, 0), (1.6, 1.4), (0.4, 6), (1.6, 10.6), (4.3, 12)], [(5.4, 2.8), (8.8, -0.6)]]),
    'R': (9, [[(0, 0), (0, 12)], [(0, 12), (4.8, 12), (6.6, 10.2), (6.6, 7.6), (4.8, 6), (0, 6)], [(4.2, 6), (8, 0)]]),
    'S': (8.6, [[(7.4, 10.4), (5, 12), (2.2, 11.2), (1, 8.8), (2.4, 6.6), (5.8, 5.2), (7.2, 3.2), (6.2, 0.8), (3.2, 0), (0.8, 1.4)]]),
    'T': (8.6, [[(0, 12), (8, 12)], [(4, 12), (4, 0)]]),
    'U': (9.6, [[(0, 12), (0, 3.2), (1.4, 0.8), (4.3, 0), (7.2, 0.8), (8.6, 3.2), (8.6, 12)]]),
    'V': (9, [[(0, 12), (4, 0), (8, 12)]]),
    'W': (10.4, [[(0, 12), (1.9, 0), (4.3, 8.4), (6.7, 0), (8.6, 12)]]),
    'X': (8.6, [[(0, 0), (7.6, 12)], [(0, 12), (7.6, 0)]]),
    'Y': (9, [[(0, 12), (4, 6.6), (8, 12)], [(4, 6.6), (4, 0)]]),
    'Z': (8.6, [[(0, 12), (7.6, 12), (0, 0), (7.6, 0)]]),
    'a': (8, [[(6.8, 6.6), (5, 8), (2.2, 8), (0.7, 6.2), (0.7, 2), (2.2, 0), (5, 0), (6.8, 1.6)], [(7, 8), (7, 0)]]),
    'b': (8, [[(0, 12), (0, 0)], [(0, 7), (1.2, 8), (4.4, 8), (6.4, 6.6), (7, 4), (6.4, 1.4), (4.4, 0), (1.2, 0), (0, 1)]]),
    'c': (7.6, [[(6.8, 6.6), (5, 8), (2.2, 8), (0.7, 6.2), (0.7, 2), (2.2, 0), (5, 0), (6.8, 1.6)]]),
    'd': (8, [[(7, 7), (5.8, 8), (2.6, 8), (0.6, 6.6), (0, 4), (0.6, 1.4), (2.6, 0), (5.8, 0), (7, 1)], [(7, 12), (7, 0)]]),
    'e': (7.6, [[(0.7, 4.6), (7, 4.6), (6.6, 6.8), (4.2, 8.2), (1.8, 7.4), (0.7, 5), (0.7, 2.4), (2.2, 0.2), (4.6, 0), (6.8, 1.2)]]),
    'f': (4.6, [[(6, 11), (4.4, 12.2), (2.6, 11.4), (2.2, 8.6), (2.2, 0)], [(0.2, 8.6), (4.8, 8.6)]]),
    'g': (8, [[(6.8, 6.8), (5, 8), (2.2, 8), (0.7, 6.2), (0.7, 2), (2.2, 0.2), (5, 0), (6.8, 1.6)], [(7, 8), (7, -0.8), (6, -2.8), (3.4, -3.4), (1.4, -2.6)]]),
    'h': (8, [[(0, 12), (0, 0)], [(0, 5), (1.4, 7.4), (4.4, 8), (6.4, 6.6), (7, 3.2), (7, 0)]]),
    'i': (3, [[(1.2, 8), (1.2, 0)], [(1.2, 10.8), (1.2, 11.6)]]),
    'j': (4.2, [[(4.8, 10.8), (4.8, 11.6)], [(4.8, 8), (4.8, -1.2), (3.6, -3), (1.6, -3.2)]]),
    'k': (7.6, [[(0, 12), (0, 0)], [(6.4, 8), (0.8, 3.2)], [(2, 4.4), (7, 0)]]),
    'l': (3, [[(1.2, 12), (1.2, 0)]]),
    'm': (11, [[(0, 8), (0, 0)], [(0, 5), (1.2, 7.4), (3.4, 8), (4.8, 6.6), (5, 3.2), (5, 0)], [(5, 5), (6.2, 7.4), (8.4, 8), (9.8, 6.6), (10, 3.2), (10, 0)]]),
    'n': (8, [[(0, 8), (0, 0)], [(0, 5), (1.4, 7.4), (4.4, 8), (6.4, 6.6), (7, 3.2), (7, 0)]]),
    'o': (7.6, [[(3.4, 8), (6, 6.6), (6.8, 4), (6, 1.4), (3.4, 0), (1, 1.4), (0.2, 4), (1, 6.6), (3.4, 8)]]),
    'p': (8, [[(0, 8), (0, -3.4)], [(0, 7), (1.2, 8), (4.4, 8), (6.4, 6.6), (7, 4), (6.4, 1.4), (4.4, 0), (1.2, 0), (0, 1)]]),
    'q': (8, [[(7, 7), (5.8, 8), (2.6, 8), (0.6, 6.6), (0, 4), (0.6, 1.4), (2.6, 0), (5.8, 0), (7, 1)], [(7, 8), (7, -3.4)]]),
    'r': (5.6, [[(0, 8), (0, 0)], [(0, 4.6), (1.4, 7.4), (4, 8.2), (5.6, 7.8)]]),
    's': (7, [[(6.4, 6.8), (4.4, 8), (2, 7.4), (1.2, 5.6), (2.6, 4.2), (5.4, 3.2), (6.2, 1.6), (4.8, 0), (2, 0), (0.7, 1)]]),
    't': (5.2, [[(2.4, 11), (2.4, 1.2), (3.4, 0), (5, 0.2)], [(0, 8.4), (5.4, 8.4)]]),
    'u': (8, [[(0, 8), (0, 2.8), (1.2, 0.6), (3.8, 0), (6, 1.4), (7, 3.4)], [(7, 8), (7, 0)]]),
    'v': (7.6, [[(0, 8), (3.4, 0), (6.8, 8)]]),
    'w': (8.6, [[(0, 8), (1.5, 0), (3.4, 5.6), (5.3, 0), (7.2, 8)]]),
    'x': (7.6, [[(0, 0), (6.8, 8)], [(0, 8), (6.8, 0)]]),
    'y': (7.6, [[(0, 8), (3.6, 2.4)], [(6.8, 8), (3.6, 2.4), (2.2, -2.2), (0.6, -3.2)]]),
    'z': (7.6, [[(0, 8), (6.8, 8), (0, 0), (6.8, 0)]]),
    '0': (8.6, [[(3.6, 12), (6.4, 10.2), (7.4, 6), (6.4, 1.8), (3.6, 0), (1, 1.8), (0, 6), (1, 10.2), (3.6, 12)]]),
    '1': (7, [[(2, 9.8), (4.4, 12), (4.4, 0)], [(1.4, 0), (7, 0)]]),
    '2': (8.6, [[(1, 9.6), (3, 12), (5.8, 11.4), (6.8, 9), (5.4, 6.2), (0.6, 0), (7.6, 0)]]),
    '3': (8.6, [[(1, 10.2), (3.4, 12), (5.8, 11), (6.4, 8.6), (5, 6.6), (2.4, 6.6)], [(2.4, 6.6), (5.4, 6), (6.8, 3.6), (5.8, 1), (3, 0), (0.8, 1.2)]]),
    '4': (8.6, [[(5.4, 0), (5.4, 12), (0.4, 3.6), (8, 3.6)]]),
    '5': (8.6, [[(7, 12), (1.4, 12), (1, 7.2), (3.4, 7.8), (5.8, 7), (6.8, 4.2), (5.6, 1), (2.8, 0), (0.8, 1.2)]]),
    '6': (8.6, [[(6.6, 10.6), (4.4, 12), (2, 9.6), (0.8, 6.2), (0.8, 3), (2, 0.8), (4.4, 0), (6.6, 1.4), (7, 4), (5.8, 6.2), (3.4, 6.6), (1.2, 5.6)]]),
    '7': (8.2, [[(0.4, 12), (7.4, 12), (3.4, 0)]]),
    '8': (8.6, [[(4, 12), (6, 10.8), (6, 8.8), (4, 7.4), (2, 8.8), (2, 10.8), (4, 12)], [(4, 7.4), (6.6, 6), (7, 2.6), (4, 0), (1, 2.6), (1.4, 6), (4, 7.4)]]),
    '9': (8.6, [[(1.4, 1.4), (3.4, 0), (5.8, 2.4), (7.2, 6), (7.2, 9), (5.8, 11.2), (3.4, 11.6), (1.2, 10), (1, 7.6), (2.2, 5.6), (4.4, 5.2), (6.8, 6.4)]]),
    '.': (3, [[(1, 0), (1, 0.6)]]),
    ',': (3, [[(1.6, 1.4), (0.9, -1.4)]]),
    ':': (3, [[(1, 6.4), (1, 7)], [(1, 0), (1, 0.6)]]),
    ';': (3, [[(1, 6.4), (1, 7)], [(1.6, 1.4), (0.9, -1.4)]]),
    '!': (3.2, [[(1.2, 12), (1.2, 3.6)], [(1.2, 0), (1.2, 0.6)]]),
    '?': (7.6, [[(1, 9.6), (3, 12), (5.8, 11.4), (6.8, 9.2), (5.4, 6.8), (3.4, 5.6), (3.4, 3.4)], [(3.4, 0), (3.4, 0.6)]]),
    "'": (2.6, [[(2, 12), (1.2, 9.4)]]),
    '"': (6, [[(1.6, 12), (1, 9.4)], [(4.6, 12), (4, 9.4)]]),
    '-': (6, [[(0.4, 4.6), (5, 4.6)]]),
    '\u2013': (8, [[(0, 4.6), (7.2, 4.6)]]),
    '\u2014': (11, [[(0, 4.6), (10, 4.6)]]),
    '\u00b7': (3.2, [[(1.2, 4.4), (1.2, 5)]]),
    '(': (5, [[(5.4, 12), (3, 9), (2.2, 6), (3, 3), (5.4, 0)]]),
    ')': (5, [[(0.6, 12), (3, 9), (3.8, 6), (3, 3), (0.6, 0)]]),
    '/': (6, [[(0.8, 0), (5.4, 12)]]),
    '%': (9.6, [[(2.2, 11.4), (3.8, 10.4), (3.6, 8.6), (2, 8.2), (0.6, 9.4), (0.8, 11), (2.2, 11.4)], [(1, 0), (7.6, 12)], [(6.4, 3.8), (8, 2.8), (7.8, 1), (6.2, 0.6), (4.8, 1.8), (5, 3.4), (6.4, 3.8)]]),
    '$': (8.6, [[(7.4, 10.4), (5, 12), (2.2, 11.2), (1, 8.8), (2.4, 6.6), (5.8, 5.2), (7.2, 3.2), (6.2, 0.8), (3.2, 0), (0.8, 1.4)], [(4.2, -1.6), (4.2, 13.6)]]),
    '#': (9.6, [[(2.4, 0), (3.4, 12)], [(6.4, 0), (7.4, 12)], [(0.4, 4.2), (8.8, 4.2)], [(0.4, 7.8), (8.8, 7.8)]]),
    '+': (8, [[(0.4, 6), (7.2, 6)], [(3.8, 2.2), (3.8, 9.8)]]),
    '=': (8, [[(0.4, 8.6), (7.2, 8.6)], [(0.4, 4), (7.2, 4)]]),
    ' ': (4.6, []),
}
FALLBACK = FONT['?']
SPACE_ADV = 4.6


def glyph(ch):
    if ch in FONT:
        return FONT[ch]
    if ch in ('\u2019', '\u2018'):
        return FONT["'"]
    if ch in ('\u201c', '\u201d'):
        return FONT['"']
    if ch in ('\u2026',):
        return FONT['.']
    return FALLBACK


# ---------------------------------------------------------------- canvas
SS = 2                      # supersample factor (rendered big, averaged down)
W, H = 1200, 1200           # final size
DW, DH = W * SS, H * SS
BUF = bytearray(DW * DH * 3)


def _set(x, y, rgb):
    if 0 <= x < DW and 0 <= y < DH:
        i = (y * DW + x) * 3
        BUF[i] = rgb[0]
        BUF[i + 1] = rgb[1]
        BUF[i + 2] = rgb[2]


def fill_all(rgb):
    row = bytes(rgb) * DW
    for y in range(DH):
        BUF[y * DW * 3:(y + 1) * DW * 3] = row


def rect(x, y, w, h, rgb):
    x0, y0 = int(round(x * SS)), int(round(y * SS))
    x1, y1 = int(round((x + w) * SS)), int(round((y + h) * SS))
    rw = bytes(rgb) * max(0, x1 - x0)
    for yy in range(max(0, y0), min(DH, y1)):
        i = (yy * DW + max(0, x0)) * 3
        BUF[i:i + len(rw)] = rw


def disc(cx, cy, r, rgb):
    cx, cy, r = cx * SS, cy * SS, r * SS
    x0, x1 = int(cx - r - 1), int(cx + r + 1)
    y0, y1 = int(cy - r - 1), int(cy + r + 1)
    r2 = r * r
    for yy in range(max(0, y0), min(DH, y1 + 1)):
        dy = yy - cy
        for xx in range(max(0, x0), min(DW, x1 + 1)):
            dx = xx - cx
            if dx * dx + dy * dy <= r2:
                _set(xx, yy, rgb)


def line(x0, y0, x1, y1, rgb, wdt):
    """Thick line with round caps, drawn by stamping discs."""
    x0, y0, x1, y1 = x0 * SS, y0 * SS, x1 * SS, y1 * SS
    r = wdt * SS / 2.0
    dx, dy = x1 - x0, y1 - y0
    dist = max(abs(dx), abs(dy))
    steps = max(1, int(dist / max(1.0, r * 0.55)))
    r2 = r * r
    rad = int(r + 1)
    for s in range(steps + 1):
        cx = x0 + dx * s / steps
        cy = y0 + dy * s / steps
        for yy in range(int(cy - rad), int(cy + rad + 1)):
            if 0 <= yy < DH:
                dyy = yy - cy
                for xx in range(int(cx - rad), int(cx + rad + 1)):
                    if 0 <= xx < DW:
                        dxx = xx - cx
                        if dxx * dxx + dyy * dyy <= r2:
                            _set(xx, yy, rgb)


def poly(pts, rgb, wdt, close=False):
    pp = list(pts) + ([pts[0]] if close and pts else [])
    for a, b in zip(pp, pp[1:]):
        line(a[0], a[1], b[0], b[1], rgb, wdt)


def fill_poly(pts, rgb):
    """Scanline polygon fill (even-odd), device space."""
    dp = [(x * SS, y * SS) for x, y in pts]
    ys = [p[1] for p in dp]
    y0, y1 = int(min(ys)), int(max(ys))
    n = len(dp)
    for yy in range(max(0, y0), min(DH, y1 + 1)):
        yc = yy + 0.5
        xs = []
        for i in range(n):
            xa, ya = dp[i]
            xb, yb = dp[(i + 1) % n]
            if (ya <= yc < yb) or (yb <= yc < ya):
                xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa, xb = int(xs[k]), int(xs[k + 1])
            for xx in range(max(0, xa), min(DW, xb + 1)):
                _set(xx, yy, rgb)


# ---------------------------------------------------------------- text
def text_w(text, cap, tracking=0.0):
    """Width in final px for a string at cap-height `cap` (final px)."""
    sc = cap / 12.0
    tot = 0.0
    for ch in text:
        tot += SPACE_ADV * sc if ch == ' ' else glyph(ch)[0] * sc
    if text:
        tot += tracking * (len(text) - 1)
    return tot


def draw_text(x, ybase, text, cap, rgb, wdt, tracking=0.0, align='left'):
    """Draw text; ybase is the baseline in final px (y grows down)."""
    sc = cap / 12.0
    tw = text_w(text, cap, tracking)
    if align == 'center':
        x -= tw / 2.0
    elif align == 'right':
        x -= tw
    cx = x
    for ch in text:
        if ch == ' ':
            cx += SPACE_ADV * sc + tracking
            continue
        adv, strokes = glyph(ch)
        for stroke in strokes:
            pts = [(cx + gx * sc, ybase - gy * sc) for gx, gy in stroke]
            for a, b in zip(pts, pts[1:]):
                line(a[0], a[1], b[0], b[1], rgb, wdt)
            if len(pts) == 1:
                line(pts[0][0], pts[0][1], pts[0][0], pts[0][1], rgb, wdt)
        cx += adv * sc + tracking
    return tw


def fit_cap(text, target_w, tracking=0.0):
    """Cap-height so the string spans exactly target_w (final px)."""
    lo, hi = 1.0, 400.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if text_w(text, mid, tracking) < target_w:
            lo = mid
        else:
            hi = mid
    return lo


def wrap(text, cap, max_w, tracking=0.0):
    words = text.split()
    lines, cur = [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if text_w(trial, cap, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, ybase, text, cap, rgb, wdt, max_w, leading, tracking=0.0):
    """Wrapped paragraph; returns the y of the last baseline."""
    for ln in wrap(text, cap, max_w, tracking):
        draw_text(x, ybase, ln, cap, rgb, wdt, tracking)
        ybase += leading
    return ybase - leading


# ---------------------------------------------------------------- png
def save_png(path):
    raw = bytearray()
    # downsample SS x SS by averaging, emit scanlines with filter 0
    for y in range(H):
        raw.append(0)
        for x in range(W):
            sr = sg = sb = 0
            for dy in range(SS):
                base = ((y * SS + dy) * DW + x * SS) * 3
                for dx in range(SS):
                    i = base + dx * 3
                    sr += BUF[i]
                    sg += BUF[i + 1]
                    sb += BUF[i + 2]
            n = SS * SS
            raw += bytes((sr // n, sg // n, sb // n))

    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as fh:
        fh.write(png)


# ---------------------------------------------------------------- poster
import math

PAPER = (243, 234, 216)
INK = (20, 17, 12)
RED = (186, 32, 22)
WHITE = (250, 248, 240)
TEAL = (13, 70, 84)
GREY = (96, 90, 78)


def circle_pts(cx, cy, r, n=40):
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def flag_us(x, y):
    rect(x, y, 96, 56, WHITE)
    for i in range(4):
        rect(x, y + i * 16, 96, 8, (178, 34, 42))
    rect(x, y, 42, 30, (30, 40, 110))
    for r in range(3):
        for c in range(4):
            disc(x + 6 + c * 10, y + 6 + r * 9, 1.7, WHITE)


def flag_cn(x, y):
    rect(x, y, 96, 56, (206, 32, 40))
    disc(x + 15, y + 14, 5.5, (250, 214, 60))
    for dx, dy in ((30, 6), (34, 14), (34, 23), (30, 31)):
        disc(x + dx, y + dy, 2.3, (250, 214, 60))


def flag_ru(x, y):
    rect(x, y, 96, 19, WHITE)
    rect(x, y + 19, 96, 18, (30, 70, 170))
    rect(x, y + 37, 96, 19, (200, 40, 40))


def lead_panel(x, y, w, h):
    rect(x, y, w, h, TEAL)
    disc(x + w / 2, y + 104, 84, (32, 112, 124))
    poly(circle_pts(x + w / 2, y + 104, 84), (120, 195, 200), 2, close=True)
    line(x + w / 2 - 84, y + 104, x + w / 2 + 84, y + 104, (120, 195, 200), 1.6)
    for px, fn in ((120, flag_us), (332, flag_cn), (544, flag_ru)):
        line(x + px, y + 22, x + px, y + 120, (205, 200, 185), 3)
        fn(x + px + 3, y + 22)
    fill_poly([(x + 56, y + 182), (x + 608, y + 182), (x + 576, y + 214), (x + 88, y + 214)], (120, 80, 38))
    line(x + 56, y + 182, x + 608, y + 182, (172, 122, 62), 3)
    for cx in (150, 332, 514):
        disc(x + cx, y + 150, 14, (10, 10, 10))
        fill_poly([(x + cx - 27, y + 214), (x + cx + 27, y + 214),
                   (x + cx + 16, y + 166), (x + cx - 16, y + 166)], (10, 10, 10))


def ill_climate(x, y, w, h):
    rect(x, y, w, h, (18, 64, 44))
    disc(x + 72, y + 35, 26, (52, 128, 84))
    poly([(x + 60, y + 14), (x + 68, y + 27), (x + 61, y + 38), (x + 71, y + 50), (x + 65, y + 58)], (18, 64, 44), 3.4)
    poly([(x + 84, y + 18), (x + 78, y + 30), (x + 86, y + 44)], (18, 64, 44), 3)
    line(x + 252, y + 10, x + 252, y + 40, WHITE, 5)
    line(x + 252, y + 24, x + 252, y + 42, (230, 60, 40), 3)
    disc(x + 252, y + 50, 8, (230, 60, 40))
    for i in range(3):
        line(x + 258, y + 16 + i * 10, x + 266, y + 16 + i * 10, WHITE, 2)


def ill_cyber(x, y, w, h):
    rect(x, y, w, h, (14, 28, 72))
    for rx in (26, 118):
        rect(x + rx, y + 12, 74, 46, (10, 20, 52))
        for r in range(3):
            rect(x + rx + 8, y + 19 + r * 14, 44, 6, (70, 110, 190))
            disc(x + rx + 62, y + 22 + r * 14, 2.6, (90, 230, 140) if r != 1 else (240, 90, 80))
    fill_poly([(x + 252, y + 10), (x + 228, y + 54), (x + 276, y + 54)], (248, 196, 40))
    draw_text(x + 252, y + 48, '!', 24, INK, 3.4, align='center')
    fill_poly([(x + 312, y + 8), (x + 294, y + 38), (x + 305, y + 38), (x + 297, y + 60), (x + 320, y + 29), (x + 308, y + 29)], (248, 196, 40))


def ill_factory(x, y, w, h):
    rect(x, y, w, h, (22, 20, 18))
    rect(x + 18, y + 42, 190, 28, (56, 52, 48))
    rect(x + 36, y + 12, 16, 34, (56, 52, 48))
    rect(x + 70, y + 20, 12, 26, (56, 52, 48))
    poly([(x + 120, y + 42), (x + 140, y + 28), (x + 160, y + 42), (x + 180, y + 28), (x + 200, y + 42)], (56, 52, 48), 7)
    for fx in (238, 272, 306):
        fill_poly([(x + fx - 11, y + 58), (x + fx, y + 22), (x + fx + 11, y + 58)], (238, 110, 30))
        fill_poly([(x + fx - 5.5, y + 58), (x + fx, y + 36), (x + fx + 5.5, y + 58)], (250, 196, 60))
    for sx, sy, sr in ((44, 8, 4), (80, 5, 5), (120, 9, 3.4)):
        disc(x + sx, y + sy, sr, (120, 116, 110))


def ill_nigeria(x, y, w, h):
    rect(x, y, w, h, (110, 170, 220))
    disc(x + 296, y + 18, 11, (250, 205, 70))
    rect(x, y + 44, w, h - 44, (40, 110, 170))
    for wx, wy in ((30, 54), (120, 60), (230, 53), (300, 61)):
        poly([(x + wx, y + wy), (x + wx + 12, y + wy - 4), (x + wx + 24, y + wy)], WHITE, 2)
    fill_poly([(x + 58, y + 42), (x + 152, y + 42), (x + 138, y + 57), (x + 74, y + 57)], (110, 74, 40))
    rect(x + 94, y + 30, 28, 12, (236, 230, 214))
    line(x + 108, y + 30, x + 108, y + 16, INK, 2.4)


def ill_vegas(x, y, w, h):
    rect(x, y, w, h, (26, 26, 30))
    fill_poly([(x + 38, y + 48), (x + 70, y + 35), (x + 150, y + 31), (x + 216, y + 36), (x + 246, y + 48), (x + 240, y + 55), (x + 46, y + 55)], (206, 36, 32))
    fill_poly([(x + 126, y + 32), (x + 140, y + 23), (x + 168, y + 23), (x + 180, y + 32)], (150, 24, 24))
    rect(x + 30, y + 24, 9, 22, (170, 30, 28))
    disc(x + 82, y + 54, 9.5, (8, 8, 8))
    disc(x + 82, y + 54, 3.6, (170, 170, 170))
    disc(x + 212, y + 54, 9.5, (8, 8, 8))
    disc(x + 212, y + 54, 3.6, (170, 170, 170))
    line(x + 302, y + 8, x + 302, y + 60, WHITE, 2.4)
    for r in range(3):
        for c in range(4):
            rect(x + 302 + c * 9, y + 8 + r * 9, 9, 9, WHITE if (r + c) % 2 == 0 else INK)


def ill_seoul(x, y, w, h):
    rect(x, y, w, h, (22, 34, 84))
    fill_poly([(x + 28, y + 32), (x + 54, y + 18), (x + 80, y + 32), (x + 54, y + 46)], (12, 12, 14))
    rect(x + 44, y + 38, 20, 8, (12, 12, 14))
    line(x + 80, y + 32, x + 80, y + 48, (250, 205, 70), 2.2)
    disc(x + 80, y + 51, 2.6, (250, 205, 70))
    rect(x + 128, y + 10, 88, 50, (240, 238, 230))
    for i in range(3):
        line(x + 138, y + 20 + i * 11, x + 178, y + 20 + i * 11, (150, 148, 140), 2.4)
    line(x + 140, y + 18, x + 204, y + 52, RED, 5)
    line(x + 204, y + 18, x + 140, y + 52, RED, 5)
    fill_poly([(x + 244, y + 54), (x + 292, y + 26), (x + 299, y + 33), (x + 251, y + 60)], (244, 190, 60))
    fill_poly([(x + 292, y + 26), (x + 299, y + 33), (x + 288, y + 34)], (60, 50, 40))


STRIP_PAINT = {0: ill_climate, 1: ill_cyber, 2: ill_factory,
               3: ill_nigeria, 4: ill_vegas, 5: ill_seoul}

STORIES = [
    ("CLIMATE \u00b7 ANTALYA, TURKEY",
     ["COP31 TALKS COLLAPSE", "WITHOUT A DEAL"],
     "Two days into overtime, nearly 200 nations failed to agree on fossil fuels and finance. Guterres: 'deeply disappointed.'"),
    ("CYBER \u00b7 WASHINGTON",
     ["HACKERS BREACH FBI", "CRIMINAL DATABASE"],
     "Intruders hit the NCIC files \u2014 fingerprints, wanted and missing persons. Trump confirmed it; an FBI probe is under way."),
    ("DISASTER \u00b7 INDONESIA",
     ["FACTORY FIRE: DOZENS", "STILL MISSING"],
     "Fire tore through a confectionery factory, killing at least 3 workers; rescuers still search for over 30 missing."),
    ("DISASTER \u00b7 NIGERIA",
     ["FUNERAL BOAT CAPSIZES", "\u2014 24 DEAD"],
     "A boat carrying mourners to a funeral overturned in southern Nigeria. At least 24 people drowned."),
    ("SPORT \u00b7 LAS VEGAS",
     ["VERSTAPPEN WINS", "A VEGAS THRILLER"],
     "An extraordinary Grand Prix: 34 lead changes and a Ferrari collision \u2014 and Max Verstappen still took the chequered flag."),
    ("POLITICS \u00b7 SEOUL",
     ["MINISTER QUITS OVER", "EXAM SCANDAL"],
     "Education Minister Choi Kyo-jin resigned after last-minute anti-AI-cheating rules threw college entrance exams into chaos."),
]



def box(x, y, idx, kicker, headlines, body):
    STRIP_PAINT[idx](x, y, 348, 60)
    draw_text(x, y + 84, kicker, 15, RED, 2.6, tracking=0.6)
    draw_text(x, y + 111, headlines[0], 22, INK, 3.4, tracking=0.4)
    draw_text(x, y + 137, headlines[1], 22, INK, 3.4, tracking=0.4)
    para(x, y + 161, body, 14.5, INK, 2.2, 348, 19.5)


def main():
    fill_all(PAPER)
    for inset, wd in ((14, 3), (22, 1.4)):
        poly([(inset, inset), (W - inset, inset), (W - inset, H - inset),
              (inset, H - inset)], INK, wd, close=True)
    draw_text(W / 2, 54, "LATE CITY EDITION \u00b7 No. 47 \u00b7 ONE DAY \u2014 ONE PICTURE",
              15.5, INK, 2.4, tracking=2.5, align='center')
    line(36, 66, W - 36, 66, INK, 2)
    mast = "THE WORLD ON SUNDAY"
    cap = fit_cap(mast, 1120, 3)
    draw_text(W / 2, 78 + cap, mast, cap, INK, cap * 0.13, tracking=3, align='center')
    ry = 78 + cap + 14
    line(36, ry, W - 36, ry, RED, 4.5)
    line(36, ry + 6, W - 36, ry + 6, INK, 1.4)
    bar_y = ry + 14
    rect(36, bar_y, 1128, 52, INK)
    draw_text(54, bar_y + 34, "ALL THE DAY'S NEWS", 18, WHITE, 2.6, tracking=1)
    draw_text(W / 2, bar_y + 35, "SUNDAY \u00b7 22 NOVEMBER 2026", 24.5, WHITE, 3.4,
              tracking=1, align='center')
    draw_text(W - 54, bar_y + 34, "IN ONE PICTURE", 18, WHITE, 2.6, tracking=1, align='right')
    kick_y = bar_y + 86
    draw_text(36, kick_y, "THE SUMMIT FALLOUT \u00b7 SHENZHEN \u2014 WASHINGTON \u2014 KYIV",
              19, RED, 3, tracking=1.2)
    h1 = "PEACE ON PAPER IN SHENZHEN,"
    h2 = "WAR AT FULL VOLUME IN UKRAINE"
    hcap = min(fit_cap(h1, 1128, 4), fit_cap(h2, 1128, 4), 62)
    b1 = kick_y + hcap + 14
    draw_text(36, b1, h1, hcap, INK, hcap * 0.115, tracking=4)
    b2 = b1 + hcap * 1.24
    draw_text(36, b2, h2, hcap, INK, hcap * 0.115, tracking=4)
    lead_y = b2 + 24
    lead_panel(36, lead_y, 664, 216)
    tx = 724
    yb = para(tx, lead_y + 23,
              "Trump, Xi and Putin's 'declaration of peace' \u2014 no nuclear war, more oil, "
              "a weaker world court \u2014 met its verdicts on Sunday.",
              18, INK, 2.7, 440, 24.5)
    para(tx, yb + 40,
         "Trump hailed 'one of the most momentous summits in many years'; Zelensky "
         "called it 'very unsuccessful for Russia'.",
         18, INK, 2.7, 440, 24.5)
    sb_y = lead_y + 172
    rect(tx, sb_y, 8, 44, RED)
    draw_text(tx + 22, sb_y + 18, "KYIV AND KRYVYI RIH STRIKES: 5 DEAD", 16.5, INK, 2.9)
    draw_text(tx + 22, sb_y + 39, "RUSSIA'S BIGGEST ATTACK DAY OF THE YEAR", 16.5, INK, 2.9)
    div_y = lead_y + 252
    div_txt = "SIX MORE STORIES THAT SHAPED THE DAY"
    draw_text(W / 2, div_y, div_txt, 19, INK, 3.2, tracking=1, align='center')
    div_hw = text_w(div_txt, 19, 1) / 2
    line(36, div_y - 8, W / 2 - div_hw - 18, div_y - 8, INK, 2)
    line(W / 2 + div_hw + 18, div_y - 8, W - 36, div_y - 8, INK, 2)
    for i, (kick, heads, body) in enumerate(STORIES):
        box(36 + (i % 3) * 372, 700 + (i // 3) * 218, i, kick, heads, body)
    rect(36, 1134, 1128, 40, INK)
    draw_text(54, 1161, "ALSO TODAY", 12.5, RED, 2.4, tracking=1)
    fx = 54 + text_w("ALSO TODAY", 12.5, 1) + 16
    ftext = ("NEPAL'S PM IN DELHI FOR TALKS WITH MODI \u00b7 ROHINGYA WELCOME THE ICJ "
             "GENOCIDE VERDICT \u2014 AND ASK TO GO HOME \u00b7 DRAWN IN PURE PYTHON")
    fcap = min(12.5, fit_cap(ftext, W - 54 - fx, 0.5))
    draw_text(fx, 1161, ftext, fcap, WHITE, 2.2, tracking=0.5)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(os.path.abspath(__file__))
    save_png(os.path.join(outdir, "entry.png"))


if __name__ == "__main__":
    main()
