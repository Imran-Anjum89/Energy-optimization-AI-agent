import streamlit as st

from components.header import render_header
from components.kpi_cards import render_kpi_cards
from components.charts import daily_usage_chart
from components.metrics import current_usage
from components.agent_pipeline import render_pipeline
from components.recommendation_cards import recommendations


render_header()

render_kpi_cards()

st.write("")

left, right = st.columns([2,1])

with left:

    daily_usage_chart()

with right:

    current_usage()

st.write("")

render_pipeline()

st.write("")

recommendations()