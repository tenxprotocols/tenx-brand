#!/usr/bin/env python3
"""Generate pandoc/assets/report-cover-art.png — the decorative graphic on
the report cover (see build_report_reference() in build-reference.py).

Deliberately NOT a generic stock wireframe/hexagon-network graphic, and
deliberately NOT the icon's three triangles scattered apart either (an
earlier attempt at that read as generic geometric confetti, disconnected
from the brand). This instead uses the icon mark WHOLE and large,
cropped off the edge of the canvas like a watermark, tone-on-tone in a
lighter violet — a real, recognizable extension of the brand mark rather
than borrowed decoration or abstracted-into-meaninglessness shapes. Same
"icon over wordmark" logo asset library that already exists is left
untouched — this is a one-off derived asset, not a fifth logo
composition, since no other context needs an oversized cropped watermark.

Rasterizes via rsvg-convert directly, not ImageMagick's `magick ... svg`
delegate — see logo/build-logos.py's rasterize() docstring for why
(that delegate crashes on this repo's SVGs; direct invocation doesn't).
"""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS_DIR = HERE / "assets"
OUTPUT = ASSETS_DIR / "report-cover-art.png"

ICON_PATHS = [
    'M22.2679 30H6.87012L14.5684 22.3006L22.2679 30Z',
    'M18.4356 4.9061L25.2009 11.6703L30 6.87012V24.2015L5.79853 0H23.3417L18.4356 4.9061Z',
    'M7.80424 15.5364L0 23.3417V7.73212L7.80424 15.5364Z',
]
ICON_SIZE = 30.13  # icon.svg's viewBox is 0 0 30.13 30.13

# Canvas: a wide banner strip, sized for the report cover's decoration zone.
W, H = 1600, 520
PNG_HEIGHT = 1040  # 2x W/H for a crisp raster at print size

# Two instances of the WHOLE icon (not its individual triangles): a
# moderate one on the right, a smaller quieter one on the left — both
# fully visible. An earlier attempt let the large instance bleed off the
# canvas edge as a "watermark," but at that scale the crop cut through
# the icon's own negative space and left only unrecognizable fragments
# in the corner — kept whole instead, since a recognizable mark, even
# smaller, beats an oversized illegible one.
INSTANCES = [
    (3.4, 1430, 260, 16, 0.24),
    (2.1, 230, 380, -12, 0.16),
]

ART_VIOLET = "#8B6BB8"  # a mid violet, lighter than COVER_HEX (#3D1A5B) — tone-on-tone, not a contrasting accent


def instance_markup(scale, x, y, rotation, opacity):
    paths = "\n".join(f'    <path d="{d}"/>' for d in ICON_PATHS)
    # Center the icon's own viewBox before scaling/rotating, so (x, y) is
    # where the icon's center lands, not its top-left corner.
    half = ICON_SIZE / 2
    return (
        f'  <g transform="translate({x},{y}) rotate({rotation}) scale({scale}) '
        f'translate({-half},{-half})" fill="{ART_VIOLET}" fill-opacity="{opacity}">\n'
        f'{paths}\n'
        f'  </g>'
    )


def main():
    ASSETS_DIR.mkdir(exist_ok=True)
    groups = "\n".join(instance_markup(*inst) for inst in INSTANCES)
    # Solid COVER_HEX background baked into the image itself, not left
    # transparent — found (by rendering a test docx) that LibreOffice
    # doesn't reliably composite a transparent PNG's background against
    # the shaded paragraph color it's placed in; a large image's
    # transparent area rendered as plain white instead of showing the
    # violet paragraph shading through it. Baking the same background
    # color in removes the dependency on that compositing entirely.
    background = f'  <rect x="0" y="0" width="{W}" height="{H}" fill="#3D1A5B"/>'
    svg = (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg">\n{background}\n{groups}\n</svg>\n'
    )
    svg_path = ASSETS_DIR / "report-cover-art.svg"
    svg_path.write_text(svg)
    subprocess.run(
        ["rsvg-convert", "-h", str(PNG_HEIGHT), "-a", "--background-color", "none",
         "-o", str(OUTPUT), str(svg_path)],
        check=True,
    )
    print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
