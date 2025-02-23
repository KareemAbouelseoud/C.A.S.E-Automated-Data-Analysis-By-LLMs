import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
from data_description_generator import AgentGraphState, data_description_generator_node
from QUGEN import QUGEN
from genai_config import model

sys.path.append(os.getcwd())

st.markdown("""
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
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 class='main-title'>📊 Smart Dataset Analysis Suite</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("Data Input")
        uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
        st.markdown("---")
        st.header("Analysis Settings")
        analysis_mode = st.selectbox("Analysis Depth", ["Basic", "Advanced"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            state = AgentGraphState({"df": df})
            
            if "description" not in st.session_state:
                with st.spinner("🔍 Analyzing dataset structure..."):
                    state = data_description_generator_node(state, model)
                    st.session_state["description"] = state["description"]
                    st.session_state["feedback"] = ""
                    st.session_state["accepted"] = False
                    st.session_state["rejected"] = False  
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("<h2 class='section-header'>Dataset Overview</h2>", unsafe_allow_html=True)
                
                with st.expander("📋 Basic Information", expanded=True):
                    st.markdown(f"""
                    **Rows:** {df.shape[0]}  
                    **Columns:** {df.shape[1]}  
                    **Numeric Features:** {len(df.select_dtypes(include='number').columns)}  
                    **Categorical Features:** {len(df.select_dtypes(include='object').columns)}
                    """)
                    
                    st.markdown("**Sample Data**")
                    st.dataframe(df.head(3), height=150)
                
                with st.expander("🔑 Dataset Schema"):
                    schema = state.get("schema", [])
                    st.write("**Column Names:**")
                    st.write(", ".join(schema))
                
                with st.expander("🧮 Basic Statistics"):
                    stats = state.get("basic_stats", pd.DataFrame())
                    st.dataframe(stats.style.format(precision=2), use_container_width=True)
            
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
                        st.rerun()
                
                if analysis_mode == "Advanced":
                    with st.spinner("🧠 Generating intelligent insights..."):
                        qugen = QUGEN(model=model)
                        state = qugen.invoke(state)
                    
                    st.markdown("<h3 class='section-header'>💡 Key Insights</h3>", unsafe_allow_html=True)
                    
                    if "insight_cards" in state:
                        for i, card in enumerate(state["insight_cards"][:5]):
                            with st.container():
                                st.markdown(f"""
                                <div class="data-card">
                                    <h4>📌 Insight #{i+1}: {card['question']}</h4>
                                    <p><em>{card['reason']}</em></p>
                                    <div class="metric-box">
                                        <b>Analysis Pattern:</b> {card['breakdown']} by {card['measure']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                try:
                                    fig = create_visualization(df, card)
                                    st.plotly_chart(fig, use_container_width=True)
                                except Exception as e:
                                    st.warning(f"Visualization error: {str(e)}")
                                
                                st.markdown("---")
                    else:
                        st.warning("No insights generated. Try adjusting analysis settings.")
        
        except Exception as e:
            st.error(f"Error processing dataset: {str(e)}")

def create_visualization(df, card):
    """Create interactive visualization for insight card"""
    breakdown = card['breakdown']
    measure = card['measure']
    agg_func, col = breakdown.split('(')[0], breakdown.split('(')[1].strip(')')
    
    plot_df = df.groupby(measure)[col].agg(agg_func.lower()).reset_index()
    
    fig = px.bar(
        plot_df,
        x=measure,
        y=col,
        title=f"{agg_func} of {col} by {measure}",
        labels={col: f"{agg_func} Value", measure: "Category"},
        color=measure,
        height=400
    )
    
    fig.update_layout(
        hovermode="x unified",
        showlegend=False,
        margin=dict(t=40, b=20),
        xaxis_title=None,
        yaxis_title=None
    )
    return fig

if __name__ == "__main__":
    main()
