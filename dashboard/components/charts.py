import streamlit as st
import plotly.express as px
import pandas as pd


def daily_usage_chart():

    df = pd.DataFrame({

        "Day": [

            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
            "Sun"

        ],

        "Energy": [

            32,
            35,
            31,
            36,
            39,
            43,
            37

        ]

    })

    fig = px.line(

        df,

        x="Day",

        y="Energy",

        markers=True,

        title="Daily Energy Consumption"

    )

    fig.update_layout(

        height=400,

        template="plotly_white"

    )

    st.plotly_chart(

        fig,

        width="stretch"

    )