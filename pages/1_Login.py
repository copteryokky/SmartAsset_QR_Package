# pages/1_Login.py
import streamlit as st
from auth import login_form, is_authed, logout_button

st.set_page_config(page_title="เข้าสู่ระบบ", page_icon="🔐", layout="centered")

if is_authed():
    st.success("คุณเข้าสู่ระบบแล้ว")
    st.page_link("pages/2_Smart_Asset_Dashboard.py", label="ไปหน้า Dashboard ➜", icon="🧾")
else:
    login_form()

logout_button("sidebar")
