#!/usr/bin/env python3
"""Rebuild reference.docx from TenX brand colors/fonts/logo.

Run this whenever colors.md, typography.md, or the logo change — it
regenerates pandoc/reference.docx, the single style template both
tenx-doc-templates' and tenx-documents' sync pipelines pass to Pandoc via
--reference-doc. Requires: pandoc, python-docx (`pip install python-docx`).
"""
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.shared import RGBColor, Pt, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGO_PNG = REPO_ROOT / "logo" / "tenx-logo-header.png"
PANDOC_DIR = Path(__file__).resolve().parent
PREVIEW_CONTENT = PANDOC_DIR / "preview-content.md"
OUTPUT = PANDOC_DIR / "reference.docx"

ACCENT = RGBColor(0xA8, 0x55, 0xF7)   # colors.md: Accent (violet)
MASTHEAD_HEX = "3D1A5B"               # deep violet, darker than the accent, for the masthead band
GRAY = RGBColor(0x6B, 0x6B, 0x6B)     # colors.md: Gray — mid
FONT = "Calibri"                      # typography.md

# Deliberately dropped after review: a curve+badge cover graphic (a large
# violet sweep + circular logo badge) was built and rendered, but real SOC 2
# / ISO 27001 policy documents converge on restrained, typographic title
# pages — no illustrative cover art (that's an annual-report/pitch-deck
# convention, a different genre). Illustrative shapes at fixed positions
# also can't adapt to a variable-length title without either colliding with
# the text or requiring per-document layout — a real robustness gap for a
# reference template meant to work for every policy name. The masthead band
# below stays text-only for exactly that reason: paragraph shading grows
# with wrapped text automatically, a fixed shape does not.


def set_style_font_color(doc, style_name, color=None, bold=None, size=None):
    style = doc.styles[style_name]
    style.font.name = FONT
    rpr = style.element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rpr.append(rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rFonts.set(qn(attr), FONT)
    if color is not None:
        style.font.color.rgb = color
    if bold is not None:
        style.font.bold = bold
    if size is not None:
        style.font.size = size


def shade_title_style(doc, size, text_color, bold=True, pad_v=Pt(16), pad_h_twips=180):
    """Turn the Title style into a self-contained colored panel: shaded,
    inset a bit further than the paragraph's own indent so text never
    touches the box edge, with equal top/bottom padding so a single-line
    title sits vertically centered in its own box. Deliberately does NOT
    bleed past the page margins — a paragraph's indent controls both the
    shading extent and where its text starts (there's no way to make a
    shaded box wider than its own text at the paragraph level), so a true
    edge-to-edge bleed always drags the text uncomfortably close to the
    page edge too. Staying within the margins keeps real breathing room on
    every side and still reads as a deliberate title panel. A long title
    wraps to multiple lines and the box grows to fit — nothing to collide
    with. Only ever fires for policy-convention documents; templates never
    trigger Pandoc's title-block path."""
    style = doc.styles['Title']
    pPr = style.element.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), MASTHEAD_HEX)
    pPr.append(shd)
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), str(pad_h_twips))
    ind.set(qn('w:right'), str(pad_h_twips))
    pPr.append(ind)
    style.font.color.rgb = text_color
    style.font.size = size
    style.font.bold = bold
    style.paragraph_format.space_before = pad_v
    style.paragraph_format.space_after = pad_v
    style.paragraph_format.line_spacing = 1.15


def style_meta_line(doc, style_name, size, text_color, space_before=Pt(0), space_after=Pt(2)):
    """Author/Date sit outside the colored title panel entirely — plain
    text on the page background, per direct feedback that company name
    and version info read better outside the block than crammed inside
    it. Both styles are basedOn Title in Pandoc's default reference.docx,
    so they inherit Title's shading/indent through the style cascade —
    not setting anything here would silently leave them shaded. Override
    both explicitly rather than relying on absence."""
    style = doc.styles[style_name]
    pPr = style.element.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), 'auto')
    pPr.append(shd)
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), '0')
    ind.set(qn('w:right'), '0')
    pPr.append(ind)
    style.font.color.rgb = text_color
    style.font.size = size
    style.paragraph_format.space_before = space_before
    style.paragraph_format.space_after = space_after


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base_path = Path(tmp) / "default-reference.docx"
        subprocess.run(
            ["pandoc", "-o", str(base_path), "--print-default-data-file", "reference.docx"],
            check=True,
        )
        doc = Document(str(base_path))

        set_style_font_color(doc, 'Normal')
        set_style_font_color(doc, 'Heading 1', color=ACCENT, bold=True, size=Pt(18))
        set_style_font_color(doc, 'Heading 2', color=ACCENT, bold=True, size=Pt(14))
        set_style_font_color(doc, 'Heading 3', color=ACCENT, bold=True, size=Pt(12))
        set_style_font_color(doc, 'TOC Heading', color=ACCENT, bold=True, size=Pt(18))

        # Title: a colored panel, inset within the margins with real
        # padding on every side (see shade_title_style's docstring for why
        # it doesn't bleed to the page edge). Author/Date (company name,
        # version/confidentiality/date string) sit outside it as plain
        # text — per direct feedback, metadata reads better outside the
        # colored block than crammed inside it.
        shade_title_style(doc, size=Pt(24), text_color=RGBColor(0xFF, 0xFF, 0xFF))
        style_meta_line(
            doc, 'Author', size=Pt(11), text_color=GRAY,
            space_before=Pt(12), space_after=Pt(2),
        )
        style_meta_line(
            doc, 'Date', size=Pt(10), text_color=GRAY,
            space_after=Pt(14),
        )

        # Page break before TOC Heading — separates the title page from the
        # TOC page. Policies pass --toc; templates don't, so this only ever
        # fires for policy documents.
        doc.styles['TOC Heading'].paragraph_format.page_break_before = True

        # Footer: centered page number, on every document regardless of type.
        section = doc.sections[0]
        section.footer.is_linked_to_previous = False
        footer_para = section.footer.paragraphs[0]
        footer_para.alignment = 1  # center
        footer_para.text = ""
        run = footer_para.add_run()
        run.font.name = FONT
        run.font.size = Pt(9)
        run.font.color.rgb = GRAY
        fld_begin = OxmlElement('w:fldChar')
        fld_begin.set(qn('w:fldCharType'), 'begin')
        instr = OxmlElement('w:instrText')
        instr.set(qn('xml:space'), 'preserve')
        instr.text = "PAGE"
        fld_end = OxmlElement('w:fldChar')
        fld_end.set(qn('w:fldCharType'), 'end')
        r_element = run._r
        r_element.append(fld_begin)
        r_element.append(instr)
        r_element.append(fld_end)

        # Header: logo, top-left, small, on every page of every document.
        header = section.header
        header.is_linked_to_previous = False
        header_para = header.paragraphs[0]
        header_para.alignment = 0  # left
        run = header_para.add_run()
        run.add_picture(str(LOGO_PNG), height=Cm(0.5))

        # Pandoc's own default reference.docx body is just a swatch of
        # literal style-name placeholders ("Heading 1", "Body Text.", ...)
        # — useless for judging what a real document actually looks like.
        # Rendering a realistic preview document through this styled base
        # (via --reference-doc) bakes real, meaningful demo content into
        # the final reference.docx while keeping every style, the header
        # logo, and the footer page-number field intact — pandoc copies
        # those through unchanged from whatever --reference-doc it's given.
        styled_base_path = Path(tmp) / "styled-base.docx"
        doc.save(str(styled_base_path))
        subprocess.run(
            [
                "pandoc", str(PREVIEW_CONTENT),
                f"--reference-doc={styled_base_path}",
                "--toc",
                "-o", str(OUTPUT),
            ],
            check=True,
        )
        print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
