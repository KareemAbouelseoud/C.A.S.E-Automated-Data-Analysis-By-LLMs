import streamlit as st
from Flow.QUGEN import QUGEN
from genai_config import model
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def render_ai_analysis(col, df, state, analysis_mode, viz_function):
    with col:
        st.markdown(
            "<h2 class='section-header'>Analysis Results</h2>",
            unsafe_allow_html=True,
        )

        with st.expander("📄 Dataset Description", expanded=True):
            desc = state.get("description", "No description generated")
            st.write(desc)

        if analysis_mode == "Advanced":
            with st.spinner("🧠 Generating intelligent insights..."):
                qugen = QUGEN(model=model)
                state = qugen.invoke(state)

            st.markdown(
                "<h3 class='section-header'>💡 Key Insights</h3>",
                unsafe_allow_html=True,
            )

            if "insight_cards" in state:
                for i, card in enumerate(state["insight_cards"][:]):
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
                            fig = viz_function(df, card)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Visualization error: {str(e)}")
                        st.markdown("---")
            else:
                st.warning("No insights generated. Try adjusting analysis settings.")
    return state
