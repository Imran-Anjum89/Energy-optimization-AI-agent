from pathlib import Path

import streamlit as st

from components.theme import configure_page
from components.sidebar import render_sidebar


configure_page()

render_sidebar()

css = Path(__file__).parent / "assets" / "styles.css"

with open(css) as f:

    st.markdown(

        f"<style>{f.read()}</style>",

        unsafe_allow_html=True

    )