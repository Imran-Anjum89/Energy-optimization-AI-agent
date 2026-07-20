import streamlit as st


def render_kpi_cards():

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "⚡ Energy Usage",
            "776 kWh",
            "+2.6%"
        )

    with col2:
        st.metric(
            "💰 Estimated Cost",
            "₹8,540",
            "-4.2%"
        )

    with col3:
        st.metric(
            "🌱 CO₂ Reduction",
            "32 kg",
            "+8%"
        )

    with col4:
        st.metric(
            "🤖 AI Status",
            "Online",
            "5 Agents"
        )