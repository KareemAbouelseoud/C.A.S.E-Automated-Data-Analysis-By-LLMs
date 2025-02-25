from recurr import *


def set_page_config():
    st.set_page_config(
        page_title="Smart Dataset Analysis Suite", layout="wide", page_icon="📊"
    )


def load_custom_css():
    import streamlit as st

    st.markdown(
        """
    <style>
        .main-title {
            color: #ffffff;
            text-align: center;
            margin-bottom: 30px;
        }
        .section-header {
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-top: 25px;
        }
        .data-card {
            background-color: rgba(40, 40, 40, 0.9);
            color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border: 1px solid #4a4a4a;
        }
        .data-card h4 {
            color: #58a6ff;
        }
        .metric-box {
            background-color: rgba(50, 50, 50, 0.7);
            padding: 8px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
