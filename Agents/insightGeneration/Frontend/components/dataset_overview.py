import streamlit as st
import pandas as pd


def render_dataset_overview(col, df, state):
    with col:
        st.markdown(
            "<h2 class='section-header'>Dataset Overview</h2>", unsafe_allow_html=True
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
            schema = state.get("schema", [])
            st.write("**Column Names:**")
            st.write(", ".join(schema))

        with st.expander("🧮 Basic Statistics"):
            stats = state.get("basic_stats", {})

            st.subheader("Numerical Statistics")
            if "numerical" in stats:
                numerical_df = (
                    pd.DataFrame(stats["numerical"])
                    if isinstance(stats["numerical"], dict)
                    else stats["numerical"]
                )
                st.dataframe(
                    numerical_df.style.format(precision=2), use_container_width=True
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
