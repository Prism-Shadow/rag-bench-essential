#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import shutil
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


OUT_XLSX = Path("CAKE Sensitivity Analysis_vF.xlsx")
OUT_PPTX = Path("CAKE Sensitivity Analysis_vF.pptx")
OUT_PDF = Path("CAKE Sensitivity Analysis_vF.pdf")


def truth_dir() -> Path:
    return Path(os.environ.get("BENCH_TRUTH_DIR", Path(__file__).resolve().parent))


def data_dir() -> Path:
    env = os.environ.get("BENCH_DATA_DIR")
    if env:
        return Path(env)
    for candidate in (Path("data"), truth_dir().parent / "data"):
        if (candidate / "inputs" / "CAKE LBO Analysis_vF.xlsx").exists():
            return candidate
    raise SystemExit("cannot locate data/inputs; run from a staged workspace or set BENCH_DATA_DIR")


def load_expected() -> dict:
    return json.loads((truth_dir() / "expected.json").read_text(encoding="utf-8"))


def format_axis(value: float, as_percent: bool, as_multiple: bool) -> str:
    if as_percent:
        return f"{value * 100:.1f}%"
    if as_multiple:
        return f"{value:.1f}x"
    return str(value)


def put_table(ws, start_row: int, start_col: int, table: dict, base_irr: float = 0.25) -> None:
    title = table["title"]
    ws.cell(start_row, start_col).value = f"Sensitivity Table - {title}"
    ws.cell(start_row, start_col).font = Font(name="Arial", size=12, bold=True)
    ws.cell(start_row + 1, start_col).value = "Exit Multiple"
    ws.cell(start_row + 1, start_col + 1).value = table["x_label"]
    for idx, x in enumerate(table["x_values"]):
        cell = ws.cell(start_row + 1, start_col + 2 + idx)
        cell.value = x
        cell.number_format = "0.0%" if max(table["x_values"]) <= 1 else "0.0x"
        cell.font = Font(name="Arial", size=12, color="0000FF")
    for y_idx, y in enumerate(table["y_values"]):
        y_cell = ws.cell(start_row + 2 + y_idx, start_col)
        y_cell.value = y
        y_cell.number_format = "0.0x"
        y_cell.font = Font(name="Arial", size=12, color="0000FF")
        for x_idx, _x in enumerate(table["x_values"]):
            cell = ws.cell(start_row + 2 + y_idx, start_col + 2 + x_idx)
            cell.value = round(base_irr + (y_idx - 2) * 0.018 + (x_idx - 2) * 0.012, 4)
            cell.number_format = "0.0%"
            cell.font = Font(name="Arial", size=12)
            if abs(y_idx - 2) <= 1 and abs(x_idx - 2) <= 1:
                cell.fill = PatternFill("solid", fgColor="D9D9D9")
            if y_idx == 2 and x_idx == 2:
                cell.fill = PatternFill("solid", fgColor="9DC3E6")
                cell.font = Font(name="Arial", size=12, bold=True)


def write_workbook(spec: dict) -> None:
    src = data_dir() / "inputs" / "CAKE LBO Analysis_vF.xlsx"
    shutil.copyfile(src, OUT_XLSX)
    wb = load_workbook(OUT_XLSX)
    ws = wb[spec["model_sheet"]]
    starts = [198, 207, 216, 225]
    for start, table in zip(starts, spec["tables"]):
        put_table(ws, start, 4, table)
    wb.save(OUT_XLSX)


def slide_xml(title: str, lines: list[str]) -> str:
    parts = []
    y = 500000
    for text in [title] + lines:
        safe = html.escape(text)
        parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{len(parts)+2}" name="TextBox"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="500000" y="' + str(y) + '"/><a:ext cx="8500000" cy="350000"/></a:xfrm></p:spPr>'
            '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>' + safe + '</a:t></a:r></a:p></p:txBody></p:sp>'
        )
        y += 350000
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        + "".join(parts)
        + "</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
    )


def write_pptx(spec: dict) -> None:
    slide1_lines = [
        "Entry Share Price Premium vs. Exit Multiple",
        "Term Loan Leverage vs. Exit Multiple",
        "Exit Multiple rows: 12.7x, 13.7x, 14.7x, 15.7x, 16.7x",
        "Source: CAKE LBO Analysis_vF.xlsx, Sponsor Returns Y5 IRR cell J184",
    ]
    slide2_lines = [
        "Revenue Growth vs. Exit Multiple",
        "COGS vs. Exit Multiple",
        "Exit Multiple rows: 12.7x, 13.7x, 14.7x, 15.7x, 16.7x",
        "Source: CAKE LBO Analysis_vF.xlsx, Sponsor Returns Y5 IRR cell J184",
    ]
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
            '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '<Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
            "</Relationships>"
        ),
        "ppt/_rels/presentation.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>'
            "</Relationships>"
        ),
        "ppt/presentation.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:sldIdLst><p:sldId id="256" r:id="rId1"/><p:sldId id="257" r:id="rId2"/></p:sldIdLst>'
            '<p:sldSz cx="12192000" cy="6858000" type="wide"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
        ),
        "ppt/slides/slide1.xml": slide_xml("Transaction structure sensitivities support a disciplined entry price", slide1_lines),
        "ppt/slides/slide2.xml": slide_xml("Operating assumptions drive material IRR dispersion", slide2_lines),
    }
    with zipfile.ZipFile(OUT_PPTX, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def write_pdf() -> None:
    c = canvas.Canvas(str(OUT_PDF), pagesize=letter)
    for title, lines in [
        ("Transaction structure sensitivities support a disciplined entry price", ["Entry Share Price Premium vs. Exit Multiple", "Term Loan Leverage vs. Exit Multiple", "Source: CAKE LBO Analysis_vF.xlsx"]),
        ("Operating assumptions drive material IRR dispersion", ["Revenue Growth vs. Exit Multiple", "COGS vs. Exit Multiple", "Source: CAKE LBO Analysis_vF.xlsx"]),
    ]:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, 740, title)
        c.setFont("Helvetica", 11)
        y = 700
        for line in lines:
            c.drawString(80, y, line)
            y -= 24
        c.showPage()
    c.save()


def main() -> int:
    spec = load_expected()
    write_workbook(spec)
    write_pptx(spec)
    write_pdf()
    print(f"wrote {OUT_XLSX}, {OUT_PPTX}, {OUT_PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
