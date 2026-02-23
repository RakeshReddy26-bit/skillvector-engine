"""SkillVector Engine — Modern Dashboard Application.

Single-entry Streamlit app with sidebar navigation,
custom dark theme, and multi-page routing.
"""

import logging
import os
import sys
import uuid

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from streamlit_option_menu import option_menu

from app.components.ui_helpers import inject_custom_css, render_footer
from src.db.database import init_db
from src.db.models import UserRepository, EventRepository
from src.auth.auth_service import AuthService
from src.utils.rate_limiter import RateLimiter

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# ── Database ─────────────────────────────────────────────────────────────────
init_db()

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="SkillVector Engine",
    page_icon="SV",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ────────────────────────────────────────────────────────
inject_custom_css()

# ── Cold start warning (Render free tier) ────────────────────────────────────
if os.getenv("RENDER") and "cold_start_dismissed" not in st.session_state:
    st.info(
        "This app runs on a free server that sleeps after 15 min of inactivity. "
        "First load may take ~30 seconds. Thanks for your patience!",
        icon="snowflake",
    )
    st.session_state["cold_start_dismissed"] = True

# ── Session state initialization ─────────────────────────────────────────────
if "rate_limiter" not in st.session_state:
    st.session_state["rate_limiter"] = RateLimiter(
        max_requests=int(os.getenv("RATE_LIMIT_PER_HOUR", "10")),
        window_seconds=3600,
    )
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())


# ── Auth helpers ─────────────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return "user_id" in st.session_state and st.session_state["user_id"] is not None


def is_admin() -> bool:
    if not is_logged_in():
        return False
    admin_email = os.getenv("ADMIN_EMAIL", "")
    user_email = st.session_state.get("user_email", "")
    return admin_email and user_email.lower() == admin_email.lower()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <div style="font-size: 28px; font-weight: 700; color: #FAFAFA; letter-spacing: -0.5px;">
            SkillVector
        </div>
        <div style="font-size: 12px; color: #8B949E; margin-top: 2px;">
            AI-Powered Career Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    nav_options = ["Dashboard", "Analyze", "Learning Path", "History"]
    nav_icons = ["speedometer2", "search", "diagram-3", "clock-history"]

    if is_admin():
        nav_options.append("Admin")
        nav_icons.append("shield-lock")

    selected_page = option_menu(
        menu_title=None,
        options=nav_options,
        icons=nav_icons,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#8B949E", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "padding": "10px 16px",
                "border-radius": "8px",
                "color": "#FAFAFA",
                "margin": "2px 0",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4F8BF9 0%, #6C63FF 100%)",
                "color": "white",
                "font-weight": "600",
            },
        },
    )

    st.markdown("---")

    # Auth section
    if is_logged_in():
        st.markdown(f"""
        <div style="padding: 8px 0;">
            <div style="font-size: 12px; color: #8B949E;">Logged in as</div>
            <div style="font-size: 14px; color: #FAFAFA; font-weight: 500;">
                {st.session_state.get('user_email', 'User')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            for key in ["user_id", "user_email"]:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        auth = AuthService()
        users = UserRepository()

        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", key="login_btn", use_container_width=True):
                user = users.get_user_by_email(email)
                if user and auth.verify_password(password, user["password_hash"]):
                    st.session_state["user_id"] = user["id"]
                    st.session_state["user_email"] = user["email"]
                    EventRepository().track("login", user_id=user["id"])
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with tab_register:
            reg_email = st.text_input("Email", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_pass2 = st.text_input("Confirm", type="password", key="reg_pass2")
            if st.button("Register", key="reg_btn", use_container_width=True):
                valid_email, email_err = auth.validate_email(reg_email)
                valid_pass, pass_err = auth.validate_password(reg_pass)
                if not valid_email:
                    st.error(email_err)
                elif not valid_pass:
                    st.error(pass_err)
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match.")
                elif users.user_exists(reg_email):
                    st.error("Account already exists.")
                else:
                    hashed = auth.hash_password(reg_pass)
                    user_id = users.create_user(reg_email, hashed)
                    st.session_state["user_id"] = user_id
                    st.session_state["user_email"] = reg_email
                    EventRepository().track("register", user_id=user_id)
                    st.success("Account created!")
                    st.rerun()

    # Footer info
    st.markdown("---")
    remaining = st.session_state["rate_limiter"].remaining(st.session_state["session_id"])
    st.markdown(f"""
    <div style="font-size: 11px; color: #8B949E; text-align: center;">
        {remaining} analyses remaining this hour
    </div>
    """, unsafe_allow_html=True)


# ── Page Routing ─────────────────────────────────────────────────────────────

if selected_page == "Dashboard":
    from app.pages.dashboard import render_dashboard
    render_dashboard()

elif selected_page == "Analyze":
    from app.pages.analyze import render_analyze
    render_analyze()

elif selected_page == "Learning Path":
    from app.pages.learning_path import render_learning_path
    render_learning_path()

elif selected_page == "History":
    from app.pages.history import render_history
    render_history()

elif selected_page == "Admin":
    from app.pages.admin import render_admin
    render_admin()


# ── Footer ───────────────────────────────────────────────────────────────────
render_footer()
