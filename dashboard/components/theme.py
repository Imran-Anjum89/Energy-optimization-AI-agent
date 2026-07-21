import streamlit as st
from dashboard.components.auth_ui import show_login_interface
from pathlib import Path


def configure_page():

    st.set_page_config(

        page_title="Energy Intelligence Center",

        page_icon="⚡",

        layout="wide",

        initial_sidebar_state="expanded"
    )

    # Apply premium global CSS styles
    css_path = Path(__file__).parent.parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Enforce login check
    if "user" not in st.session_state or not st.session_state["user"]:
        show_login_interface()
        st.stop()