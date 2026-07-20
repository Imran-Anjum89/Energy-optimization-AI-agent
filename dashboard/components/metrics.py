import streamlit as st


def current_usage():

    st.subheader("⚡ Current Usage")

    st.metric(

        "Current Load",

        "1.42 kW"

    )

    st.progress(65)

    st.caption("65% of today's expected peak")