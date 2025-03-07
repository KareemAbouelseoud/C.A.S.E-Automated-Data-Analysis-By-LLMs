import sys
import os
from langgraph.graph import StateGraph, END,START
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from Flow.QUGEN.node import qugen_node
from Flow.Data_description_generator.data_description_node import data_description_generator_node,DataDescription
from Flow.Data_description_generator.human_node import human_input
import uuid
from typing import Dict, Annotated,List
from langgraph.graph import add_messages
import pandas as pd
sys.path.append(os.getcwd())

#define states
class AgentGraphState(Dict):
    df: str
    description: str
    human_feedback: Annotated[list[str], add_messages]
    insight_cards: List[Dict[str, str]]
   

#GRAPH PIPELINE
graph_builder = StateGraph(AgentGraphState)
#define nodes
graph_builder.add_node("data_description",  data_description_generator_node)
graph_builder.add_node("human_node", human_input)
graph_builder.add_node("QUGEN",qugen_node)
#define edges
graph_builder.add_edge(START, "data_description")
graph_builder.add_edge("data_description", "human_node")

#compile the graph
checkpointer=MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

#TEST
thread_config= {"configurable": {"thread_id": uuid.uuid4()}}
#mock dataset
# file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
# dataset = pd.read_csv(file_path)


df = "first col:200,100 ,second col:ok hi"
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


