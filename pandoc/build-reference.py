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
from docx.shared import RGBColor, Pt, Cm, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

REPO_ROOT = Path(__file__).resolve().parent.parent
# Stacked lockup (icon above wordmark), not the horizontal one — per direct
# feedback that the mark should read icon-over-text on the title page, not
# icon-beside-text. 512px is far more resolution than the ~0.7in print size
# below needs, but logo/build-logos.py's smallest common size (128px) would
# be visibly soft at that size, so round up rather than regenerate a
# one-off in-between size just for this.
LOGO_PNG = REPO_ROOT / "logo" / "png" / "lockup-stacked-black-512.png"
PANDOC_DIR = Path(__file__).resolve().parent
PREVIEW_CONTENT = PANDOC_DIR / "preview-content.md"
OUTPUT = PANDOC_DIR / "reference.docx"

ACCENT = RGBColor(0xA8, 0x55, 0xF7)   # colors.md: Accent (violet)
GRAY = RGBColor(0x6B, 0x6B, 0x6B)     # colors.md: Gray — mid
FONT = "Calibri"                      # typography.md
LOGO_HEIGHT = Cm(1.5)                 # ~3x the old 0.5cm header mark — see header block below

# Title-page design history, oldest first:
# 1. A curve+badge cover graphic (a large violet sweep + circular logo
#    badge) was built and rendered, then dropped after review — real SOC 2
#    / ISO 27001 policy documents converge on restrained, typographic title
#    pages, and illustrative shapes at fixed positions can't adapt to a
#    variable-length title without either colliding with the text or
#    requiring per-document layout.
# 2. A shaded "masthead band" (Title as a colored panel, inset within the
#    margins) replaced it — paragraph shading grows with wrapped text
#    automatically, a fixed shape does not.
# 3. The masthead band itself was later dropped per direct feedback: no
#    background color on Title, and the TenX logo moved from a small
#    top-left header mark to a large, centered lockup directly above the
#    title, so logo + title + Author/Date now read as one cohesive,
#    centered unit instead of a colored box with a corner logo. See the
#    header block and style_title() below for how that's built.


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
    # Pandoc's default styles carry theme-font attributes (w:asciiTheme etc.)
    # on the same rFonts element, and per ECMA-376 §17.3.2.26 theme
    # attributes OVERRIDE the literal ones when both are present — leaving
    # them in place means the style silently renders in the document theme's
    # font (Aptos Display in Pandoc 3.x), not Calibri. Strip them so the
    # literal values actually win.
    for attr in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rFonts.get(qn(attr)) is not None:
            del rFonts.attrib[qn(attr)]
    if color is not None:
        style.font.color.rgb = color
    if bold is not None:
        style.font.bold = bold
    if size is not None:
        style.font.size = size


def style_title(doc, size, text_color, bold=True, space_before=Pt(18), space_after=Pt(16)):
    """Plain Title style: no shading, no box, no indent — the logo above
    it (see the header block in main()) now carries the visual weight
    that a colored panel used to. Pandoc's default Title is already
    center-aligned, so centering doesn't need to be set here.

    space_before is the only lever controlling the gap between the
    header logo and this text (top_margin/header_distance set the floor;
    this adds a touch more breathing room on top of that) — kept small so
    the title reads as directly under the logo, one cohesive block, not a
    separate element. space_after is the gap down to Author, which does
    most of the remaining separation via its own space_before."""
    style = doc.styles['Title']
    style.font.color.rgb = text_color
    style.font.size = size
    style.font.bold = bold
    style.paragraph_format.space_before = space_before
    style.paragraph_format.space_after = space_after
    style.paragraph_format.line_spacing = 1.15


def style_meta_line(doc, style_name, size, text_color, space_before=Pt(0), space_after=Pt(2)):
    """Author/Date: plain gray text below the title. Safe to leave
    shading/indent/bold unset here now that Title itself carries none of
    those (Author/Date are basedOn Title in Pandoc's default
    reference.docx, so previously — when Title was a colored, indented,
    bold panel — this function had to explicitly override all three to
    avoid inheriting them; with Title plain, there's nothing left to
    override)."""
    style = doc.styles[style_name]
    style.font.color.rgb = text_color
    style.font.size = size
    style.font.bold = False
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

        # Pandoc's default reference.docx doesn't set page size/margins
        # explicitly (python-docx reads them back as None) — pin them so
        # the fixed vertical-positioning math below (centering the title,
        # pinning the metadata near the bottom) is against known numbers,
        # not whatever the rendering application happens to default to.
        section = doc.sections[0]
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        # top_margin is section-wide — it also sets where body text starts
        # on every page after the title page (TOC, then real content), not
        # just page 1. It's sized to fit header_distance + the now-larger
        # logo (see the header block below) plus a small buffer, and kept
        # as tight as that requires rather than pushed further down: doing
        # the latter to visually center the logo+title block on the title
        # page would waste that same extra space on every subsequent page.
        # Genuine vertical centering of a header-anchored element is out of
        # reach for that reason — same kind of hard OOXML wall as the
        # earlier rounded-corners case — so this settles for "logo sits
        # directly above the title as one tight, cohesive unit in the upper
        # part of the page" rather than "block is dead-center."
        section.header_distance = Inches(0.6)
        section.top_margin = Inches(1.3)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        set_style_font_color(doc, 'Normal')
        set_style_font_color(doc, 'Heading 1', color=ACCENT, bold=True, size=Pt(18))
        set_style_font_color(doc, 'Heading 2', color=ACCENT, bold=True, size=Pt(14))
        set_style_font_color(doc, 'Heading 3', color=ACCENT, bold=True, size=Pt(12))
        set_style_font_color(doc, 'TOC Heading', color=ACCENT, bold=True, size=Pt(18))
        # Title/Author/Date need the same Calibri treatment: shade_title_style
        # and style_meta_line set color/size/shading but never touch the font
        # name, so without these calls the three title-page styles keep ONLY
        # Pandoc's theme-font attributes and render in the theme font instead
        # of Calibri. Color/size/bold for these are set below.
        set_style_font_color(doc, 'Title')
        set_style_font_color(doc, 'Author')
        set_style_font_color(doc, 'Date')

        # Title: plain colored text (no panel — see the design-history
        # comment near ACCENT/LOGO_HEIGHT above), sitting directly under
        # the large centered logo in the header. Author/Date (company
        # name, version/confidentiality/date string) follow below.
        #
        # Vertical layout of the title page is a fixed-spacing
        # approximation, not true centering/bottom-anchoring — Pandoc
        # generates Title/Author/Date as plain top-down-flowing
        # paragraphs, and there's no page-relative vertical anchor
        # available at the paragraph-style level (that would need a
        # full-page table cell with vAlign, which would have to wrap
        # content Pandoc itself generates — not reachable via
        # --reference-doc styling).
        #
        # These numbers still need to survive a 2-line WRAPPED title
        # (tested: "Remote Access and Bring-Your-Own-Device (BYOD) Security
        # Policy") without the metadata paragraph silently overflowing onto
        # a real page 2 (confirmed failure mode of an earlier version of
        # these numbers — shifts every subsequent page number by one).
        style_title(doc, size=Pt(24), text_color=ACCENT, space_before=Pt(18), space_after=Pt(16))
        style_meta_line(
            doc, 'Author', size=Pt(11), text_color=GRAY,
            space_before=Pt(100), space_after=Pt(2),
        )
        style_meta_line(
            doc, 'Date', size=Pt(10), text_color=GRAY,
            space_after=Pt(0),
        )

        # Page break before TOC Heading — separates the title page from the
        # TOC page. Policies pass --toc; templates don't, so this only ever
        # fires for policy documents.
        doc.styles['TOC Heading'].paragraph_format.page_break_before = True

        # Footer: centered page number — but not on page 1. Page 1 is
        # always the title page for policy documents (or the only page
        # for a short template), and a page number there reads oddly with
        # no visible page content yet. Templates that run past one page
        # still get numbered from their actual page 2 onward, same as
        # policies.
        #
        # The XML this produces is spec-correct (titlePg set, a distinct
        # empty w:type="first" footer, a separate w:type="default" footer
        # carrying the PAGE field) and Word/Google Docs honor it exactly
        # as intended. LibreOffice 26.2 headless does not: verified with an
        # isolated minimal docx that as soon as ANY header is present —
        # even one identically defined for first-page and default, with no
        # other asymmetry at all — LO leaks the default footer's page
        # number onto page 1 regardless. This reproduces with or without
        # the brand header below, so it isn't something introduced by this
        # design; it's the same category of LO-headless-only limitation as
        # the TOC-field-population issue noted further down (a rendering
        # tool gap, not a document defect) and isn't worth chasing further
        # here — Word and Google Docs are the real targets.
        section.different_first_page_header_footer = True
        section.first_page_footer.is_linked_to_previous = False
        section.first_page_footer.paragraphs[0].text = ""

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

        # Header: logo, centered, large enough to anchor the title page
        # (see LOGO_HEIGHT/style_title above — it sits directly above
        # Title as one block). Defined explicitly for BOTH first-page and
        # default: with titlePg set (see the footer comment above), an
        # undefined first-page header renders BLANK per spec rather than
        # inheriting the default — and the title page is exactly where we
        # want the logo, so it needs its own explicit reference. Content
        # happens to be identical on every page here, which also just
        # reads as a reasonable consistent brand presence throughout.
        for header_obj in (section.first_page_header, section.header):
            header_obj.is_linked_to_previous = False
            header_para = header_obj.paragraphs[0]
            header_para.alignment = 1  # center
            run = header_para.add_run()
            run.add_picture(str(LOGO_PNG), height=LOGO_HEIGHT)

        # Tell any compliant consumer (Word, in particular) to refresh all
        # fields — including the policy TOC field — the moment the
        # document is opened, so a reader never has to manually press F9.
        # This does NOT fix LibreOffice's headless PDF export, which was
        # confirmed (by testing both this flag and an export-filter option)
        # to leave the TOC field unpopulated regardless — a rendering-tool
        # limitation, not a document defect. Word honors this flag per
        # spec, and Google Docs independently converts the field to its
        # own live, auto-refreshing TOC object at import time either way.
        update_fields = OxmlElement('w:updateFields')
        update_fields.set(qn('w:val'), 'true')
        doc.settings.element.insert(0, update_fields)

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
