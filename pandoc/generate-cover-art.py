#!/usr/bin/env python3
"""Generate pandoc/assets/report-cover-art.png — the decorative graphic on
the report cover (see build_report_reference() in build-reference.py).

A low-poly triangular mosaic in a handful of violet shades, in the spirit
of ref4's faceted-polygon texture (one of the templatelab.com cover-page
references the report cover is modeled on) — NOT a generic stock
wireframe/hexagon-network graphic.

History of what didn't work, kept here so it isn't retried:
- OOXML paragraph shading patterns (w:shd val="diagStripe" etc.) looked
  like the "free" way to get real geometric texture with no image at all
  — tested directly in a minimal docx and LibreOffice 26.2 headless
  renders EVERY pattern value as a flat solid block, ignoring the
  pattern entirely. Dead end for anything renderable here.
- Two small, low-opacity (~0.15-0.24) tone-on-tone copies of the whole
  icon mark, scattered on the masthead band — read as "a large block of
  purple" per direct feedback, not a visible pattern. This mosaic
  replaces that: opaque, high-contrast, and sized to cover the entire
  masthead band, not tucked into a small corner of it.
- Before THAT: the icon's three individual triangles repeated at
  different scales/rotations — read as disconnected geometric confetti.

Rasterizes via rsvg-convert directly, not ImageMagick's `magick ... svg`
delegate — see logo/build-logos.py's rasterize() docstring for why
(that delegate crashes on this repo's SVGs; direct invocation doesn't).
"""
import random
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ASSETS_DIR = HERE / "assets"
OUTPUT = ASSETS_DIR / "report-cover-art.png"
LOGO_WHITE = REPO_ROOT / "logo" / "png" / "lockup-horizontal-white-512.png"

# Canvas: matches the masthead band's actual aspect ratio (wide banner).
W, H = 1600, 900
PNG_HEIGHT = 1350  # 1.5x for a crisp raster at print size

COVER_HEX = "#3D1A5B"
# A small palette of violet shades spanning both lighter and darker than
# COVER_HEX, so facets read as genuine light/shadow variation rather than
# random noise — weighted so COVER_HEX-adjacent tones dominate and the
# lightest/darkest are accents, not half the mosaic.
PALETTE = [
    "#3D1A5B",  # base
    "#3D1A5B",
    "#4B2570",  # lighter step 1
    "#4B2570",
    "#5B3486",  # lighter step 2
    "#2E1345",  # darker step 1
    "#6B4499",  # lighter step 3 (accent)
    "#241033",  # darker step 2 (accent)
]

COLS, ROWS = 14, 8
JITTER = 0.35  # fraction of a cell the shared grid vertices wander, for an organic (not perfectly uniform) low-poly look

SEED = 20260714  # fixed, not random.random() with no seed — reproducible output, stable git diffs on regeneration


def build_grid():
    """A COLS x ROWS grid of points, each perturbed by a seeded random
    jitter so shared vertices between triangles still line up (no gaps),
    but the mesh doesn't look like a perfectly regular grid."""
    rng = random.Random(SEED)
    cell_w, cell_h = W / COLS, H / ROWS
    points = {}
    for row in range(ROWS + 1):
        for col in range(COLS + 1):
            x, y = col * cell_w, row * cell_h
            # Don't jitter the outer border — keeps the mosaic's edges
            # flush with the canvas, no ragged/transparent edge gaps.
            if 0 < row < ROWS:
                y += rng.uniform(-JITTER, JITTER) * cell_h
            if 0 < col < COLS:
                x += rng.uniform(-JITTER, JITTER) * cell_w
            points[(row, col)] = (x, y)
    return points


def triangle_markup(p1, p2, p3, color):
    pts = f"{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"
    return f'  <polygon points="{pts}" fill="{color}"/>'


def main():
    ASSETS_DIR.mkdir(exist_ok=True)
    points = build_grid()
    rng = random.Random(SEED + 1)
    triangles = []
    for row in range(ROWS):
        for col in range(COLS):
            tl, tr = points[(row, col)], points[(row, col + 1)]
            bl, br = points[(row + 1, col)], points[(row + 1, col + 1)]
            # Split each grid cell into two triangles along a diagonal
            # that alternates direction per cell — a real low-poly mesh
            # doesn't cut every cell the same way, and alternating avoids
            # a repetitive chevron artifact a uniform diagonal would show.
            if (row + col) % 2 == 0:
                triangles.append((tl, tr, bl))
                triangles.append((tr, br, bl))
            else:
                triangles.append((tl, tr, br))
                triangles.append((tl, br, bl))
    shapes = "\n".join(
        triangle_markup(a, b, c, rng.choice(PALETTE)) for a, b, c in triangles
    )
    svg = (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect x="0" y="0" width="{W}" height="{H}" fill="{COVER_HEX}"/>\n'
        f'{shapes}\n</svg>\n'
    )
    svg_path = ASSETS_DIR / "report-cover-art.svg"
    svg_path.write_text(svg)
    subprocess.run(
        ["rsvg-convert", "-h", str(PNG_HEIGHT), "-a", "--background-color", "none",
         "-o", str(OUTPUT), str(svg_path)],
        check=True,
    )

    # Composite the logo directly onto the mosaic (top-left, padded) so
    # the reference doc only has to insert ONE image for the whole
    # masthead — the header no longer needs a separate logo paragraph
    # plus a separate art paragraph with their own independent spacing to
    # tune against each other.
    logo_height = round(PNG_HEIGHT * 0.11)
    pad = round(PNG_HEIGHT * 0.07)
    composited = ASSETS_DIR / "report-cover-art.tmp.png"
    subprocess.run(
        [
            "magick", str(OUTPUT),
            "(", str(LOGO_WHITE), "-resize", f"x{logo_height}", ")",
            "-gravity", "NorthWest", "-geometry", f"+{pad}+{pad}", "-composite",
            str(composited),
        ],
        check=True,
    )
    composited.replace(OUTPUT)
    print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
