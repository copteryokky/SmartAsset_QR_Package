# auth.py
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _load_users():
    """อ่านผู้ใช้จาก .env รูปแบบ:
    APP_USERS="admin:1234, user1:pass1"
    """
    raw = os.getenv("APP_USERS", "admin:1234")
    users = {}
    for pair in [p.strip() for p in raw.split(",") if p.strip()]:
        if ":" in pair:
            u, p = pair.split(":", 1)
            users[u.strip()] = p.strip()
    return users

def is_authed() -> bool:
    return bool(st.session_state.get("auth_user"))

def require_login():
    """ถ้ายังไม่ล็อกอิน ให้สวิตช์ไปหน้า Login"""
    if not is_authed():
        st.info("กรุณาเข้าสู่ระบบก่อน", icon="🔒")
        try:
            st.switch_page("pages/1_Login.py")
        except Exception:
            st.stop()

def login_form():
    st.header("เข้าสู่ระบบ")
    users = _load_users()
    with st.form("login"):
        u = st.text_input("ชื่อผู้ใช้", key="login_user")
        p = st.text_input("รหัสผ่าน", type="password", key="login_pass")
        ok = st.form_submit_button("เข้าสู่ระบบ")
    if ok:
        if u in users and users[u] == p:
            st.session_state["auth_user"] = u
            st.success(f"ยินดีต้อนรับ {u}")
            try:
                st.switch_page("pages/2_Smart_Asset_Dashboard.py")
            except Exception:
                st.experimental_rerun()
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

def logout_button(where="sidebar"):
    btn = st.sidebar if where == "sidebar" else st
    if btn.button("ออกจากระบบ", use_container_width=True):
        for k in ["auth_user", "login_user", "login_pass"]:
            st.session_state.pop(k, None)
        st.experimental_rerun()
