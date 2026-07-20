import streamlit as st
from components.header import render_header
from components.sidebar import render_sidebar
from components.theme import configure_page
from utils.data_loader import load_reports_data, load_insight_data
from components.floating_ai import floating_ai
configure_page()
render_sidebar()
render_header()

st.title("📄 Audit Reports")

with st.spinner("Compiling Energy Intelligence Audit Report..."):
    report_data = load_reports_data()
    insight_data = load_insight_data()

if report_data:
    st.success("✅ Audit report generated successfully.")

    # AI reasoning-layer banner — this is the InsightAgent's judgment,
    # not a fixed rule, surfaced directly (perceive -> reason -> act).
    if insight_data:
        alert_level = insight_data.get("alert_level", "Normal")
        source = insight_data.get("source", "llm")

        banner_style = {
            "Urgent": ("🔴", "#FEE2E2", "#991B1B", "#DC2626"),
            "Watch": ("🟠", "#FFFBEB", "#78350F", "#F59E0B"),
            "Normal": ("🟢", "#ECFDF5", "#065F46", "#10B981"),
        }.get(alert_level, ("🟢", "#ECFDF5", "#065F46", "#10B981"))

        icon, bg, text_color, border = banner_style
        source_note = (
            "AI-generated judgment" if source == "llm"
            else "deterministic fallback — no LLM key configured"
        )

        st.markdown(
            f"""
            <div style="padding:16px 20px; border-radius:8px; background-color:{bg};
                        border:1px solid {border}; margin-bottom:16px;">
                <h3 style="margin:0; color:{text_color};">{icon} Alert Level: {alert_level}</h3>
                <p style="margin:6px 0 0; color:{text_color};">
                    <b>Primary concern:</b> {insight_data.get("primary_concern", "")}
                </p>
                <p style="margin:4px 0 0; font-size:0.85em; color:{text_color}; opacity:0.8;">
                    {source_note}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("🧠 AI Insight Agent — Reasoning"):
            st.write(insight_data.get("reasoning", ""))
            st.write("**Executive Summary:**")
            st.write(insight_data.get("executive_summary", ""))

    st.write("")

    # Render the markdown report directly in Streamlit
    st.markdown(report_data["summary_markdown"])

else:
    st.warning("Unable to generate reports data.")
floating_ai()