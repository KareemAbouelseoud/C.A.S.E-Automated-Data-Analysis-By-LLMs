import streamlit as st

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def render_sidebar():
    with st.sidebar:
        st.header("Data Input")
        uploaded_file = st.file_uploader(
            "Upload CSV Dataset",
            type=["csv"],
        )
        st.markdown("---")
        st.header("Analysis Settings")
        analysis_mode = st.selectbox(
            "Analysis Depth",
            ["Basic", "Advanced"],
        )
    return uploaded_file, analysis_mode
