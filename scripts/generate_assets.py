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
    "$": "..... ..#.. .###. ##### .###. .#.#. .....",  # star
    "[": ".###. .#... .#... .#... .#... .#... .###.",
    "]": ".###. ...#. ...#. ...#. ...#. ...#. .###.",
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

    # title
    b.append(text("WELCOME TO", W / 2, 28, 3, CYAN, INK, center=True))
    title = "STEVEN HUR"
    tpx = 11
    ty = 66
    tx = W / 2 - text_width(title, tpx) / 2
    b.append(
        f'<defs><linearGradient id="tg" x1="0" y1="{ty}" x2="0" y2="{ty + 7 * tpx}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff6c8"/><stop offset=".29" stop-color="#fff6c8"/>'
        f'<stop offset=".29" stop-color="{YELLOW}"/><stop offset=".58" stop-color="{YELLOW}"/>'
        f'<stop offset=".58" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ORANGE}"/>'
        "</linearGradient></defs>"
    )
    b.append(f'<path fill="{RED}" d="{text_path(title, tx + 6, ty + 6, tpx)}"/>')
    b.append(f'<path fill="{INK}" d="{text_path(title, tx + 10, ty + 10, tpx)}" opacity=".6"/>')
    b.append(f'<path fill="url(#tg)" d="{text_path(title, tx, ty, tpx)}"/>')
    b.append(text("SOFTWARE ENGINEER", W / 2, 162, 4, WHITE, INK, center=True))
    b.append(text("} PRESS START", W / 2, 214, 3, YELLOW, INK, cls="blink", center=True))

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
    b.append(text("BUG FIXED!", 172, 206, 2, GREEN, INK, cls="pop"))
    b.append(text("+100 EXP", 172, 226, 2, YELLOW, INK, cls="pop"))

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
@keyframes pop{{0%,79%{{opacity:0;transform:translateY(0)}}82%{{opacity:1}}95%{{opacity:1;transform:translateY(-8px)}}100%{{opacity:0;transform:translateY(-8px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.fb,.pop{{opacity:0}}.bug{{transform:translateX(640px)}}}}
"""
    return svg_doc(W, H, "".join(b), css, "Steven Hur - Software Engineer")


# --------------------------------------------------------------------------
# 2. Welcome scene: my character as an NPC + dialog box
# --------------------------------------------------------------------------
def _npc_frames():
    base = [
        "....KKKKK.......",
        "...KhHHHHK......",
        "..KRRHHHHHK.....",
        ".KRHHHHHHHHK....",
        ".KRRHSSSSHHK....",
        ".KRRSSSSSSSK....",  # row 5: open-eye pixel is a separate blinking overlay
        ".KRRSSSSESSK....",  # row 6: eye (doubles as the closed-eye line)
        "..KHSSSSSSsK....",
        "...KKSSSSK......",
        "..KBBBBBBK......",
        ".KBBBBBBBBK.....",
        ".KbBBBBBBbK.....",
        ".KSBBBBBBSK.....",
        "..KPPPPPPK......",
        "..KPPKKPPK......",
        "..KWWK.KWWK.....",
    ]

    def wave(hand):
        rows = list(base)
        for r, suffix in hand.items():
            rows[r] = rows[r][:12] + suffix
        rows[8] = "...KKSSSSKKBK..."
        rows[9] = "..KBBBBBBBBK...."
        rows[12] = ".KSBBBBBBBK....."
        return rows

    wave_a = wave({2: "..K.", 3: ".KSK", 4: ".KSK", 5: "KBK.", 6: "KBK.", 7: "BK.."})
    wave_b = wave({2: ".K..", 3: "KSK.", 4: "KSK.", 5: "BK..", 6: "BK..", 7: "BK.."})
    return base, wave_a, wave_b


TREE = [
    ".....KKKK.....",
    "...KKLLLLKK...",
    "..KLLLGGLLLK..",
    ".KLLGGGGGGLLK.",
    ".KLGGGGGGGGGK.",
    "KLGGGGLGGGGGDK",
    "KGGGGLLLGGGGDK",
    "KGGGGGGGGGGDDK",
    "KGGGGGGGGGDDDK",
    ".KDGGGGGGDDDK.",
    ".KDDDGGDDDDDK.",
    "..KKDDDDDDKK..",
    "....KKTtKK....",
    ".....KTtK.....",
    ".....KTtK.....",
    ".....KTtK.....",
    "....KTTttK....",
    "...KKKKKKKK...",
]
TREE_PAL = {"K": "#1f4a2a", "L": "#7bd96b", "G": "#3f9e4d", "D": "#2f7d3c", "T": "#8a5530", "t": "#54301a"}

CLOUD = [
    "....WWWW........",
    "..WWWWWWWW.WWW..",
    ".WWWWWWWWWWWWWW.",
    "WWWWWWWWWWWWWWWW",
    "BWWWWWWWWWWWWWWB",
    ".BBBBBBBBBBBBBB.",
]
CLOUD_PAL = {"W": WHITE, "B": "#d6ecfb"}

FLOWER = [".R.", "RYR", ".g."]
BUTTERFLY_A = ["W.K.W", "WWKWW", ".WKW."]
BUTTERFLY_B = ["..K..", ".WKW.", "..K.."]


def welcome():
    W, H = 960, 552
    HORIZON = 216
    dy = 320  # dialog box top
    b = []
    b.append(pixel_frame(0, 0, W, H))
    b.append(f'<defs><clipPath id="scene"><rect x="12" y="12" width="{W - 24}" height="{H - 24}"/></clipPath></defs>')
    b.append('<g clip-path="url(#scene)">')

    # daytime sky
    bands = ["#5fb6f5", "#6fc1f7", "#82cbf8", "#97d5fa", "#aee0fb", "#c6eafc"]
    bh = (HORIZON - 12) / len(bands)
    for i, c in enumerate(bands):
        b.append(f'<rect x="0" y="{12 + i * bh:g}" width="{W}" height="{bh + 1:g}" fill="{c}"/>')
    sun = ["..YYYY..", ".YYYYYY.", "YYYYYYYY", "YYYYYYYY", "YYYYYYYY", "YYYYYYYY", ".YYYYYY.", "..YYYY.."]
    b.append(f'<g class="glow">{sprite(sun, {"Y": "#fff6c8"}, 812, 28, 10)}</g>')
    b.append(sprite(sun, {"Y": YELLOW}, 824, 40, 7))

    # drifting clouds (two copies for a seamless loop)
    clouds = []
    for off in (0, W):
        for cx, cy, s in [(80, 48, 6), (400, 92, 5), (640, 36, 4)]:
            clouds.append(sprite(CLOUD, CLOUD_PAL, cx + off, cy, s))
    b.append(f'<g class="clouds">{"".join(clouds)}</g>')

    # stepped hills
    r = random.Random(11)
    for color, lo, hi, step in [("#8fd3a0", 32, 72, 32), ("#6dbf7e", 12, 40, 24)]:
        d, h = [], (lo + hi) // 2
        for x in range(0, W, step):
            h = max(lo, min(hi, h + r.choice([-8, 0, 8])))
            d.append(f"M{x} {HORIZON - h}h{step}v{h}h{-step}z")
        b.append(f'<path fill="{color}" d="{"".join(d)}"/>')

    # grass field with checker tiles and tufts
    b.append(f'<rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="#5ad16a"/>')
    tiles, tufts = [], []
    for ty in range(HORIZON, H, 32):
        for tx in range(0, W, 32):
            if (tx // 32 + ty // 32) % 2:
                tiles.append(f"M{tx} {ty}h32v32h-32z")
    for _ in range(40):
        gx, gy = r.randrange(0, W, 4), r.randrange(HORIZON + 8, dy, 4)
        tufts.append(f"M{gx} {gy}h4v4h-4z M{gx + 8} {gy - 4}h4v8h-4z")
    b.append(f'<path fill="#52c463" d="{"".join(tiles)}"/>')
    b.append(f'<path fill="#3f9e4d" d="{"".join(tufts)}"/>')

    # trees and signpost
    b.append(sprite(TREE, TREE_PAL, 560, 262 - 18 * 6, 6))
    b.append(sprite(TREE, TREE_PAL, 830, 280 - 18 * 7, 7))
    b.append(sprite(TREE, TREE_PAL, 470, 240 - 18 * 4, 4))
    sx, sy = 676, 200
    b.append(f'<rect x="{sx + 20}" y="{sy + 44}" width="12" height="52" fill="#54301a"/>')
    b.append(f'<rect x="{sx + 104}" y="{sy + 44}" width="12" height="52" fill="#54301a"/>')
    b.append(f'<rect x="{sx}" y="{sy}" width="136" height="52" fill="#2a160a"/>')
    b.append(f'<rect x="{sx + 4}" y="{sy + 4}" width="128" height="44" fill="#c47a2c"/>')
    b.append(f'<rect x="{sx + 4}" y="{sy + 40}" width="128" height="8" fill="#8a4f1f"/>')
    b.append(text("GITHUB", sx + 68, sy + 14, 3, "#2a160a", center=True))

    # flowers swaying
    for i, (fx, fy) in enumerate([(300, 240), (348, 268), (420, 292), (640, 300), (740, 250), (900, 300), (40, 246), (520, 284)]):
        col = [RED, WHITE, "#ff9ecb", YELLOW][i % 4]
        b.append(f'<g class="sway s{i % 2}">{sprite(FLOWER, {"R": col, "Y": YELLOW if col != YELLOW else ORANGE, "g": "#2f7d3c"}, fx, fy, 6)}</g>')

    # butterflies
    for i, delay in enumerate((0, 6)):
        pal = {"W": "#ff9ecb" if i == 0 else "#fff6c8", "K": "#1b1b2f"}
        b.append(
            f'<g class="fly" style="animation-delay:-{delay}s"><g class="flap">'
            f'<g class="fa">{sprite(BUTTERFLY_A, pal, 0, 0, 4)}</g>'
            f'<g class="fb">{sprite(BUTTERFLY_B, pal, 0, 0, 4)}</g></g></g>'
        )

    # NPC (me): idles, blinks and waves at visitors
    base, wave_a, wave_b = _npc_frames()
    S = 8
    nx, ny = 104, dy - 28 - 16 * S
    b.append(f'<rect x="{nx + 8}" y="{ny + 16 * S - 8}" width="{10 * S}" height="12" fill="#3f9e4d"/>')
    b.append('<g class="bob">')
    b.append(f'<g class="idle">{sprite(base, HERO_PAL, nx, ny, S)}</g>')
    b.append(f'<g class="wa">{sprite(wave_a, HERO_PAL, nx, ny, S)}</g>')
    b.append(f'<g class="wb">{sprite(wave_b, HERO_PAL, nx, ny, S)}</g>')
    b.append(f'<rect class="eye" x="{nx + 8 * S}" y="{ny + 5 * S}" width="{S}" height="{S}" fill="#1b1b2f"/>')
    b.append("</g>")
    for i, delay in enumerate((0, 1.3)):
        b.append(f'<g class="note" style="animation-delay:-{delay}s">'
                 f'{sprite(NOTE, {"#": CYAN if i else YELLOW}, nx + 4 + i * 14, ny + 20, 4)}</g>')

    # speech bubble
    bx, by, bw, bh = nx + 16 * S + 8, ny - 44, 112, 52
    b.append(
        '<g class="bubble">'
        f'<rect x="{bx}" y="{by + 4}" width="{bw}" height="{bh - 8}" fill="{INK}"/>'
        f'<rect x="{bx + 4}" y="{by}" width="{bw - 8}" height="{bh}" fill="{INK}"/>'
        f'<rect x="{bx + 4}" y="{by + 4}" width="{bw - 8}" height="{bh - 8}" fill="{WHITE}"/>'
        f'<path fill="{INK}" d="M{bx} {by + bh}h16v-4h-12v12h-4z M{bx - 8} {by + bh + 8}h8v4h-8z"/>'
        f'<path fill="{WHITE}" d="M{bx + 4} {by + bh - 4}h8v4h-4v4h-4z"/>'
        + text("HI!", bx + bw / 2, by + 12, 4, RED, center=True)
        + "</g>"
    )
    b.append("</g>")  # end scene clip

    # dialog box with nameplate
    b.append(pixel_frame(24, dy, W - 48, H - dy - 24, fill="#101330"))
    b.append(pixel_frame(48, dy - 26, 176, 52, fill=RED, inner=FRAME))
    b.append(text("STEVEN", 48 + 88, dy - 11, 3, WHITE, INK, center=True))
    lines = [
        "WELCOME TO MY GITHUB, TRAVELER!",
        "I'M A HARDWORKING SOFTWARE ENGINEER",
        "WHO LOVES TURNING DATA INTO RELIABLE,",
        "HIGH-PERFORMANCE INTELLIGENT SYSTEMS.",
    ]
    lx, ly0, lh, lpx = 64, dy + 40, 34, 3
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
    b.append(text("~", W - 88, H - 72, 4, YELLOW, INK, cls="arrow"))

    # wave twice every 4s, idle the rest of the time
    def frames(on):
        ks = []
        for k in range(9):
            ks.append(f"{k * 5}%{{opacity:{1 if (k < 8 and k % 2 == on) else 0}}}")
        return "".join(ks)

    idle_k = "0%{opacity:0}40%{opacity:1}"
    done = t / cycle * 100
    css = (
        "".join(css_lines)
        + f"""
.idle,.wa,.wb{{animation-duration:4s;animation-iteration-count:infinite;animation-timing-function:step-end}}
.idle{{animation-name:idle}}.wa{{animation-name:wa}}.wb{{animation-name:wb}}
@keyframes idle{{{idle_k}}}@keyframes wa{{{frames(0)}}}@keyframes wb{{{frames(1)}}}
.bob{{animation:bob 1.2s steps(1) infinite}}
@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(4px)}}}}
.eye{{animation:eye 4s steps(1) infinite}}
@keyframes eye{{0%,88%{{opacity:1}}92%{{opacity:0}}96%{{opacity:1}}}}
.bubble{{animation:bub 1s steps(1) infinite}}
@keyframes bub{{0%{{transform:translateY(0)}}50%{{transform:translateY(-4px)}}}}
.note{{opacity:0;animation:note 2.6s linear infinite}}
@keyframes note{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:1}}80%{{opacity:1}}100%{{opacity:0;transform:translate(-16px,-56px)}}}}
.clouds{{animation:drift 90s linear infinite}}
@keyframes drift{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}
.glow{{animation:glow 2s steps(1) infinite}}
@keyframes glow{{0%{{opacity:.9}}50%{{opacity:.5}}}}
.sway{{animation:sway 1.6s steps(1) infinite}}.s1{{animation-delay:-.8s}}
@keyframes sway{{0%{{transform:translateX(0)}}50%{{transform:translateX(4px)}}}}
.fa{{animation:fa .3s steps(1) infinite}}.fb{{animation:fb .3s steps(1) infinite}}
@keyframes fa{{0%{{opacity:1}}50%{{opacity:0}}}}@keyframes fb{{0%{{opacity:0}}50%{{opacity:1}}}}
.fly{{animation:fly 12s steps(48) infinite}}
@keyframes fly{{0%{{transform:translate(260px,150px)}}25%{{transform:translate(380px,110px)}}50%{{transform:translate(520px,170px)}}75%{{transform:translate(400px,200px)}}100%{{transform:translate(260px,150px)}}}}
.arrow{{opacity:0;animation:arrow {cycle}s infinite}}
@keyframes arrow{{0%,{done:.2f}%{{opacity:0;transform:translateY(0)}}{done + .1:.2f}%,{done + 3:.2f}%,{done + 9:.2f}%,{done + 15:.2f}%,{done + 21:.2f}%{{opacity:1;transform:translateY(0)}}{done + 1.5:.2f}%,{done + 7.5:.2f}%,{done + 13.5:.2f}%,{done + 19.5:.2f}%{{opacity:1;transform:translateY(4px)}}97%{{opacity:1}}100%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}[class^=tc]{{display:none}}.idle,.wb,.note{{opacity:0}}.fly{{transform:translate(380px,120px)}}.fb{{opacity:0}}}}
"""
    )
    return svg_doc(W, H, "".join(b), css, "Steven, my pixel character, welcomes visitors to my GitHub")


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


# --------------------------------------------------------------------------
# 5. Inventory icons missing from skillicons.dev
# --------------------------------------------------------------------------
# Logo paths from simple-icons (CC0), 24x24 viewBox.
NUMPY_PATH = "M10.315 4.876L6.3048 2.8517l-4.401 2.1965 4.1186 2.0683zm1.8381.9277l4.2045 2.1223-4.3622 2.1906-4.125-2.0718zm5.6153-2.9213l4.3193 2.1658-3.863 1.9402-4.2131-2.1252zm-1.859-.9329L12.021 0 8.1742 1.9193l4.0068 2.0208zm-3.0401 16.7443V24l4.7107-2.3507-.0053-5.3085zm4.7037-4.2057l-.0052-5.2528-4.6985 2.3356v5.2546zm5.6553-.9845v5.327l-4.0178 2.0052-.0029-5.3028zm0-1.8626V6.4214l-4.0253 2.001.0034 5.2633zM11.2062 11.571L8.0333 9.9756v6.895s-3.8804-8.2564-4.2399-8.998c-.0463-.0957-.2371-.2007-.2858-.2262C2.8118 7.2812.773 6.2485.773 6.2485V18.43l2.8204 1.5076v-6.3674s3.8392 7.3775 3.878 7.458c.0389.0807.4245.8582.8362 1.1314.5485.363 2.8992 1.7766 2.8992 1.7766z"
SPARK_PATH = "M10.812 0c-.425.013-.845.215-1.196.605a3.593 3.593 0 00-.493.722c-.355.667-.425 1.415-.556 2.143a551.9 551.9 0 00-.726 4.087c-.027.16-.096.227-.244.273C5.83 8.386 4.06 8.94 2.3 9.514c-.387.125-.773.289-1.114.506-1.042.665-1.196 1.753-.415 2.71.346.422.79.715 1.284.936 1.1.49 2.202.976 3.3 1.47.019.01.036.013.053.019h-.004l1.306.535c0 .023.002.045 0 .073-.2 2.03-.39 4.063-.58 6.095-.04.419-.012.831.134 1.23.317.87 1.065 1.148 1.881.701.372-.204.666-.497.937-.818 1.372-1.623 2.746-3.244 4.113-4.872.111-.133.205-.15.363-.098.349.117.697.231 1.045.347h.001c.02.012.045.02.073.03l.142.042c1.248.416 2.68.775 3.929 1.19.4.132.622.164 1.045.098.311-.048.592-.062.828-.236.602-.33.995-.957.988-1.682-.005-.427-.154-.813-.35-1.186-.82-1.556-1.637-3.113-2.461-4.666-.078-.148-.076-.243.037-.375 1.381-1.615 2.756-3.236 4.133-4.855.272-.32.513-.658.653-1.058.308-.878-.09-1.57-1-1.741a2.783 2.783 0 00-1.235.069c-1.974.521-3.947 1.041-5.918 1.57-.175.047-.26.015-.355-.144a353.08 353.08 0 00-2.421-4.018 4.61 4.61 0 00-.652-.849c-.371-.37-.802-.549-1.227-.536zm.172 3.703a.592.592 0 01.189.211c.87 1.446 1.742 2.89 2.609 4.338.07.118.135.16.277.121 1.525-.41 3.052-.813 4.579-1.217.367-.098.735-.193 1.103-.289a.399.399 0 01-.1.2c-1.259 1.48-2.516 2.962-3.779 4.438-.11.13-.12.22-.04.37.937 1.803 1.768 3.309 2.498 4.76l-3.696-1.019c-.538-.18-1.077-.358-1.615-.539-.163-.055-.25-.03-.36.1-1.248 1.488-2.504 2.97-3.759 4.454a.398.398 0 01-.18.132c.035-.378.068-.757.104-1.136.149-1.572.297-3.144.451-4.716-.03-.318.117-.405-.322-.545-1.493-.593-3.346-1.321-4.816-1.905a.595.595 0 01.24-.134c1.797-.57 3.595-1.14 5.394-1.705.127-.04.199-.092.211-.233.013-.148.05-.294.076-.441.241-1.363.483-2.726.726-4.088.068-.386.14-.771.21-1.157z"


# --------------------------------------------------------------------------
# 6. Inventory: tech stack as an RPG item grid with an auto-moving cursor
# --------------------------------------------------------------------------
# Pixel sprites for each id live in scripts/icon_pixels.json (made by pixelate_icons.py).
INVENTORY = [
    {"id": "python", "name": "PYTHON", "rarity": "LEGENDARY", "type": "MAIN WEAPON", "stat": "+99 DATA MAGIC"},
    {"id": "java", "name": "JAVA", "rarity": "EPIC", "type": "HEAVY ARMOR", "stat": "+80 STABILITY"},
    {"id": "spring", "name": "SPRING BOOT", "rarity": "EPIC", "type": "BOOTS", "stat": "+70 JUMP POWER"},
    {"id": "js", "name": "JAVASCRIPT", "rarity": "RARE", "type": "THROWING DAGGER", "stat": "+60 WEB AGILITY"},
    {"id": "github", "name": "GITHUB", "rarity": "RARE", "type": "GUILD BADGE", "stat": "+60 TEAMWORK"},
    {"id": "mysql", "name": "MYSQL", "rarity": "RARE", "type": "STORAGE CHEST", "stat": "+60 QUERY SPEED"},
    {"id": "postgres", "name": "POSTGRESQL", "rarity": "EPIC", "type": "ELEPHANT MOUNT", "stat": "+80 INTEGRITY"},
    {"id": "git", "name": "GIT", "rarity": "RARE", "type": "TIME SCROLL", "stat": "UNDO ANY MISTAKE"},
    {"id": "pytorch", "name": "PYTORCH", "rarity": "LEGENDARY", "type": "FLAME TORCH", "stat": "+99 NEURAL POWER"},
    {"id": "sklearn", "name": "SCIKIT-LEARN", "rarity": "EPIC", "type": "ALCHEMY KIT", "stat": "+80 ACCURACY"},
    {"id": "numpy", "name": "NUMPY", "rarity": "EPIC", "type": "ARRAY CUBE", "stat": "+90 VECTOR SPEED"},
    {"id": "pyspark", "name": "PYSPARK", "rarity": "EPIC", "type": "SPARK GEM", "stat": "+90 BIG DATA AOE"},
]
RARITY = {"LEGENDARY": (ORANGE, 5), "EPIC": ("#b57bff", 4), "RARE": (BLUE, 3)}
ICON_PIXELS = Path(__file__).resolve().parent / "icon_pixels.json"


def inventory():
    import json

    icons = json.loads(ICON_PIXELS.read_text())
    W, H = 960, 300
    N = len(INVENTORY)
    COLS, SLOT, GAP = 6, 88, 12
    gx, gy = 36, 36
    per = 1.8
    cycle = N * per
    b = [pixel_frame(0, 0, W, H)]
    css = []

    def slot_xy(i):
        return gx + (i % COLS) * (SLOT + GAP), gy + (i // COLS) * (SLOT + GAP)

    # item grid
    for i, item in enumerate(INVENTORY):
        x, y = slot_xy(i)
        col, _ = RARITY[item["rarity"]]
        cls = ' class="legend"' if item["rarity"] == "LEGENDARY" else ""
        b.append(f'<rect{cls} x="{x}" y="{y}" width="{SLOT}" height="{SLOT}" fill="{col}"/>')
        b.append(f'<rect x="{x + 4}" y="{y + 4}" width="{SLOT - 8}" height="{SLOT - 8}" fill="{INK}"/>')
        b.append(f'<rect x="{x + 8}" y="{y + 8}" width="{SLOT - 16}" height="{SLOT - 16}" fill="#1a1f4a"/>')
        b.append(f'<rect x="{x + 8}" y="{y + 8}" width="{SLOT - 16}" height="4" fill="#262c63"/>')
        ic = icons[item["id"]]
        b.append(sprite(ic["rows"], ic["palette"], x + 8, y + 8, 3))
    hint = "AUTO-BROWSING..."
    grid_right = gx + COLS * SLOT + (COLS - 1) * GAP
    b.append(text(hint, grid_right - text_width(hint, 2), H - 52, 2, GRAY, INK, cls="blink"))
    lx = gx
    for k, (label, (col, _)) in enumerate(RARITY.items()):
        b.append(f'<rect x="{lx}" y="{H - 52}" width="14" height="14" fill="{col}"/>')
        b.append(text(label, lx + 22, H - 52, 2, col, INK))
        lx += 22 + text_width(label, 2) + 28

    # cursor: yellow corner brackets hopping slot to slot
    c = 6
    L, T = 20, 6
    s = SLOT + 2 * c
    corners = (
        f"M0 0h{L}v{T}h{-(L - T)}v{L - T}h{-T}z"
        f"M{s} 0v{L}h{-T}v{-(L - T)}h{-(L - T)}v{-T}z"
        f"M0 {s}v{-L}h{T}v{L - T}h{L - T}v{T}z"
        f"M{s} {s}h{-L}v{-T}h{L - T}v{-(L - T)}h{T}z"
    )
    b.append(f'<g class="cursor"><g class="cpulse"><path fill="{YELLOW}" d="{corners}"/></g></g>')
    ks = []
    for i in range(N):
        x, y = slot_xy(i)
        ks.append(f"{i / N * 100:.3f}%{{transform:translate({x - c}px,{y - c}px)}}")
    x, y = slot_xy(0)
    ks.append(f"100%{{transform:translate({x - c}px,{y - c}px)}}")
    css.append(f".cursor{{animation:cur {cycle}s step-end infinite}}@keyframes cur{{{''.join(ks)}}}")

    # detail panel, one page per item, synced with the cursor
    px0, py0, pw, ph = 652, 24, 284, H - 48
    b.append(pixel_frame(px0, py0, pw, ph, fill=NAVY2))
    ix = px0 + 22
    for i, item in enumerate(INVENTORY):
        col, stars = RARITY[item["rarity"]]
        ic = icons[item["id"]]
        page = [
            f'<rect x="{ix - 4}" y="{py0 + 20}" width="80" height="80" fill="{col}"/>',
            f'<rect x="{ix}" y="{py0 + 24}" width="72" height="72" fill="#1a1f4a"/>',
            sprite(ic["rows"], ic["palette"], ix, py0 + 24, 3),
            text(item["rarity"], ix + 92, py0 + 30, 2, col, INK),
            text("$" * stars, ix + 92, py0 + 52, 3, YELLOW, INK),
            text(item["name"], ix, py0 + 116, 3, WHITE, INK),
            text(item["type"], ix, py0 + 150, 2, GRAY, INK),
            text(item["stat"], ix, py0 + 176, 2, GREEN, INK),
            text("[E] EQUIPPED", ix, py0 + 208, 2, CYAN, INK),
        ]
        b.append(f'<g class="p{i}">{"".join(page)}</g>')
        a, z = i / N * 100, (i + 1) / N * 100
        css.append(
            f".p{i}{{opacity:{1 if i == 0 else 0};animation:p{i} {cycle}s step-end infinite}}"
            f"@keyframes p{i}{{0%{{opacity:{1 if i == 0 else 0}}}"
            + (f"{a:.3f}%{{opacity:1}}" if i else "")
            + f"{z:.3f}%{{opacity:0}}100%{{opacity:0}}}}"
        )

    css.append("""
.blink{animation:blink 1.4s steps(1) infinite}
@keyframes blink{0%{opacity:1}50%{opacity:.35}}
.cpulse{animation:cp .6s steps(1) infinite}
@keyframes cp{0%{transform:translate(0,0)}50%{transform:translate(0,-2px)}}
.legend{animation:legend 1.2s steps(1) infinite}
@keyframes legend{0%{fill:#ff9f43}50%{fill:#ffd25a}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
""")
    names = ", ".join(it["name"].title() for it in INVENTORY)
    return svg_doc(W, H, "".join(b), "".join(css), f"Inventory: {names}")


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        "banner.svg": banner(),
        "welcome.svg": welcome(),
        "header-inventory.svg": header("INVENTORY", "ITEMS: 12", CHEST, CHEST_PAL),
        "header-quests.svg": header("QUEST LOG", "CLEARED: 5  ACTIVE: 2", SCROLL, SCROLL_PAL),
        "header-battle.svg": header("BATTLE LOG", "CONTRIBUTIONS.EXE", JOYSTICK, JOY_PAL),
        "footer.svg": footer(),
        "inventory.svg": inventory(),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg)
        print(f"wrote assets/{name} ({len(svg) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
