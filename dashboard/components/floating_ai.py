"""
Professional Floating AI Button
"""

import streamlit as st


def floating_ai():

    st.markdown("""
    <style>

    /* Hide default button styling */
    div[data-testid="stButton"] > button {

        position: fixed !important;

        right: 28px;
        bottom: 28px;

        width: 148px !important;
        height: 148px !important;

        border-radius: 50% !important;

        border: 2px solid rgba(255,255,255,.08) !important;

        background:
        radial-gradient(circle at 30% 30%,
        #4F46E5,
        #2563EB,
        #111827) !important;

        color: white !important;

        font-size: 0px !important;

        box-shadow:
        0 12px 35px rgba(37,99,235,.35),
        0 0 25px rgba(79,70,229,.30);

        transition: all .25s ease;

        z-index:999999;

    }


    div[data-testid="stButton"] > button:hover{

        transform: translateY(-4px) scale(1.08);

        box-shadow:
        0 18px 45px rgba(37,99,235,.45),
        0 0 35px rgba(79,70,229,.45);

    }


    div[data-testid="stButton"] > button:active{

        transform: scale(.95);

    }


    /* AI Icon */

    div[data-testid="stButton"] > button::before{

        content:"🤖";

        font-size:76px;

        position:absolute;

        left:50%;
        top:50%;

        transform:translate(-50%,-50%);

    }

    </style>

    """, unsafe_allow_html=True)

    if st.button("", key="global_ai_button"):
        st.switch_page("pages/09_AI_Assistant.py")