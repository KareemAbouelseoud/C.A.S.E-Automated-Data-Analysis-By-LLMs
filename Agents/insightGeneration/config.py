import copy
import sys
import os
import logging
from langgraph.graph import StateGraph, END,START
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import add_messages
import numpy as np
import pandas as pd
import uuid
from typing import Dict, Annotated,List
from pydantic import BaseModel, ConfigDict,Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from Data_description_generator.data_description_node import data_description_generator_node,DataDescription
from Data_description_generator.human_node import human_input
from Filteration.filteration_node import filterationA_node
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API.Requests.projectRequests import get_dataset,save_insights
from API.Endpoints.dataItems import Feedback,SaveInsights

def finalize_output(state: Dict[str, str]):
    """
    Finalize the output of the pipeline by converting all objects to JSON-serializable format.
    """
    # Create a deep copy to avoid modifying the original state
    final_state = {}
    
    # Handle insight cards
    if "insight_cards" in state:
        final_state["insight_cards"] = []
        for card in state["insight_cards"]:
            card_dict = card.model_dump()
            if hasattr(card, "resulted_df") and card.resulted_df is not None:
                card_dict["resulted_df"] = card.resulted_df.to_json() if not isinstance(card.resulted_df, str) else card.resulted_df
            final_state["insight_cards"].append(card_dict)
    
    # Handle advanced insight cards
    if "advanced_insight_cards" in state:
        final_state["advanced_insight_cards"] = {}
        for key, items in state["advanced_insight_cards"].items():
            final_state["advanced_insight_cards"][key] = []
            for subspace, card in items:
                card_dict = card.model_dump()
                if hasattr(card, "resulted_df") and card.resulted_df is not None:
                    card_dict["resulted_df"] = card.resulted_df.to_json() if not isinstance(card.resulted_df, str) else card.resulted_df
                
                # Convert subspace values to serializable format
                serializable_subspace = subspace.copy()
                if "filters" in serializable_subspace:
                    serializable_subspace["filters"] = [
                        (str(col), str(val) if isinstance(val, (int, float,np.int64, np.int32, np.int16, np.int8,np.float64, np.float32, np.float16,np.datetime64, pd.Timestamp)) else val)
                        for col, val in serializable_subspace["filters"]
                    ]
                
                final_state["advanced_insight_cards"][key].append((serializable_subspace, card_dict))
    
    # Handle description
    if "description" in state:
        final_state["description"] = state["description"].model_dump() if hasattr(state["description"], "model_dump") else state["description"]
    
    # Copy other simple fields
    for key in ["df", "schema", "human_feedback", "num_cards", "insights_explanation", "report"]:
        if key in state:
            final_state[key] = state[key]
    
    # print("Final state keys:", final_state.keys())
    final_state = make_serializable(final_state)
    print("Serialization check complete")

    # print("Final state after serialization:", final_state)
    return final_state

def PipelineGate(state):
    if state.get("num_iterations")==0 :
        print("This is the first Time to go through the pipeline Now the next node is the human node,num_iterations:", state.get("num_iterations"))
        return "human_node"
    else:
        print("This is the second Time to go through the pipeline Now the next node is the QUGEN node,num_iterations:", state.get("num_iterations"))
        return "qugen_node"

def restart_pipeline(state):
    if  state.get("num_iterations")==1 :
        print("rerunning pipeline,num_iterations:", state.get("num_iterations"))
        return "Report_Node"
    else:
        print("Finalizing output,num_iterations:", state.get("num_iterations"))
        return "Finalize_output"
def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.datetime64, pd.Timestamp)):
        print("FOUND DATETIME")
        print(obj)
        return obj.astype(str)
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj