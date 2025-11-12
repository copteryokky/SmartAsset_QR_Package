# Home.py
import streamlit as st
from auth import is_authed, logout_button

st.set_page_config(page_title="Asset Management System", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.hero{background:#0b2e4f;padding:20px;border-radius:16px;color:#eaf6ff;text-align:center;margin:12px 0 24px}
.hero h1{margin:0;font-size:38px}
.hero h3{margin:6px 0 0;opacity:.9;font-weight:500}
.card{background:#e6fbff;border:1px solid #bfeef7;border-radius:18px;padding:24px;box-shadow:0 6px 24px rgba(0,0,0,.08)}
.nav{display:flex;gap:18px;justify-content:flex-end;margin-bottom:8px}
.nav a{color:#0ea5e9;text-decoration:none;font-weight:600}
</style>
<div class="nav">
  <a href="#">หน้าหลัก</a>
  <a href="https://copteryokky.github.io/SmartAsset_QR_Package/pages/index.html" target="_blank">หน้าทรัพย์สิน (ออนไลน์)</a>
  <a href="https://github.com/copteryokky/SmartAsset_QR_Package" target="_blank">ที่มาโค้ด</a>
</div>
<div class="hero"><h1>โปรแกรมจัดการเครื่องมือแพทย์</h1><h3>Asset Management System</h3></div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1,1])
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ภาพรวม")
    st.write(
        "- สร้างหน้า HTML ต่อครุภัณฑ์จาก Excel\n"
        "- ทำ QR ให้สแกนไปหน้าออนไลน์\n"
        "- มี Dashboard ค้นหา/พรีวิว/ดาวน์โหลด PNG และรวม PDF 3×8"
    )
    if is_authed():
        st.success("คุณได้เข้าสู่ระบบแล้ว ✅")
        st.page_link("pages/2_Smart_Asset_Dashboard.py", label="ไปหน้า Smart Asset Dashboard + QR ➜", icon="🧾")
    else:
        st.page_link("pages/1_Login.py", label="เข้าสู่ระบบเพื่อใช้งาน Dashboard ➜", icon="🔐")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("ลิงก์ที่เกี่ยวข้อง")
    st.link_button("เปิดหน้า index (ออนไลน์)", "https://copteryokky.github.io/SmartAsset_QR_Package/pages/index.html")
    st.link_button("Repository", "https://github.com/copteryokky/SmartAsset_QR_Package")
    st.markdown('</div>', unsafe_allow_html=True)

logout_button("sidebar")
