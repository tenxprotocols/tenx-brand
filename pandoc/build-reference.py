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
OUTPUT = Path(__file__).resolve().parent / "reference.docx"

ACCENT = RGBColor(0xA8, 0x55, 0xF7)  # colors.md: Accent (violet)
GRAY = RGBColor(0x6B, 0x6B, 0x6B)    # colors.md: Gray — mid
FONT = "Calibri"                     # typography.md


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


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base_path = Path(tmp) / "default-reference.docx"
        subprocess.run(
            ["pandoc", "-o", str(base_path), "--print-default-data-file", "reference.docx"],
            check=True,
        )
        doc = Document(str(base_path))

        set_style_font_color(doc, 'Normal')
        set_style_font_color(doc, 'Title', color=ACCENT, bold=True, size=Pt(28))
        set_style_font_color(doc, 'Heading 1', color=ACCENT, bold=True, size=Pt(18))
        set_style_font_color(doc, 'Heading 2', color=ACCENT, bold=True, size=Pt(14))
        set_style_font_color(doc, 'Heading 3', color=ACCENT, bold=True, size=Pt(12))
        set_style_font_color(doc, 'Author', color=GRAY, size=Pt(12))
        set_style_font_color(doc, 'Date', color=GRAY, size=Pt(12))
        set_style_font_color(doc, 'TOC Heading', color=ACCENT, bold=True, size=Pt(18))

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

        doc.save(str(OUTPUT))
        print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
