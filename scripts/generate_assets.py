#!/usr/bin/env python3
"""Generate the pixel-art SVG assets used in the profile README.

Everything is drawn with plain <path> rectangles (no external fonts or images),
so GitHub renders it reliably. Animations are pure CSS inside each SVG.

    python3 scripts/generate_assets.py   # writes assets/*.svg
"""
from __future__ import annotations

import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
INK = "#0f0f23"
NAVY = "#14183a"
NAVY2 = "#1e2452"
FRAME = "#f4f1de"
FRAME2 = "#8b93c9"
YELLOW = "#ffd25a"
ORANGE = "#ff9f43"
RED = "#e8505b"
TEAL = "#2ec4b6"
CYAN = "#7fdbff"
GREEN = "#5ad16a"
BLUE = "#4f8cff"
WHITE = "#ffffff"
GRAY = "#9aa0c8"

# --------------------------------------------------------------------------
# 5x7 bitmap font
# --------------------------------------------------------------------------
_FONT_SRC = {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .###.",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# #...# ##..# #.#.# #..## #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "####. ....# ....# .###. ....# ....# ####.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": "..##. .#... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. .#... .#... .#...",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ...#. .##..",
    " ": "..... ..... ..... ..... ..... ..... .....",
    ".": "..... ..... ..... ..... ..... .##.. .##..",
    ",": "..... ..... ..... ..... .##.. .##.. .#...",
    "!": "..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..",
    "?": ".###. #...# ....# ...#. ..#.. ..... ..#..",
    ":": "..... .##.. .##.. ..... .##.. .##.. .....",
    "-": "..... ..... ..... ##### ..... ..... .....",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "'": "..#.. ..#.. .#... ..... ..... ..... .....",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    "(": "...#. ..#.. .#... .#... .#... ..#.. ...#.",
    ")": ".#... ..#.. ...#. ...#. ...#. ..#.. .#...",
    ">": ".#... ..#.. ...#. ....# ...#. ..#.. .#...",
    "<": "...#. ..#.. .#... #.... .#... ..#.. ...#.",
    "_": "..... ..... ..... ..... ..... ..... #####",
    "#": ".#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.",
    "=": "..... ..... ##### ..... ##### ..... .....",
    "%": "##..# ##..# ...#. ..#.. .#... #..## #..##",
    # custom glyphs
    "}": "#.... ##... ###.. ####. ###.. ##... #....",  # play triangle
    "~": "..... ..... ##### .###. ..#.. ..... .....",  # dialog arrow
    "*": "..... .#.#. ##### ##### .###. ..#.. .....",  # heart
}
FONT = {k: v.split() for k, v in _FONT_SRC.items()}
CELL = 6  # glyph advance in font pixels (5 + 1 spacing)


def text_width(s: str, px: int) -> int:
    return (len(s) * CELL - 1) * px


def text_path(s: str, x: float, y: float, px: int) -> str:
    """Return path data for `s` drawn at (x, y) with font pixel size `px`."""
    d = []
    for i, ch in enumerate(s.upper()):
        glyph = FONT.get(ch, FONT["?"])
        gx = x + i * CELL * px
        for r, row in enumerate(glyph):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    w = (c - start) * px
                    d.append(f"M{gx + start * px:g} {y + r * px:g}h{w:g}v{px:g}h{-w:g}z")
                else:
                    c += 1
    return "".join(d)


def text(s, x, y, px, fill, shadow=None, off=None, cls="", center=False, extra=""):
    if center:
        x = x - text_width(s, px) / 2
    off = off if off is not None else px
    out = []
    c = f' class="{cls}"' if cls else ""
    out.append(f"<g{c}{extra}>")
    if shadow:
        out.append(f'<path fill="{shadow}" d="{text_path(s, x + off, y + off, px)}"/>')
    out.append(f'<path fill="{fill}" d="{text_path(s, x, y, px)}"/>')
    out.append("</g>")
    return "".join(out)


# --------------------------------------------------------------------------
# Sprites
# --------------------------------------------------------------------------
def sprite(rows, palette, x, y, px):
    """Render a list of strings as pixels; '.' is transparent."""
    by_color: dict[str, list[str]] = {}
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            k = row[c]
            if k == "." or k not in palette:
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == k:
                c += 1
            w = (c - start) * px
            by_color.setdefault(palette[k], []).append(
                f"M{x + start * px:g} {y + r * px:g}h{w:g}v{px:g}h{-w:g}z"
            )
    return "".join(f'<path fill="{col}" d="{"".join(ds)}"/>' for col, ds in by_color.items())


HERO_PAL = {
    "K": "#1b1b2f",  # outline
    "H": "#3b2a20",  # hair
    "h": "#5a4030",  # hair highlight
    "S": "#f2c49b",  # skin
    "s": "#d99b74",  # skin shade
    "E": "#1b1b2f",  # eye
    "R": RED,        # headphones
    "B": TEAL,       # hoodie
    "b": "#1f8f85",  # hoodie shade
    "P": "#3d405b",  # pants
    "W": "#f4f1de",  # shoes
}

HERO_TOP = [
    "....KKKKK...",
    "...KhHHHHK..",
    "..KRRHHHHHK.",
    ".KRHHHHHHHHK",
    ".KRRHSSSSHHK",
    ".KRRSSSSESSK",
    ".KRRSSSSESSK",
    "..KHSSSSSSsK",
    "...KKSSSSK..",
    "..KBBBBBBK..",
    ".KBBBBBBBBK.",
]
HERO_RUN_A = HERO_TOP + [
    ".KbBBBBBBSSK",
    "..KBBBBBBKK.",
    "..KPPKKPPK..",
    ".KPPK..KPPK.",
    ".KWWK...KWWK",
]
HERO_RUN_B = HERO_TOP + [
    ".KSSBBBBbBK.",
    "..KBBBBBBK..",
    "...KPPPPK...",
    "...KPPKPK...",
    "...KWWKWWK..",
]

BUG_PAL = {"K": "#1b1b2f", "G": "#7bd96b", "g": "#3f9e4d", "W": WHITE, "R": RED}
BUG_A = [
    ".K........K.",
    "..K......K..",
    "...KKKKKK...",
    "..KGGGGGGK..",
    ".KGWKGGWKGK.",
    "KGGGGGGGGGGK",
    "KgGgGgGgGgGK",
    ".KggggggggK.",
    ".K.K....K.K.",
]
BUG_B = BUG_A[:-1] + ["K..K....K..K"]

HEART = [
    ".RR.RR.",
    "RWRRRRR",
    "RRRRRRR",
    ".RRRRR.",
    "..RRR..",
    "...R...",
]
HEART_PAL = {"R": RED, "W": "#ffb3b8"}

COIN = [
    "..KKKK..",
    ".KYYYYK.",
    "KYYWYYOK",
    "KYYWYYOK",
    "KYYWYYOK",
    "KYYYYYOK",
    ".KOOOOK.",
    "..KKKK..",
]
COIN_PAL = {"K": "#5a3a10", "Y": YELLOW, "W": "#fff6c8", "O": ORANGE}

CHEST = [
    ".KKKKKKKKKK.",
    "KOOOOOOOOOOK",
    "KOooooooooOK",
    "KOooooooooOK",
    "KKKKKYYKKKKK",
    "KOOOOYYOOOOK",
    "KOoooKKoooOK",
    "KOooooooooOK",
    "KOooooooooOK",
    "KOOOOOOOOOOK",
    "KKKKKKKKKKKK",
]
CHEST_PAL = {"K": "#2a160a", "O": "#c47a2c", "o": "#8a4f1f", "Y": YELLOW}

SCROLL = [
    ".KKKKKKKKKK.",
    "KppKPPPPPPPK",
    "KpKPPPPPPPPK",
    ".KPLLLLLLPK.",
    ".KPPPPPPPPK.",
    ".KPLLLLLPPK.",
    ".KPPPPPPPPK.",
    ".KPLLLLLLPK.",
    ".KPPPPPPPPK.",
    "KKKKKKKKKKKK",
    "KpppppppppK.",
    ".KKKKKKKKK..",
]
SCROLL_PAL = {"K": "#3a2412", "P": "#f3dfb0", "p": "#d9b77a", "L": "#a0784a"}

JOYSTICK = [
    "....KKKK....",
    "...KRRRRK...",
    "...KRWRRK...",
    "...KRRRRK...",
    "....KKKK....",
    ".....KK.....",
    ".....KK.....",
    "..KKKKKKKK..",
    ".KGGGGGGGGK.",
    "KGYGGGGGBGGK",
    "KGGGGGGGGGGK",
    "KKKKKKKKKKKK",
]
JOY_PAL = {"K": "#1b1b2f", "R": RED, "W": "#ffb3b8", "G": "#6b7090", "Y": YELLOW, "B": BLUE}

NOTE = [
    "..###",
    "..#.#",
    "..#..",
    "..#..",
    "###..",
    "###..",
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def svg_doc(w, h, body, css, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" shape-rendering="crispEdges" role="img" aria-label="{title}">'
        f"<title>{title}</title><style>{css}</style>{body}</svg>\n"
    )


def pixel_frame(x, y, w, h, fill=NAVY, outer=FRAME, inner=FRAME2, b=4):
    """A JRPG-style window with notched pixel corners."""
    return (
        # outer light border with notched corners
        f'<path fill="{outer}" d="M{x + b} {y}h{w - 2 * b}v{b}h{b}v{h - 2 * b}h{-b}v{b}'
        f'h{-(w - 2 * b)}v{-b}h{-b}v{-(h - 2 * b)}h{b}z"/>'
        f'<rect x="{x + b}" y="{y + b}" width="{w - 2 * b}" height="{h - 2 * b}" fill="{INK}"/>'
        f'<rect x="{x + 2 * b}" y="{y + 2 * b}" width="{w - 4 * b}" height="{h - 4 * b}" fill="{inner}"/>'
        f'<rect x="{x + 3 * b}" y="{y + 3 * b}" width="{w - 6 * b}" height="{h - 6 * b}" fill="{fill}"/>'
    )


# --------------------------------------------------------------------------
# 1. Banner
# --------------------------------------------------------------------------
def banner():
    W, H = 960, 320
    GROUND = 256
    rnd = random.Random(1993)
    b = []

    # banded night sky
    bands = ["#0b0d26", "#0f1131", "#14143b", "#1a1745", "#211a4f", "#2a1d58", "#341f5f", "#402266"]
    bh = GROUND / len(bands)
    for i, c in enumerate(bands):
        b.append(f'<rect x="0" y="{i * bh:g}" width="{W}" height="{bh + 1:g}" fill="{c}"/>')

    # stars
    for i in range(70):
        sx, sy = rnd.randrange(0, W, 4), rnd.randrange(0, 200, 4)
        size = rnd.choice([4, 4, 4, 8])
        cls = f"tw tw{i % 4}"
        col = rnd.choice([WHITE, "#cfd6ff", "#fff1b8"])
        if size == 8:
            b.append(
                f'<path class="{cls}" fill="{col}" d="M{sx + 4} {sy}h4v4h4v4h-4v4h-4v-4h-4v-4h4z"/>'
            )
        else:
            b.append(f'<rect class="{cls}" x="{sx}" y="{sy}" width="4" height="4" fill="{col}"/>')

    # moon
    moon = [
        "...####...",
        ".########.",
        ".####.###.",
        "##########",
        "#######.##",
        "###.######",
        "##########",
        ".########.",
        ".###.####.",
        "...####...",
    ]
    b.append(sprite(moon, {"#": "#f4e9c1"}, 872, 84, 6))

    # far hills (slow parallax), first screen repeated so the loop is seamless
    hd = []
    r = random.Random(7)
    h = 40
    cols = []
    for x in range(0, W, 16):
        h = max(16, min(72, h + r.choice([-8, -4, 0, 4, 8])))
        cols.append((x, h))
    for off in (0, W):
        for x, h in cols:
            hd.append(f"M{x + off} {GROUND - h}h16v{h}h-16z")
    b.append(f'<g class="hills"><path fill="#2a1f55" d="{"".join(hd)}"/></g>')

    # city skyline (mid parallax) with windows
    sky = []
    lit = []
    blink = []
    r = random.Random(42)
    x = 0
    buildings = []
    while x < W:
        bw = r.choice([40, 48, 56, 64, 72])
        bh2 = r.choice([48, 64, 72, 88, 104, 120])
        buildings.append((x, bw, bh2))
        x += bw + r.choice([0, 8, 16])
    # window state: 0 = dark, 1 = lit, 2 = blinking (decided once, drawn twice)
    windows = []
    for bx, bw, bh2 in buildings:
        bw = min(bw, W - bx)
        for wy in range(GROUND - bh2 + 8, GROUND - 8, 12):
            for wx in range(bx + 8, bx + bw - 8, 12):
                roll = r.random()
                windows.append((wx, wy, 2 if roll < 0.05 else (1 if roll < 0.35 else 0)))
    for off in (0, W):
        for bx, bw, bh2 in buildings:
            bw = min(bw, W - bx)
            sky.append(f"M{bx + off} {GROUND - bh2}h{bw}v{bh2}h{-bw}z")
        for wx, wy, st in windows:
            if st == 1:
                lit.append(f"M{wx + off} {wy}h4v4h-4z")
            elif st == 2:
                blink.append(f"M{wx + off} {wy}h4v4h-4z")
    b.append(
        '<g class="city">'
        f'<path fill="#1a1338" d="{"".join(sky)}"/>'
        f'<path fill="{YELLOW}" opacity=".85" d="{"".join(lit)}"/>'
        f'<path class="winblink" fill="{CYAN}" d="{"".join(blink)}"/>'
        "</g>"
    )

    # ground (fast scroll, 32px tile)
    g = []
    g.append(f'<rect x="0" y="{GROUND}" width="{W + 64}" height="{H - GROUND}" fill="#6b3f22"/>')
    g.append(f'<rect x="0" y="{GROUND}" width="{W + 64}" height="8" fill="#7bd96b"/>')
    g.append(f'<rect x="0" y="{GROUND + 8}" width="{W + 64}" height="8" fill="#3f9e4d"/>')
    dark, light = [], []
    for tx in range(0, W + 64, 32):
        dark.append(f"M{tx} {GROUND + 16}h4v{H - GROUND - 16}h-4z")
        dark.append(f"M{tx + 8} {GROUND + 28}h8v4h-8z M{tx + 20} {GROUND + 44}h8v4h-8z")
        light.append(f"M{tx + 12} {GROUND + 20}h4v4h-4z M{tx + 24} {GROUND + 36}h4v4h-4z")
        light.append(f"M{tx + 4} {GROUND + 52}h4v4h-4z")
        dark.append(f"M{tx + 16} {GROUND + 8}h4v4h-4z")
    g.append(f'<path fill="#54301a" d="{"".join(dark)}"/>')
    g.append(f'<path fill="#8a5530" d="{"".join(light)}"/>')
    b.append(f'<g class="ground">{"".join(g)}</g>')

    # HUD
    b.append(text("1P STEVEN", 24, 20, 3, WHITE, INK))
    b.append(text("SCORE 001993", 24, 48, 2, CYAN, INK))
    for i in range(3):
        b.append(f'<g class="hb">{sprite(HEART, HEART_PAL, W - 120 + i * 32, 22, 4)}</g>')
    b.append(text("LIFE", W - 120, 52, 2, GRAY, INK))

    # title
    b.append(text("WELCOME TO", W / 2, 34, 3, CYAN, INK, center=True))
    title = "STEVEN HUR"
    tpx = 9
    tx = W / 2 - text_width(title, tpx) / 2
    b.append(
        '<defs><linearGradient id="tg" x1="0" y1="66" x2="0" y2="129" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff6c8"/><stop offset=".29" stop-color="#fff6c8"/>'
        f'<stop offset=".29" stop-color="{YELLOW}"/><stop offset=".58" stop-color="{YELLOW}"/>'
        f'<stop offset=".58" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}"/>'
        "</linearGradient></defs>"
    )
    b.append(f'<path fill="{RED}" d="{text_path(title, tx + 6, 66 + 6, tpx)}"/>')
    b.append(f'<path fill="{INK}" d="{text_path(title, tx + 10, 66 + 10, tpx)}" opacity=".6"/>')
    b.append(f'<path fill="url(#tg)" d="{text_path(title, tx, 66, tpx)}"/>')
    b.append(text("JONG WAN HUR  -  MACHINE LEARNING ENGINEER", W / 2, 146, 3, WHITE, INK, center=True))
    b.append(text("} PRESS START", W / 2, 184, 3, YELLOW, INK, cls="blink", center=True))

    # hero: runs in place, jumps on the bug
    hx, hy = 96, GROUND - 16 * 5
    b.append(
        '<g class="hero">'
        f'<g class="fa">{sprite(HERO_RUN_A, HERO_PAL, hx, hy, 5)}</g>'
        f'<g class="fb">{sprite(HERO_RUN_B, HERO_PAL, hx, hy, 5)}</g>'
        "</g>"
    )
    # bug enemy walks in from the right
    bx, by = 0, GROUND - 9 * 5
    b.append(
        '<g class="bug"><g class="squash">'
        f'<g class="fa">{sprite(BUG_A, BUG_PAL, bx, by, 5)}</g>'
        f'<g class="fb">{sprite(BUG_B, BUG_PAL, bx, by, 5)}</g>'
        "</g></g>"
    )
    b.append(text("BUG FIXED!", 176, 188, 3, GREEN, INK, cls="pop"))
    b.append(text("+100 EXP", 176, 216, 2, YELLOW, INK, cls="pop"))

    css = f"""
.tw{{animation:tw 3s steps(1) infinite}}
.tw1{{animation-delay:-.7s}}.tw2{{animation-delay:-1.4s;animation-duration:2.2s}}.tw3{{animation-delay:-2.1s;animation-duration:4s}}
@keyframes tw{{0%,100%{{opacity:1}}50%{{opacity:.15}}}}
.winblink{{animation:tw 1.6s steps(1) infinite}}
.hills{{animation:scroll 60s linear infinite}}
.city{{animation:scroll 30s linear infinite}}
@keyframes scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}
.ground{{animation:gscroll .25s linear infinite}}
@keyframes gscroll{{from{{transform:translateX(0)}}to{{transform:translateX(-32px)}}}}
.blink{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
.hb{{animation:beat 1.2s steps(1) infinite}}
@keyframes beat{{0%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
.fa{{animation:fa .3s steps(1) infinite}}
.fb{{animation:fb .3s steps(1) infinite}}
@keyframes fa{{0%{{opacity:1}}50%{{opacity:0}}}}
@keyframes fb{{0%{{opacity:0}}50%{{opacity:1}}}}
.hero{{animation:jump 5s infinite}}
@keyframes jump{{
 0%,62%{{transform:translateY(0);animation-timing-function:cubic-bezier(.2,.7,.4,1)}}
 71%{{transform:translateY(-84px);animation-timing-function:cubic-bezier(.6,0,.8,.3)}}
 80%,100%{{transform:translateY(0)}}}}
.bug{{animation:walk 5s linear infinite}}
@keyframes walk{{0%{{transform:translateX({W + 16}px)}}80%,100%{{transform:translateX(96px)}}}}
.squash{{transform-box:fill-box;transform-origin:50% 100%;animation:squash 5s infinite}}
@keyframes squash{{0%,79%{{transform:scaleY(1);opacity:1}}82%{{transform:scaleY(.25);opacity:1}}90%,100%{{transform:scaleY(.25);opacity:0}}}}
.pop{{opacity:0;animation:pop 5s infinite}}
@keyframes pop{{0%,79%{{opacity:0;transform:translateY(0)}}82%{{opacity:1}}95%{{opacity:1;transform:translateY(-24px)}}100%{{opacity:0;transform:translateY(-24px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.fb,.pop{{opacity:0}}.bug{{transform:translateX(640px)}}}}
"""
    return svg_doc(W, H, "".join(b), css, "Steven Hur - Machine Learning Engineer")


# --------------------------------------------------------------------------
# 2. Status window + dialog
# --------------------------------------------------------------------------
def status():
    W, H = 960, 480
    b = []
    b.append(pixel_frame(0, 0, W, H))

    # portrait
    px0, py0 = 40, 44
    b.append(pixel_frame(px0, py0, 176, 176, fill="#2b2f6b"))
    face_px = 12
    fx = px0 + (176 - 12 * face_px) / 2
    fy = py0 + 22
    face = [row for row in HERO_TOP[:9]]
    face_closed = [r.replace("E", "S") for r in face]
    face_closed[6] = face[6]  # keep lower eye pixel = closed eye line
    b.append(sprite(face_closed, HERO_PAL, fx, fy, face_px))
    b.append(f'<g class="eye"><rect x="{fx + 8 * face_px}" y="{fy + 5 * face_px}" width="{face_px}" '
             f'height="{face_px}" fill="#1b1b2f"/></g>')
    # floating music notes from the headphones
    for i, (nx, delay) in enumerate([(px0 + 22, 0), (px0 + 40, 1.3)]):
        b.append(f'<g class="note" style="animation-delay:-{delay}s">'
                 f'{sprite(NOTE, {"#": CYAN if i else YELLOW}, nx, py0 + 60, 4)}</g>')

    # info
    ix = 248
    rows = [("NAME", "JONG WAN HUR"), ("ALIAS", "STEVEN HUR"), ("CLASS", "ML ENGINEER"), ("GUILD", "OPEN SOURCE")]
    for i, (k, v) in enumerate(rows):
        y = 56 + i * 40
        b.append(text(k, ix, y, 3, GRAY, INK))
        b.append(text(v, ix + 108, y, 3, WHITE, INK))

    # bars
    bx, bw, bh = 676, 240, 20
    bars = [("HP", GREEN, "full"), ("MP", BLUE, "full"), ("XP", YELLOW, "xp")]
    for i, (label, col, kind) in enumerate(bars):
        y = 54 + i * 40
        b.append(text(label, bx - 52, y + 0, 3, WHITE, INK))
        b.append(f'<rect x="{bx - 4}" y="{y - 4}" width="{bw + 8}" height="{bh + 8}" fill="{FRAME}"/>')
        b.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" fill="{INK}"/>')
        cls = ' class="xpfill"' if kind == "xp" else ""
        b.append(f'<rect{cls} x="{bx}" y="{y}" width="{bw}" height="{bh}" fill="{col}"/>')
        b.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="4" fill="{WHITE}" opacity=".35"/>')
    b.append(text("COFFEE", bx + bw - 8 - text_width("COFFEE", 2), 54 + 40 + 3, 2, WHITE, INK))
    b.append(text("LEVEL UP!", bx + bw / 2, 54 + 80 + 34, 3, YELLOW, RED, cls="lvl", center=True))

    # dialog box with nameplate
    dy = 256
    b.append(pixel_frame(24, dy, W - 48, H - dy - 24, fill="#101330"))
    b.append(pixel_frame(48, dy - 26, 176, 52, fill=RED, inner=FRAME))
    b.append(text("STEVEN", 48 + 88, dy - 11, 3, WHITE, INK, center=True))
    lines = [
        "WELCOME TO MY GITHUB, TRAVELER!",
        "I'M A HARDWORKING MACHINE LEARNING ENGINEER",
        "WHO LOVES TURNING DATA INTO RELIABLE,",
        "HIGH-PERFORMANCE INTELLIGENT SYSTEMS.",
    ]
    lx, ly0, lh, lpx = 64, dy + 44, 34, 3
    covers = []
    css_lines = []
    cycle = 16.0
    per_char = 0.045
    t = 0.3
    for i, line in enumerate(lines):
        y = ly0 + i * lh
        b.append(text(line, lx, y, lpx, WHITE if i else YELLOW, INK))
        n = len(line)
        wpx = n * CELL * lpx
        start = t / cycle * 100
        end = (t + n * per_char) / cycle * 100
        t += n * per_char + 0.25
        covers.append(
            f'<rect class="tc{i}" x="{lx - 4}" y="{y - 4}" width="{wpx + 12}" height="{lh}" fill="#101330"/>'
        )
        css_lines.append(
            f".tc{i}{{animation:tc{i} {cycle}s infinite}}"
            f"@keyframes tc{i}{{0%,{start:.2f}%{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{end:.2f}%,97%{{transform:translateX({wpx}px)}}100%{{transform:translateX(0)}}}}"
        )
    b.append('<defs><clipPath id="dclip"><rect x="40" y="%d" width="%d" height="%d"/></clipPath></defs>'
             % (dy + 16, W - 80, H - dy - 56))
    b.append(f'<g clip-path="url(#dclip)">{"".join(covers)}</g>')
    b.append(text("~", W - 88, H - 80, 4, YELLOW, INK, cls="arrow"))

    done = t / cycle * 100
    css = (
        "".join(css_lines)
        + f"""
.eye{{animation:eye 4s steps(1) infinite}}
@keyframes eye{{0%,90%{{opacity:1}}93%{{opacity:0}}97%{{opacity:1}}}}
.note{{opacity:0;animation:note 2.6s linear infinite}}
@keyframes note{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:1}}80%{{opacity:1}}100%{{opacity:0;transform:translate(-12px,-56px)}}}}
.xpfill{{transform-box:fill-box;transform-origin:0 0;animation:xp 6s infinite}}
@keyframes xp{{0%{{transform:scaleX(.05);animation-timing-function:steps(24,end)}}70%,100%{{transform:scaleX(1)}}}}
.lvl{{opacity:0;animation:lvl 6s steps(1) infinite}}
@keyframes lvl{{0%,70%{{opacity:0}}72%{{opacity:1}}78%{{opacity:0}}82%{{opacity:1}}88%{{opacity:0}}92%,100%{{opacity:1}}}}
.arrow{{opacity:0;animation:arrow {cycle}s infinite}}
@keyframes arrow{{0%,{done:.2f}%{{opacity:0;transform:translateY(0)}}{done + .1:.2f}%,{done + 3:.2f}%,{done + 9:.2f}%,{done + 15:.2f}%,{done + 21:.2f}%{{opacity:1;transform:translateY(0)}}{done + 1.5:.2f}%,{done + 7.5:.2f}%,{done + 13.5:.2f}%,{done + 19.5:.2f}%{{opacity:1;transform:translateY(4px)}}97%{{opacity:1}}100%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}[class^=tc]{{display:none}}.lvl{{opacity:1}}.note{{opacity:0}}}}
"""
    )
    return svg_doc(W, H, "".join(b), css, "Player status: Jong Wan Hur (Steven), Machine Learning Engineer")


# --------------------------------------------------------------------------
# 3. Section headers
# --------------------------------------------------------------------------
def header(label, sub, icon, pal):
    W, H = 960, 72
    b = [pixel_frame(0, 0, W, H, fill=NAVY2)]
    b.append(f'<g class="bob">{sprite(icon, pal, 24, (H - len(icon) * 4) / 2, 4)}</g>')
    b.append(text("}", 88, 22, 4, YELLOW, INK, cls="blink"))
    b.append(text(label, 120, 22, 4, WHITE, INK))
    b.append(text(sub, W - 28 - text_width(sub, 2), 30, 2, CYAN, INK))
    css = """
.blink{animation:blink 1s steps(1) infinite}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
.bob{animation:bob 1.2s steps(1) infinite}
@keyframes bob{0%{transform:translateY(0)}50%{transform:translateY(-4px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
    return svg_doc(W, H, "".join(b), css, label.title())


# --------------------------------------------------------------------------
# 4. Footer
# --------------------------------------------------------------------------
def footer():
    W, H = 960, 200
    b = [pixel_frame(0, 0, W, H)]
    b.append(text("THANKS FOR PLAYING!", W / 2, 36, 5, YELLOW, RED, center=True))
    cont = "CONTINUE?"
    cx = W / 2 - text_width(cont + " 9", 4) / 2
    b.append(text(cont, cx, 100, 4, WHITE, INK))
    dx = cx + len(cont + " ") * CELL * 4
    css = []
    for i, d in enumerate("9876543210"):
        a, z = i * 10, (i + 1) * 10
        b.append(text(d, dx, 100, 4, RED, INK, cls=f"d{i}"))
        css.append(
            f".d{i}{{opacity:0;animation:d{i} 10s steps(1) infinite}}"
            f"@keyframes d{i}{{0%{{opacity:{1 if i == 0 else 0}}}"
            + (f"{a}%{{opacity:1}}" if i else "")
            + f"{z}%{{opacity:0}}}}"
        )
    b.append(text("INSERT COIN", W / 2, 152, 3, CYAN, INK, cls="blink", center=True))
    for i, x in enumerate((96, W - 96 - 48)):
        b.append(f'<g class="coin" style="animation-delay:-{i * .3}s">{sprite(COIN, COIN_PAL, x, 76, 6)}</g>')
    css.append("""
.blink{animation:blink 1s steps(1) infinite}
@keyframes blink{0%{opacity:1}50%{opacity:0}}
.coin{transform-box:fill-box;transform-origin:50% 50%;animation:spin .8s steps(1) infinite}
@keyframes spin{0%{transform:scaleX(1)}25%{transform:scaleX(.6)}50%{transform:scaleX(.2)}75%{transform:scaleX(.6)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.d0{opacity:1}}
""")
    return svg_doc(W, H, "".join(b), "".join(css), "Thanks for playing")


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "banner.svg": banner(),
        "status.svg": status(),
        "header-inventory.svg": header("INVENTORY", "ITEMS: 14", CHEST, CHEST_PAL),
        "header-quests.svg": header("QUEST LOG", "CLEARED: 5  ACTIVE: 2", SCROLL, SCROLL_PAL),
        "header-battle.svg": header("BATTLE LOG", "CONTRIBUTIONS.EXE", JOYSTICK, JOY_PAL),
        "footer.svg": footer(),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg)
        print(f"wrote assets/{name} ({len(svg) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
