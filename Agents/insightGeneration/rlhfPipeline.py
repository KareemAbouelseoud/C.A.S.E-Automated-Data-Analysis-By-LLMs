import sys
import os
from data_description_generator import AgentGraphState, data_description_generator_node,human_input
from langgraph.graph import StateGraph, END,START
from langgraph.types import Command,interrupt
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st
import pandas as pd

sys.path.append(os.getcwd())


graph_builder = StateGraph(AgentGraphState)
graph_builder.add_node("data_description", data_description_generator_node)
graph_builder.add_node("human_input", human_input)

graph_builder.add_edge(START, "data_description")  
 
graph_builder.add_edge("human_input", "data_description")  
graph_builder.add_edge("data_description", END)  


graph = graph_builder.compile()



st.title("Dataset Description Generator")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    state = AgentGraphState({"df": df})
    with st.spinner("Generating description..."):
        state = graph.invoke(state)
        st.write(state)
    # st.subheader("Generated Description")
    # st.write(state.get("description", "No description generated."))
    # st.subheader("User Feedback")
    # feedback = st.text_area("Provide feedback (or type 'accept' to confirm):", "")

    # if st.button("Submit Feedback"):
    #     if feedback.strip().lower() == "accept":
    #         st.success("Description accepted!")
    #     else:
    #         state["human_feedback"] = feedback   
    #         with st.spinner("Regenerating description based on feedback..."):
    #             state = graph.invoke(state)

    #         st.subheader("Updated Description")
    #         st.write(state.get("description", "No updated description generated."))