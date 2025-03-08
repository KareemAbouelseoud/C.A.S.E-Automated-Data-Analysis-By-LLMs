from typing import Dict
from langgraph.types import interrupt,Command
from QUGEN.node import qugen_node
import pandas as pd
from io import StringIO
import json
def human_input(state):
    """
    Interrupts graph execution for capturing human feedback and stores it in the state for the description
    node to process.
    """
    description= state["description"]

    user_feedback = interrupt(
        {"description": description, "message": "Provide feedback or type 'done' to finish."})
    # print(f"[human_input] Received human feedback: {user_feedback}")

    #if user types 'done', transition to qugen_node
    if user_feedback.lower() == "done":
        
        return Command(update={"human_node": state["human_feedback"] + ["Finalized"]}, goto="QUGEN")
    
    #otherwise,update feedback and return to first_node for re-generation
    return Command(update={"human_feedback": state["human_feedback"] + [user_feedback]}, goto="data_description")

# #for testing purposes
# def end_node(state):
#    print("end")