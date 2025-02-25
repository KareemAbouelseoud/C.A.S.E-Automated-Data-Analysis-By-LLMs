import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from Frontend.config.styles import set_page_config, load_custom_css

import plotly.express as px

from data_description_generator import AgentGraphState, data_description_generator_node
from report_generator import generate_report
import streamlit as st
from genai_config import model
from Frontend.components.sidebar import render_sidebar
from Frontend.components.dataset_overview import render_dataset_overview
from Frontend.components.ai_analysis import render_ai_analysis

import pandas as pd

sys.path.append(os.getcwd())

# Initialize page config and styles
set_page_config()
load_custom_css()


def create_visualization(df, card):
    breakdown = card["breakdown"]
    measure = card["measure"]
    agg_func, col = breakdown.split("(")[0], breakdown.split("(")[1].strip(")")

    plot_df = df.groupby(measure)[col].agg(agg_func.lower()).reset_index()

    fig = px.bar(
        plot_df,
        x=measure,
        y=col,
        title=f"{agg_func} of {col} by {measure}",
        color=measure,
        height=400,
    )

    if "score" in card:
        score = card["score"]
        if agg_func != "COUNT" and score > 0.5:
            fig.add_annotation(
                x=0.95,
                y=0.95,
                xref="paper",
                yref="paper",
                text=f"🚩 Attribution Alert ({score:.0%})\n(Largest value > 50% of total)",
                showarrow=False,
                bgcolor="white",
                font=dict(size=14, color="black"),
                bordercolor="#cccccc",
                borderwidth=1,
            )
    elif agg_func == "COUNT" and score > 0.2:
        fig.add_annotation(
            x=0.95,
            y=0.85,
            xref="paper",
            yref="paper",
            text=f"🌐 Distribution Shift ({score:.2f} JSD)",
            showarrow=False,
            bgcolor="#cce5ff",
            font=dict(size=14),
        )

    fig.update_layout(
        hovermode="x unified",
        showlegend=False,
        margin=dict(t=40, b=20),
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


def main():
    st.markdown(
        "<h1 class='main-title'>📊 Smart Dataset Analysis Suite</h1>",
        unsafe_allow_html=True,
    )

    uploaded_file, analysis_mode = render_sidebar()

    if uploaded_file is not None:
        try:
            #  nam processing
            original_name = os.path.splitext(uploaded_file.name)[0]
            clean_name = "".join(
                [c if c.isalnum() else " " for c in original_name]
            ).title()
            df = pd.read_csv(uploaded_file)

            # Data type conversions (not final)
            object_cols = df.select_dtypes(include=["object"]).columns
            df[object_cols] = df[object_cols].astype(str)
            category_cols = df.select_dtypes(include=["category"]).columns
            df[category_cols] = df[category_cols].astype("category")

            # Initialize analysis state
            state = AgentGraphState({"df": df, "dataset_name": clean_name})
            with st.spinner("🔍 Analyzing dataset structure..."):
                state = data_description_generator_node(state, model)
                state = generate_report(state)

            # Main content columns
            col1, col2 = st.columns([1, 2])

            # Render components
            render_dataset_overview(col1, df, state)
            state = render_ai_analysis(
                col2, df, state, analysis_mode, create_visualization
            )

        except Exception as e:
            st.error(f"Error processing dataset: {str(e)}")


if __name__ == "__main__":
    main()
