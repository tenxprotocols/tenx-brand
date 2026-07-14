#!/usr/bin/env python3
"""Rebuild every logo variant (SVG + PNG) from the original brand mark.

Source of truth is the path data below, extracted from the original
tenx-logo.svg (icon: the last 3 paths; wordmark "TenX": the first 4).
Bounding boxes are hardcoded, not computed live — they were derived once
via a render-at-high-DPI-then-trim pass (ImageMagick `-trim`), which is
the reliable way to get exact bounds for paths that include curves (the
"e" in "TenX" uses cubic Beziers, so eyeballing coordinates from the path
string risks being wrong). If the source paths ever change, redo that
render+trim pass rather than hand-editing these numbers.

Produces, for each of 4 compositions (icon / wordmark / lockup-horizontal
/ lockup-stacked) in 2 colors (black / white):
  - one padded SVG in svg/
  - PNG rasters at 4 common sizes in png/

Requires: ImageMagick (`magick` on PATH).
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG_DIR = HERE / "svg"
PNG_DIR = HERE / "png"

ICON_PATHS = [
    'M22.2679 30H6.87012L14.5684 22.3006L22.2679 30Z',
    'M18.4356 4.9061L25.2009 11.6703L30 6.87012V24.2015L5.79853 0H23.3417L18.4356 4.9061Z',
    'M7.80424 15.5364L0 23.3417V7.73212L7.80424 15.5364Z',
]
WORDMARK_PATHS = [
    'M52.5319 25.3354H50.377V6.97284H42V5H60.8786V6.97284H52.5319V25.3354Z',
    'M65.5999 25.639C60.774 25.639 57.7085 22.6038 57.7085 17.8386C57.7085 13.2859 60.7437 10.0383 65.5695 10.0383C69.9705 10.0383 73.0967 12.5879 73.0967 17.0495C73.0967 17.5958 73.036 18.0511 72.9449 18.4457H59.7421C59.8635 21.8147 61.5935 23.8482 65.5695 23.8482C69.0903 23.8482 70.7293 22.5431 70.7293 20.3578V20.1454H72.8842V20.3578C72.8842 23.484 69.7884 25.639 65.5999 25.639ZM65.5392 11.8291C61.6542 11.8291 59.8938 13.8323 59.7421 17.1102H71.0631C71.0631 16.9585 71.0631 16.8067 71.0631 16.6549C71.0631 13.4984 69.0599 11.8291 65.5392 11.8291Z',
    'M78.1099 25.3354H75.9549V10.3418H77.8974V15.0463H78.0492C78.5651 12.4968 80.6897 10.0383 84.423 10.0383C88.6418 10.0383 90.7361 13.0431 90.7361 16.5942V25.3354H88.5811V16.8978C88.5811 13.8019 87.0939 12.0112 83.6642 12.0112C80.022 12.0112 78.1099 14.2268 78.1099 18.0815V25.3354Z',
    'M95.3355 25.3354H92.5735L100.981 15.1677V14.9856L92.5735 5H95.3355L102.741 13.6805H102.893L110.208 5H113L104.562 15.016V15.1677L113 25.3354H110.208L102.863 16.4728H102.681L95.3355 25.3354Z',
]

# Exact bounding boxes in original path coordinate space (see docstring).
ICON_BBOX = (0.0, 0.0, 30.13, 30.13)          # x, y, w, h
WORDMARK_BBOX = (42.0, 4.93, 71.2, 20.93)     # x, y, w, h

GAP_STACKED = 6.0   # vertical gap between icon and wordmark when stacked
PAD = 4.0           # padding added on every side of every variant's viewBox
SIZES = [128, 256, 512, 1024]  # target PNG heights


def paths_markup(paths, fill):
    return '\n'.join(f'<path d="{d}" fill="{fill}"/>' for d in paths)


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

    # --- icon only ---
    build(
        "icon",
        {c: paths_markup(ICON_PATHS, c) for c in ("black", "white")},
        ICON_BBOX,
    )

    # --- wordmark only ---
    build(
        "wordmark",
        {c: paths_markup(WORDMARK_PATHS, c) for c in ("black", "white")},
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
        {c: paths_markup(ICON_PATHS, c) + '\n' + paths_markup(WORDMARK_PATHS, c) for c in ("black", "white")},
        horiz_bbox,
    )

    # --- lockup-stacked: icon centered above the wordmark, with a gap.
    # Icon is translated so its horizontal center matches the wordmark's,
    # and its bottom edge sits GAP_STACKED above the wordmark's top edge. ---
    wordmark_center_x = wx + ww / 2
    icon_center_x = ix + iw / 2
    dx = wordmark_center_x - icon_center_x
    dy = (wy - GAP_STACKED - ih) - iy
    icon_translated = f'<g transform="translate({dx:.4g},{dy:.4g})">\n{{}}\n</g>'
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
            c: icon_translated.format(paths_markup(ICON_PATHS, c)) + '\n' + paths_markup(WORDMARK_PATHS, c)
            for c in ("black", "white")
        },
        stacked_bbox,
    )


if __name__ == "__main__":
    main()
