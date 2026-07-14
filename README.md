# tenx-brand

Single source of truth for TenX Protocols brand assets used in generated
internal documents — colors, logo, typography, and the Pandoc
reference-document template that gives every synced policy and template a
consistent title page / header bar, without editing each document
individually.

This is the **parent company's** brand. The Delaware spinout (AI Workflow
Platform) will get its own brand identity and its own equivalent repo once
that's defined — this repo isn't meant to be reused for that entity.

## Contents

- [colors.md](colors.md) — color palette (confirmed + derived)
- [typography.md](typography.md) — typeface decision for generated documents
- `logo/` — see below
- `pandoc/build-reference.py` — regenerates `pandoc/reference.docx`, the
  actual style template both doc repos pass to Pandoc via `--reference-doc`

## Logo

`logo/build-logos.py` regenerates every variant from `logo/source/icon.svg`
and `logo/source/wordmark.svg` — the original brand mark's path data,
extracted once from the source SVG pulled from tenx.inc. Edit those two
files (not the script) if the mark itself ever changes.

Four compositions, each in black and white:

| Variant | What it is |
|---|---|
| `icon` | The geometric mark alone |
| `wordmark` | "TenX" alone |
| `lockup-horizontal` | Icon beside the wordmark (the original combined mark) |
| `lockup-stacked` | Icon centered above the wordmark |

Each composition produces one padded SVG in `logo/svg/` (vector, the real
source of truth for that variant) and PNG rasters at 128/256/512/1024px
tall in `logo/png/`, generated from the SVG via `rsvg-convert` (not
ImageMagick's own SVG delegate — see the script's `rasterize()` docstring
for why: ImageMagick's delegate shells out to `rsvg-convert` internally
and was found to crash specifically on the stacked lockup's `<g
transform>` group; direct invocation renders the identical file with no
issue). Every SVG/PNG has transparent background and padding around the
mark so it never touches the image edge.

## How other repos use this

`tenx-doc-templates` and `tenx-documents`' sync pipelines check out this
repo in CI and pass `pandoc/reference.docx` to Pandoc via `--reference-doc`.
Update a color, the logo, or the reference-doc build script here once;
every document picks it up on its next sync — no per-document styling.
