# TenX Protocols typography — for generated documents

No confirmed brand typeface exists yet for TenX Protocols corporate
documents (the product-level "Inter" typeface found in `swarmforge` belongs
to that product's own UI brand, not the corporate brand — do not reuse it
here).

## Decision for generated Word/Google Docs documents

Use **Calibri** as the body and heading typeface in the pandoc reference
templates.

**Why not a distinctive/custom typeface:** documents in this pipeline get
converted Markdown → `.docx` (via Pandoc) → uploaded to Drive, where Google
auto-converts to a native Google Doc. A custom font not installed on the
rendering system (Google's docx-import conversion, or a reader's own
machine if they download the `.docx`) silently falls back to a substitute —
often inconsistently between Word and Google Docs. Calibri and Arial are
the two typefaces most reliably preserved across that whole chain. Calibri
reads as more modern/current than Arial for a 2026-era company, so it's the
better default until (or unless) a real corporate typeface is confirmed.

## Open item

If TenX Protocols later adopts a specific brand typeface, replace this
decision — but confirm it survives the Markdown → docx → Google Docs
pipeline before adopting it for real documents, not just for marketing
materials.
