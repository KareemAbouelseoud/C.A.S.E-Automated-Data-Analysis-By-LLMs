import sys
import os
from data_description_rlhf import AgentGraphState, data_description_generator_node,human_input,end_node
from langgraph.graph import StateGraph, END,START
from langgraph.types import Command,interrupt
from langgraph.checkpoint.memory import MemorySaver
from genai_config import model
import uuid
import pandas as pd
sys.path.append(os.getcwd())

#GRAPH PIPELINE
graph_builder = StateGraph(AgentGraphState)
#define nodes
graph_builder.add_node("data_description", data_description_generator_node)
graph_builder.add_node("human_node", human_input)
graph_builder.add_node("end_node", end_node)
#define edges
graph_builder.add_edge(START, "data_description")
graph_builder.add_edge("data_description", "human_node")
graph_builder.add_edge("human_node", "data_description")
# graph_builder.add_edge("human_node", "end_node") 
# graph_builder.set_finish_point("end_node")

#compile the graph
checkpointer=MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

#TEST
thread_config= {"configurable": {"thread_id": uuid.uuid4()}}
#mock dataset
df = "first column:200,300 and second column:john,mary"
state = AgentGraphState({"df": df})  

for chunk in graph.stream(state, config=thread_config):
    for node_id, value in chunk.items():
        if node_id == "__interrupt__":
            while True:
                user_feedback = input("Provide feedback (or type 'done' to finish): ")
                graph.invoke(Command(resume=user_feedback), config=thread_config)
                #break if user says "done"
                if user_feedback.lower() == "done":
                    break


# import streamlit as st
# # --- Streamlit App ---
# st.title("Automated Data Analysis with LLMs")

# # Initialize session state
# if "state" not in st.session_state:
#     st.session_state.state = AgentGraphState({"df": "first column:200,300 and second column:john,mary", "human_feedback": []})
# if "feedback" not in st.session_state:
#     st.session_state.feedback = ""
# if "step" not in st.session_state:
#     st.session_state.step = 0
# if "history" not in st.session_state:
#     st.session_state.history = []
# if "interrupt" not in st.session_state:
#     st.session_state.interrupt = False

# # Stream execution
# thread_config = {"configurable": {"thread_id": uuid.uuid4()}}
# graph_steps = list(graph.stream(st.session_state.state, thread_config))

# if st.session_state.step < len(graph_steps):
#     current_chunk = graph_steps[st.session_state.step]

#     for node_id, value in current_chunk.items():
#         if node_id == "__interrupt__":
#             st.session_state.interrupt = True
#         else:
#             st.session_state.history.append(value)
#             st.write(value)

# # Display past messages
# st.write("### Previous Responses")
# for msg in st.session_state.history:
#     st.write(msg)

# # Handle feedback without rerunning
# if st.session_state.interrupt:
#     feedback = st.text_input("Provide feedback (or type 'done' to finish):", key="feedback")

#     if st.button("Submit Feedback"):
#         if feedback.lower() == "done":
#             st.session_state.interrupt = False
#             response = graph.invoke(Command(resume=feedback), thread_config)
#             st.session_state.history.append(response["description"])
#             st.session_state.feedback = ""
#         else:
#             st.session_state.state["human_feedback"].append(feedback)
#             st.session_state.feedback = ""

# # Continue button without rerun
# if not st.session_state.interrupt and st.session_state.step < len(graph_steps):
#     if st.button("Continue"):
#         st.session_state.step += 1