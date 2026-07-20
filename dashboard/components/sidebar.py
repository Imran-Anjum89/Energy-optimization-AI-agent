"""
Premium Enterprise Sidebar
"""

import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="text-align:center;padding-top:10px;padding-bottom:15px;">

            <h2 style="margin-bottom:0px;color:#15803D;">
            ⚡ Energy Intelligence
            </h2>

            <p style="color:gray;margin-top:5px;">
            AI-Powered Optimization
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        pages = [

            ("🏠", "Overview", "pages/01_Overview.py"),

            ("📈", "Usage Analytics", "pages/02_Usage_Analytics.py"),

            ("🔮", "Forecasting", "pages/03_Forecasting.py"),

            ("🚨", "Anomaly Detection", "pages/04_Anomaly_Detection.py"),

            ("💡", "Recommendations", "pages/05_Recommendations.py"),

            ("🌱", "Sustainability", "pages/06_Sustainability.py"),

            ("📄", "Reports", "pages/07_Reports.py"),

            ("⚙", "Settings", "pages/08_Settings.py"),

            ("💬", "AI Assistant", "pages/09_AI_Assistant.py")

        ]

        for icon, label, page in pages:

            st.page_link(
                page,
                label=f"{icon}  {label}"
            )

        st.divider()

        st.markdown("### 🤖 AI Status")

        st.success("Online")

        st.markdown("### 📂 Dataset")

        st.info("Processed Dataset")

        st.markdown("### ⚙ Version")

        st.caption("v1.0.0")

        st.divider()

        st.caption(
            "© 2026 Energy Optimization Agent"
        )