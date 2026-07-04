# TenX Protocols color palette

Source of truth for brand colors used across internal documents (policies,
templates, runbooks) and, where applicable, other TenX Protocols materials.
Update this file, not individual documents — the doc-sync pipelines in
`tenx-doc-templates` and `tenx-documents` read the reference templates built
from these values.

## Primary palette (confirmed)

| Name | Hex | Usage |
|---|---|---|
| Black | `#000000` | Primary text, primary background (dark mode / title pages) |
| White | `#FFFFFF` | Primary background (light mode), text on dark backgrounds |
| Accent (violet) | `#A855F7` | Headings, title-page document name, header-bar accent line, links |

## Derived palette (computed, not brand-confirmed)

The accent's complement and a darker shade, computed via HSL rotation from
`#A855F7` (H 270.7°, S 91%, L 65.1%). Not verified against any official
brand guideline — treat as a placeholder until confirmed or replaced.

| Name | Hex | Derivation | Suggested usage |
|---|---|---|---|
| Accent — shade (dark) | `#6609BE` | Same hue/sat, L reduced to 60% of base | Hover/active states, secondary emphasis, dark-mode accent |
| Masthead (deep violet) | `#3D1A5B` | Hand-tuned deep violet in the accent's hue family (picked visually, not computed) | Title-panel (masthead) background on policy title pages — the shaded box behind the white document title in `pandoc/build-reference.py` |
| Accent — complement | `#A4F755` (lime-green) | Hue +180° | Use sparingly if at all — a true color-wheel complement to a vivid violet reads as jarring in text-heavy documents. Reserve for rare status indicators (e.g. an "Active" chip) rather than structural document elements (headings, borders, footers). |

## Neutral grays (practical, not computed)

Standard tonal grays derived from the black/white primary pair, for table
borders, footer text, and secondary text — a true complementary color isn't
usable for this; grays are the practical choice.

| Name | Hex | Usage |
|---|---|---|
| Gray — dark | `#333333` | Secondary text |
| Gray — mid | `#6B6B6B` | Table borders, footer/page-number text |
| Gray — light | `#E5E5E5` | Table header backgrounds, horizontal rules |

## Open item

These values came from the user directly (black/white + `#A855F7` accent,
confirmed 2026-06-30) plus mathematically-derived shade/complement — not from
a formal brand guideline document. If a real brand guideline exists or gets
created later, replace this file's derived section accordingly.
