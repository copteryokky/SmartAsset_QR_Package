# pages/2_Smart_Asset_Dashboard.py
import io, re
from pathlib import Path
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from auth import require_login, logout_button

# ต้องล็อกอินก่อนเข้าหน้านี้
require_login()
st.set_page_config(page_title="Smart Asset Dashboard + QR", page_icon="🧾", layout="wide")

EXCEL_PATH = "Smart Asset Lab.xlsx"
OUT_DIR = Path("SmartAsset_QR_Pages")
DEFAULT_BASE_URL = "https://copteryokky.github.io/SmartAsset_QR_Package/pages/"

ID_PRIORITY = ["รหัสเครื่องมือห้องปฏิบัติการ","AssetID","รหัส","รหัสครุภัณฑ์","Code","ID","Asset Id","Asset_ID"]
PREFERRED_COLS = [
    "รหัสเครื่องมือห้องปฏิบัติการ", "AssetID", "ชื่อ", "ปี", "ยี่ห้อ", "โมเดล", "หมายเลขเครื่อง",
    "ต้นทุนต่อหน่วย", "สถานะ", "สถานที่ใช้งาน (ปัจจุบัน)", "ผู้รับผิดชอบ (ปัจจุบัน)"
]

def slugify(s: str) -> str:
    s = str(s or "").strip()
    s = re.sub(r"[^\w\-]+", "-", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "item"

def pick_id(row: pd.Series) -> str:
    for k in ID_PRIORITY:
        if k in row.index and pd.notna(row[k]) and str(row[k]).strip():
            return str(row[k])
    return f"ROW-{int(row.name)+1}"

def make_qr_img(url: str, box_size=10, border=4) -> Image.Image:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=box_size, border=border)
    qr.add_data(url); qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def draw_label_under(qr_img: Image.Image, top_text: str, bottom_text: str = "") -> Image.Image:
    W, H = qr_img.size
    label_h = 64
    out = Image.new("RGB", (W, H + label_h), "white")
    out.paste(qr_img, (0, 0))
    draw = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 18)
        font_b = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default(); font_b = ImageFont.load_default()
    def text_wh(text, font):
        if not text: return 0,0
        x0,y0,x1,y1 = draw.textbbox((0,0), text, font=font)
        return (x1-x0, y1-y0)
    tw, th = text_wh(top_text, font_b)
    draw.text(((W - tw)//2, H + 6), top_text, fill="black", font=font_b)
    if bottom_text:
        bw, bh = text_wh(bottom_text, font)
        draw.text(((W - bw)//2, H + 6 + th + 2), bottom_text, fill="black", font=font)
    return out

def layout_qr_pdf(png_paths, pdf_bytes_io):
    page_w, page_h = A4
    c = canvas.Canvas(pdf_bytes_io, pagesize=A4)
    left, right, top, bottom = 10*mm, 10*mm, 12*mm, 12*mm
    cols, rows = 3, 8
    usable_w = page_w - left - right
    usable_h = page_h - top - bottom
    cell_w = usable_w / cols; cell_h = usable_h / rows
    for i, p in enumerate(png_paths):
        if i and i % (cols*rows) == 0: c.showPage()
        r = (i % (cols*rows)) // cols; cidx = (i % cols)
        x0 = left + cidx * cell_w; y0 = bottom + (rows - 1 - r) * cell_h
        im = Image.open(p)
        iw, ih = im.size
        target_w, target_h = 42*mm, 52*mm
        aspect = iw/ih
        w, h = target_w, target_w/aspect
        if h > target_h: h = target_h; w = target_h*aspect
        x = x0 + (cell_w - w)/2; y = y0 + (cell_h - h)/2
        c.drawImage(ImageReader(im), x, y, width=w, height=h, preserveAspectRatio=True)
    c.save(); pdf_bytes_io.seek(0)

# ====== UI ======
st.title("Smart Asset Dashboard + QR")
st.caption("ค้นหา ดู QR พรีวิว ดาวน์โหลด PNG และสร้าง PDF รวม QR (A4 3×8) • สแกนแล้วไปยังหน้าออนไลน์ตาม BASE_URL")

if not Path(EXCEL_PATH).exists():
    st.error(f"ไม่พบไฟล์ Excel: {EXCEL_PATH}")
    st.stop()

df = pd.read_excel(EXCEL_PATH, sheet_name=0).dropna(how="all").reset_index(drop=True)
all_cols = df.columns.tolist()

with st.sidebar:
    st.subheader("ตัวกรอง")
    q = st.text_input("ค้นหา (ชื่อ/รหัส/คำที่อยู่ในแถว)")
    show_cols = st.multiselect("เลือกคอลัมน์ที่จะแสดง (ตารางล่าง)", options=all_cols,
                               default=[c for c in PREFERRED_COLS if c in all_cols] or all_cols[:6])
    st.divider()
    st.write("**ปลายทางหน้าออนไลน์ (BASE_URL)**")
    base_url = st.text_input("BASE_URL", value=DEFAULT_BASE_URL, help="ลงท้ายด้วย /")
    if not base_url.endswith("/"):
        st.warning("BASE_URL ควรลงท้ายด้วย '/'", icon="⚠️")

# filter
if q and q.strip():
    mask = pd.Series(False, index=df.index)
    qlow = q.strip().lower()
    for c in all_cols:
        mask |= df[c].astype(str).str.lower().str.contains(qlow, na=False)
    view = df[mask].copy()
else:
    view = df.copy()

st.subheader("ตารางรายการ")
st.dataframe(view[show_cols] if show_cols else view, use_container_width=True, height=320)

st.subheader("พรีวิว & ดาวน์โหลด")
colL, colR = st.columns([1,1])

with colL:
    label_col = "ชื่อ" if "ชื่อ" in all_cols else (show_cols[0] if show_cols else all_cols[0])
    options = [(f"{row.get(label_col,'')} · [{pick_id(row)}]", i) for i, row in view.iterrows()]
    if not options:
        st.info("ไม่พบรายการ")
    else:
        sel = st.selectbox("เลือกรายการ", options=options, format_func=lambda x: x[0])
        _, idx = sel
        row = view.loc[idx]
        rid = pick_id(row); slug = slugify(rid)
        title_txt = str(row.get("ชื่อ","")) if "ชื่อ" in row.index else ""
        url = f"{base_url}{slug}.html"
        st.write(f"**ลิงก์ปลายทาง:** {url}")
        qr = make_qr_img(url, box_size=10, border=4)
        qr_labeled = draw_label_under(qr, top_text=rid, bottom_text=title_txt)
        st.image(qr_labeled, caption="QR + ป้ายกำกับ", use_column_width=False)
        buf = io.BytesIO(); qr_labeled.save(buf, "PNG"); buf.seek(0)
        st.download_button("ดาวน์โหลด PNG ของรายการนี้", data=buf.getvalue(),
                           file_name=f"{slug}.png", mime="image/png")

with colR:
    st.markdown("### สร้าง PDF รวม QR (A4 3×8)")
    if st.button("สร้าง PDF และดาวน์โหลด"):
        tmp = OUT_DIR / "qrcodes_tmp"; tmp.mkdir(parents=True, exist_ok=True)
        pngs = []
        for _, r in view.iterrows():
            rid2 = pick_id(r); slug2 = slugify(rid2)
            url2 = f"{base_url}{slug2}.html"
            title2 = str(r.get("ชื่อ","")) if "ชื่อ" in r.index else ""
            img = draw_label_under(make_qr_img(url2), top_text=rid2, bottom_text=title2)
            p = tmp / f"{slug2}.png"; img.save(p.as_posix(), "PNG"); pngs.append(p.as_posix())
        pdf = io.BytesIO(); layout_qr_pdf(pngs, pdf)
        for p in pngs: Path(p).unlink(missing_ok=True)
        try: tmp.rmdir()
        except: pass
        st.download_button("ดาวน์โหลดไฟล์ PDF (A4 3×8)", data=pdf.getvalue(),
                           file_name="qr_labels_A4.pdf", mime="application/pdf")

logout_button("sidebar")
