#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build per-asset HTML pages (Bootstrap form style) and QR codes that link to those pages.
Input: Smart Asset Lab.xlsx (first sheet)
Output:
  - ./pages/<slug>.html (and index.html)
  - ./qrcodes/<slug>.png
  - ./qr_labels_A4_pages.pdf (A4 layout 3x8 for printing)

Usage:
  pip install pandas openpyxl "qrcode[pil]" reportlab Pillow
  python build_pages_and_qr.py
"""
import os, re, html, sys
import pandas as pd
from pathlib import Path
import qrcode
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

EXCEL_PATH = "Smart Asset Lab.xlsx"  # first sheet
OUT = Path("SmartAsset_QR_Pages")
PAGES = OUT / "pages"
QRPNG = OUT / "qrcodes"

# ใช้ของคุณแล้ว
BASE_URL = "https://copteryokky.github.io/SmartAsset_QR_Package/pages/"

# --- helpers ---------------------------------------------------------------
def ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else (url + "/")

def pick_id(row):
    # ให้ "รหัสเครื่องมือห้องปฏิบัติการ" มาก่อน จากนั้นจึง AssetID (วิธีที่ดีที่สุด)
    for k in ["รหัสเครื่องมือห้องปฏิบัติการ","AssetID","รหัส","รหัสครุภัณฑ์","Code","ID","Asset Id","Asset_ID"]:
        if k in row.index and pd.notna(row[k]) and str(row[k]).strip():
            return str(row[k]).strip()
    return f"ROW-{int(row.name)+1}"

def slugify(s):
    s = str(s or "").strip()
    s = re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE)  # เว้นวรรค/อักขระพิเศษ -> -
    s = re.sub(r"-+", "-", s).strip("-")               # ลด -- ให้เหลือ -
    return s or "item"

def render_page(title, rows):
    form_rows = ""
    for label, val in rows:
        sval = "" if (pd.isna(val) or str(val).lower()=="nan") else str(val)
        sval = html.escape(sval)
        form_rows += f"""
        <div class="mb-3 row">
          <label class="col-sm-3 col-form-label fw-semibold">{html.escape(str(label))}</label>
          <div class="col-sm-9">
            <input type="text" class="form-control" value="{sval}" readonly>
          </div>
        </div>"""
    return f"""<!doctype html>
<html lang="th">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body{{background:#f8fafc}}
      .card{{max-width:880px;margin:32px auto;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.06)}}
      .card-header{{background:#0d6efd;color:white;border-top-left-radius:16px;border-top-right-radius:16px}}
      .col-form-label{{color:#334155}}
      .form-control[readonly]{{background:#fff}}
    </style>
  </head>
  <body>
    <div class="card">
      <div class="card-header">
        <h4 class="m-0">ข้อมูลเครื่องมือห้องปฏิบัติการ</h4>
      </div>
      <div class="card-body">
        {form_rows}
        <div class="mt-4 text-center text-muted">© Smart Asset — QR Detail Page</div>
      </div>
    </div>
  </body>
</html>"""

# --- main ------------------------------------------------------------------
def main():
    # เช็คไฟล์ Excel ก่อน
    if not Path(EXCEL_PATH).exists():
        print(f"[ERROR] ไม่พบไฟล์ {EXCEL_PATH} ในโฟลเดอร์นี้", file=sys.stderr)
        sys.exit(1)

    base = ensure_trailing_slash(BASE_URL)

    OUT.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(exist_ok=True)
    QRPNG.mkdir(exist_ok=True)

    xl = pd.ExcelFile(EXCEL_PATH)
    sheet_name = xl.sheet_names[0]
    df = xl.parse(sheet_name).dropna(how="all").reset_index(drop=True)

    prefer = ["ลำดับ","ชื่อ","รหัสเครื่องมือห้องปฏิบัติการ","AssetID","ปี","ยี่ห้อ","โมเดล","หมายเลขเครื่อง",
              "ต้นทุนต่อหน่วย","สถานะ","สถานที่ใช้งาน (ปัจจุบัน)","ผู้รับผิดชอบ (ปัจจุบัน)","รูปภาพ","QR Code","_qr_image_path"]

    records = []
    used_slugs = set()  # กันชื่อชน

    for _, row in df.iterrows():
        asset_id = pick_id(row)
        slug = slugify(asset_id)

        # กันชื่อไฟล์ชน (เช่น LAB-001 ซ้ำ)
        orig = slug
        n = 2
        while slug in used_slugs:
            slug = f"{orig}-{n}"
            n += 1
        used_slugs.add(slug)

        # จัดลำดับแถวแสดงผล
        used = set(); rows_kv = []
        for k in prefer:
            if k in row.index:
                rows_kv.append((k, row[k])); used.add(k)
        for k in row.index:
            if k not in used:
                rows_kv.append((k, row[k]))

        # HTML ต่อรายการ
        html_str = render_page(asset_id, rows_kv)
        html_path = PAGES / f"{slug}.html"
        html_path.write_text(html_str, encoding="utf-8")

        # QR → ชี้ไปหน้าออนไลน์
        page_url = f"{base}{html_path.name}"
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
        qr.add_data(page_url); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img.save((QRPNG / f"{slug}.png").as_posix(), "PNG")

        records.append((asset_id, html_path.name))

    # index.html (เรียงตามชื่อทรัพย์สิน/ID)
    records_sorted = sorted(records, key=lambda x: str(x[0]))
    idx = "<!doctype html><meta charset='utf-8'><title>Smart Asset – Index</title><h2>Smart Asset – รายการหน้า</h2><ol>"
    for asset_id, fname in records_sorted:
        idx += f"<li><a href='{fname}'>{html.escape(asset_id)}</a></li>"
    idx += "</ol>"
    (PAGES / "index.html").write_text(idx, encoding="utf-8")

    # รวม QR ลง PDF (A4 3x8)
    page_w, page_h = A4
    c = canvas.Canvas((OUT / "qr_labels_A4_pages.pdf").as_posix(), pagesize=A4)
    left_margin = 10*mm; right_margin = 10*mm; top_margin = 12*mm; bottom_margin = 12*mm
    cols = 3; rows = 8
    usable_w = page_w - left_margin - right_margin
    usable_h = page_h - top_margin - bottom_margin
    cell_w = usable_w / cols; cell_h = usable_h / rows

    pngs = sorted(QRPNG.glob("*.png"))
    for i, png in enumerate(pngs):
        if i and i % (cols*rows) == 0:
            c.showPage()
        within = i % (cols*rows)
        r = within // cols
        cidx = within % cols
        x0 = left_margin + cidx * cell_w
        y0 = bottom_margin + (rows - 1 - r) * cell_h

        im = Image.open(png)
        iw, ih = im.size
        target_w = 42*mm; target_h = 52*mm
        aspect = iw/ih
        w = target_w; h = target_w/aspect
        if h > target_h: h = target_h; w = target_h*aspect
        x = x0 + (cell_w - w)/2; y = y0 + (cell_h - h)/2
        c.drawImage(ImageReader(im), x, y, width=w, height=h, preserveAspectRatio=True)

    c.save()
    print("Done. Open folder:", OUT.as_posix())

if __name__ == "__main__":
    main()
