import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from data_description_generator import AgentGraphState, data_description_generator_node
from QUGEN import QUGEN
from genai_config import model
import scoringFunction
from report_generator import generate_report

sys.path.append(os.getcwd())

st.markdown(
    """
<style>
    .main-title {
        color: #2c3e50;
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
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    st.markdown(
        "<h1 class='main-title'>📊 Smart Dataset Analysis Suite</h1>",
        unsafe_allow_html=True,
    )

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

    if uploaded_file is not None:
        try:
            original_name = os.path.splitext(uploaded_file.name)[0]
            clean_name = "".join(
                c if c.isalnum() else " " for c in original_name
            ).title()
            df = pd.read_csv(uploaded_file)
           

            ###
            object_cols = df.select_dtypes(include=["object"]).columns
            df[object_cols] = df[object_cols].astype(str)

            category_cols = df.select_dtypes(include=["category"]).columns
            df[category_cols] = df[category_cols].astype("category")

            ###
            state = AgentGraphState({"df": df, "dataset_name": clean_name})
            if "description" not in st.session_state:
                with st.spinner("🔍 Analyzing dataset structure..."):
                    state = data_description_generator_node(state, model)
                    state = generate_report(state)
                    st.session_state["description"] = state["description"]
                    st.session_state["feedback"] = ""
                    st.session_state["accepted"] = False
                    st.session_state["rejected"] = False  

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(
                    "<h2 class='section-header'>Dataset Overview</h2>",
                    unsafe_allow_html=True,
                )

                with st.expander("📋 Basic Information", expanded=True):
                    st.markdown(f"""
                    **Rows:** {df.shape[0]}  
                    **Columns:** {df.shape[1]}  
                    **Numeric Features:** {len(df.select_dtypes(include="number").columns)}  
                    **Categorical Features:** {len(df.select_dtypes(include="object").columns)}
                    """)

                    st.markdown("**Sample Data**")
                    st.dataframe(df.head(5), height=150)

                with st.expander("🔑 Dataset Schema"):
                    # BUG : Take Care of state is cleared when rerun
                    schema = df.columns.tolist()
                    st.write("**Column Names:**")
                    st.write(", ".join(schema))
                
                with st.expander("🧮 Basic Statistics"):
                    numerical_stats = df.describe(include=["number"]).reset_index()
                    categorical_stats = df.describe(include=["object", "category"]).reset_index()

                    stats = {"numerical": numerical_stats, "categorical": categorical_stats}

                    st.subheader("Numerical Statistics")
                    if "numerical" in stats:
                        numerical_df = (
                            pd.DataFrame(stats["numerical"])
                            if isinstance(stats["numerical"], dict)
                            else stats["numerical"]
                        )
                        st.dataframe(
                            numerical_df.style.format(precision=2),
                            use_container_width=True,
                        )
                    else:
                        st.warning("No numerical columns found")

                    st.subheader("Categorical Statistics")
                    if "categorical" in stats:
                        categorical_df = (
                            pd.DataFrame(stats["categorical"])
                            if isinstance(stats["categorical"], dict)
                            else stats["categorical"]
                        )
                        st.dataframe(categorical_df, use_container_width=True)
                    else:
                        st.warning("No categorical columns found")
            
            with col2:
                st.markdown("<h2 class='section-header'>AI Analysis Results</h2>", unsafe_allow_html=True)
                
                with st.expander("📄 Dataset Description", expanded=True):
                    st.write(st.session_state["description"])
                    st.markdown("**Feedback & Actions**")
                    
                if not st.session_state["accepted"]:
                    col_accept, col_reject = st.columns(2)
                    with col_accept:
                        if st.button("✅ Accept", key="accept_desc"):
                            st.session_state["accepted"] = True
                            st.session_state["rejected"] = False  
                            st.success("🎉 Description accepted!")
                            state['df'] = df
                            state['description'] = st.session_state["description"]
                            state['schema'] = schema
                            state['basic_stats'] = stats
                    
                    with col_reject:
                        if st.button("❌ Reject", key="reject_desc"):
                            st.session_state["rejected"] = True  
                            st.session_state["feedback"] = ""
                
                if st.session_state["rejected"]:
                    st.session_state["feedback"] = st.text_area("🔄 Provide feedback to improve the description (optional):", value=st.session_state["feedback"])
                    
                    if st.button("🔁 Regenerate Description", key="regen_desc"):
                        feedback_text = st.session_state["feedback"].strip()
                        state = data_description_generator_node(state, model, user_feedback=feedback_text if feedback_text else None)
                        st.session_state["description"] = state["description"]
                        st.session_state["feedback"] = ""
                        st.session_state["rejected"] = False  
                        st.write(st.session_state["description"])
                        ## BUG: Solve the issue of the buttons
                        st.rerun()
                
                if analysis_mode == "Advanced":
                    with st.spinner("🧠 Generating intelligent insights..."):
                        # Create state with required information
                        state = AgentGraphState({
                            "df": df,
                            "dataset_name": clean_name,
                            "schema": df.columns.tolist(),
                            "description": st.session_state.get("description", ""),
                            "basic_stats": {
                                "numerical": df.describe(include=["number"]).reset_index(),
                                "categorical": df.describe(include=["object", "category"]).reset_index()
                            }
                        })
                        
                        qugen = QUGEN(model=model)
                        state = qugen.invoke(state)

                    st.markdown(
                        "<h3 class='section-header'>💡 Key Insights</h3>",
                        unsafe_allow_html=True,
                    )

                    if "insight_cards" in state:
                        for i, card in enumerate(state["insight_cards"][:5]):
                            with st.container():
                                st.markdown(
                                    f"""
                                <div class="data-card">
                                    <h4>📌 Insight #{i + 1}: {card["question"]}</h4>
                                    <p><em>{card["reason"]}</em></p>
                                    <div class="metric-box">
                                        <b>Analysis Pattern:</b> {card["breakdown"]} by {card["measure"]}
                                    </div>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                                try:
                                    fig = create_visualization(df, card)
                                    st.plotly_chart(fig, use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Visualization error: {str(e)}")

                                st.markdown("---")
                    else:
                        st.warning(
                            "No insights generated. Try adjusting analysis settings."
                        )

        except Exception as e:
            st.error(f"Error processing dataset: {str(e)}")


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
        if agg_func != "COUNT":
            if score > 0.5:
                fig.add_annotation(
                    x=0.95,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=f"🚩Attribution Alert ({score:.0%}\n the largest value in a set is more than 50% of the total)",
                    showarrow=False,
                    bgcolor="#ffcccc",
                    font=dict(size=14),
                )
    elif agg_func == "COUNT":
        if score > 0.2:
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


if __name__ == "__main__":
    main()
