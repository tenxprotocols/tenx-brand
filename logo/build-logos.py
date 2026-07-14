#!/usr/bin/env python3
"""Rebuild every logo variant (SVG + PNG) from the source marks.

Source of truth is source/icon.svg and source/wordmark.svg — edit those
(not this script) if the mark itself ever changes. Each source file's
viewBox is the exact bounding box of its paths, derived once via a
render-at-high-DPI-then-trim pass (ImageMagick `-trim`), which is the
reliable way to get exact bounds for paths that include curves (the "e"
in "TenX" uses cubic Beziers, so eyeballing coordinates from the path
string risks being wrong). If the source paths ever change, redo that
render+trim pass to get the new viewBox rather than hand-editing it.

Produces, for each of 4 compositions (icon / wordmark / lockup-horizontal
/ lockup-stacked) in 2 colors (black / white):
  - one padded SVG in svg/
  - PNG rasters at 4 common sizes in png/

Requires: ImageMagick (`magick` on PATH) and rsvg-convert (`brew install
librsvg`) — see rasterize()'s docstring for why rsvg-convert is invoked
directly rather than through ImageMagick's SVG delegate.
"""
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "source"
SVG_DIR = HERE / "svg"
PNG_DIR = HERE / "png"

GAP_STACKED = 6.0   # vertical gap between icon and wordmark when stacked
PAD = 4.0           # padding added on every side of every variant's viewBox
SIZES = [128, 256, 512, 1024]  # target PNG heights


def load_source(name):
    """Read a source/*.svg file, returning (unfilled path markup, bbox).

    bbox comes straight from the file's own viewBox — see this script's
    docstring for how that number was derived.
    """
    text = (SOURCE_DIR / f"{name}.svg").read_text()
    view_box = re.search(r'viewBox="([^"]+)"', text).group(1)
    x, y, w, h = (float(v) for v in view_box.split())
    inner = re.search(r"<svg[^>]*>(.*)</svg>", text, re.DOTALL).group(1).strip()
    return inner, (x, y, w, h)


def colored(inner, fill):
    # Source files intentionally carry no fill attribute — color is a
    # property of the composition being built, not of the mark itself.
    return f'<g fill="{fill}">\n{inner}\n</g>'


def svg_doc(inner, x, y, w, h):
    return (
        f'<svg width="{w:.4g}" height="{h:.4g}" viewBox="{x:.4g} {y:.4g} {w:.4g} {h:.4g}" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg">\n{inner}\n</svg>\n'
    )


def write_svg(name, color, inner, bbox):
    x, y, w, h = bbox
    vb = (x - PAD, y - PAD, w + 2 * PAD, h + 2 * PAD)
    content = svg_doc(inner, *vb)
    path = SVG_DIR / f"{name}-{color}.svg"
    path.write_text(content)
    return path


def rasterize(svg_path, name, color):
    # rsvg-convert directly, not `magick ... svg`: ImageMagick's SVG
    # delegate shells out to rsvg-convert internally and was found (by
    # testing) to crash specifically on documents containing a <g
    # transform> group (used by the stacked lockup) — direct invocation
    # renders the exact same file with no issue, so skip the delegate
    # layer entirely rather than avoid <g transform> in the source SVGs.
    for size in SIZES:
        out = PNG_DIR / f"{name}-{color}-{size}.png"
        subprocess.run(
            ["rsvg-convert", "-h", str(size), "-a", "--background-color", "none",
             "-o", str(out), str(svg_path)],
            check=True,
        )


def build(name, inner_by_color, bbox):
    for color in ("black", "white"):
        svg_path = write_svg(name, color, inner_by_color[color], bbox)
        rasterize(svg_path, name, color)
        print(f"built {name}-{color}: svg + {len(SIZES)} pngs")


def main():
    SVG_DIR.mkdir(exist_ok=True)
    PNG_DIR.mkdir(exist_ok=True)

    icon_inner, ICON_BBOX = load_source("icon")
    wordmark_inner, WORDMARK_BBOX = load_source("wordmark")

    # --- icon only ---
    build(
        "icon",
        {c: colored(icon_inner, c) for c in ("black", "white")},
        ICON_BBOX,
    )

    # --- wordmark only ---
    build(
        "wordmark",
        {c: colored(wordmark_inner, c) for c in ("black", "white")},
        WORDMARK_BBOX,
    )

    # --- lockup-horizontal: icon + wordmark at their original relative
    # position (already designed to sit side by side, already vertically
    # aligned) — union of both bounding boxes, no transform needed. ---
    ix, iy, iw, ih = ICON_BBOX
    wx, wy, ww, wh = WORDMARK_BBOX
    horiz_bbox = (
        min(ix, wx), min(iy, wy),
        max(ix + iw, wx + ww) - min(ix, wx),
        max(iy + ih, wy + wh) - min(iy, wy),
    )
    build(
        "lockup-horizontal",
        {c: colored(icon_inner, c) + '\n' + colored(wordmark_inner, c) for c in ("black", "white")},
        horiz_bbox,
    )

    # --- lockup-stacked: icon centered above the wordmark, with a gap.
    # Icon is translated so its horizontal center matches the wordmark's,
    # and its bottom edge sits GAP_STACKED above the wordmark's top edge. ---
    wordmark_center_x = wx + ww / 2
    icon_center_x = ix + iw / 2
    dx = wordmark_center_x - icon_center_x
    dy = (wy - GAP_STACKED - ih) - iy
    stacked_icon_x = ix + dx
    stacked_icon_y = iy + dy
    stacked_bbox = (
        min(stacked_icon_x, wx), stacked_icon_y,
        max(stacked_icon_x + iw, wx + ww) - min(stacked_icon_x, wx),
        (wy + wh) - stacked_icon_y,
    )
    build(
        "lockup-stacked",
        {
            c: f'<g transform="translate({dx:.4g},{dy:.4g})">\n{colored(icon_inner, c)}\n</g>'
               + '\n' + colored(wordmark_inner, c)
            for c in ("black", "white")
        },
        stacked_bbox,
    )


if __name__ == "__main__":
    main()
