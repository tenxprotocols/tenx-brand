# tenx-brand

Single source of truth for TenX Protocols brand assets used in generated
internal documents — colors, logo, typography, and (once built) the Pandoc
reference-document templates that give every synced policy and template a
consistent title page / header bar, without editing each document
individually.

This is the **parent company's** brand. The Delaware spinout (AI Workflow
Platform) will get its own brand identity and its own equivalent repo once
that's defined — this repo isn't meant to be reused for that entity.

## Contents

- [colors.md](colors.md) — color palette (confirmed + derived)
- [typography.md](typography.md) — typeface decision for generated documents
- `logo/tenx-logo.svg` — logo, pulled from tenx.inc (white fill, transparent
  background — matches the site's dark theme)
- `pandoc/` — reference `.docx` templates built from the above (added once
  the doc-formatting work in `tenx-doc-templates` reaches that task)

## How other repos use this

`tenx-doc-templates` and `tenx-documents`' sync pipelines check out this
repo in CI and pass its reference `.docx` files to Pandoc via
`--reference-doc`. Update a color or the logo here once; every document
picks it up on its next sync — no per-document styling.
