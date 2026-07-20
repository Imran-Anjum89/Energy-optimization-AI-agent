import streamlit as st
from dashboard.components.auth_ui import show_login_interface


def configure_page():

    st.set_page_config(

        page_title="Energy Intelligence Center",

        page_icon="⚡",

        layout="wide",

        initial_sidebar_state="expanded"
    )

    # Enforce login check
    if "user" not in st.session_state or not st.session_state["user"]:
        show_login_interface()
        st.stop()