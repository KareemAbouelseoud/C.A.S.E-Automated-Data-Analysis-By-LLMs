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


