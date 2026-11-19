#!/usr/bin/env python3
"""Turn tech logos into small pixel-art sprites for the inventory.

Downloads each logo from skillicons.dev (NumPy and PySpark use the paths in
generate_assets.py), drops the dark tile background, shrinks it to a GRID x GRID
grid, snaps every pixel to a handful of the logo's own colors and writes
scripts/icon_pixels.json, which generate_assets.py reads.

Needs network access plus `rsvg-convert` and ImageMagick (`magick`).
Only re-run when the icon list changes:

    python3 scripts/pixelate_icons.py && python3 scripts/generate_assets.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_assets import INVENTORY, NUMPY_PATH, SPARK_PATH  # noqa: E402

GRID = 24
MAX_COLORS = 6
OUT = Path(__file__).resolve().parent / "icon_pixels.json"
KEYS = "ABCDEFGHIJ"


def fetch_svg(icon_id: str) -> str:
    if icon_id == "numpy":
        return _single(NUMPY_PATH, "#4DABCF")
    if icon_id == "pyspark":
        return _single(SPARK_PATH, "#E25A1C")
    url = f"https://skillicons.dev/icons?i={icon_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "pixelate-icons"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        svg = resp.read().decode()
    # drop the dark rounded tile so only the logo itself remains
    return re.sub(r'<rect[^>]*fill="#242938"[^>]*/>', "", svg)


def _single(d: str, color: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
        f'<path transform="translate(48 48) scale(6.6667)" fill="{color}" d="{d}"/></svg>'
    )


def rasterize(svg: str) -> list[list[tuple[int, int, int, int]]]:
    with tempfile.TemporaryDirectory() as tmp:
        src, png = Path(tmp) / "i.svg", Path(tmp) / "i.png"
        src.write_text(svg)
        subprocess.run(["rsvg-convert", "-w", "256", "-h", "256", str(src), "-o", str(png)], check=True)
        txt = subprocess.run(
            ["magick", str(png), "-filter", "box", "-resize", f"{GRID}x{GRID}!", "txt:-"],
            check=True, capture_output=True, text=True,
        ).stdout
    px = [[(0, 0, 0, 0)] * GRID for _ in range(GRID)]
    for line in txt.splitlines()[1:]:
        m = re.match(r"(\d+),(\d+): \(([^)]*)\)", line)
        if not m:
            continue
        x, y = int(m[1]), int(m[2])
        vals = [float(v.rstrip("%")) for v in m[3].split(",")]
        r, g, b = (int(round(v)) for v in vals[:3])
        a = vals[3] if len(vals) > 3 else 255
        a = int(round(a * 255)) if a <= 1 else int(round(a))
        px[y][x] = (r, g, b, a)
    return px


def quantize(px):
    solid = [(r, g, b) for row in px for (r, g, b, a) in row if a >= 110]
    # bucket similar shades, then keep the most common buckets as the palette
    bucket = lambda c: tuple(v // 24 for v in c)  # noqa: E731
    groups: dict[tuple, list] = {}
    for c in solid:
        groups.setdefault(bucket(c), []).append(c)
    top = [k for k, _ in Counter({k: len(v) for k, v in groups.items()}).most_common(MAX_COLORS)]
    palette = [tuple(sum(ch) // len(groups[k]) for ch in zip(*groups[k])) for k in top]

    def nearest(c):
        return min(range(len(palette)), key=lambda i: sum((a - b) ** 2 for a, b in zip(c, palette[i])))

    rows = []
    for row in px:
        rows.append("".join(KEYS[nearest((r, g, b))] if a >= 110 else "." for (r, g, b, a) in row))
    return rows, {KEYS[i]: "#%02x%02x%02x" % c for i, c in enumerate(palette)}


def main():
    data = {}
    for item in INVENTORY:
        rows, pal = quantize(rasterize(fetch_svg(item["id"])))
        data[item["id"]] = {"rows": rows, "palette": pal}
        print(f"{item['id']:>8}: {len(pal)} colors")
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)}")


if __name__ == "__main__":
    main()
