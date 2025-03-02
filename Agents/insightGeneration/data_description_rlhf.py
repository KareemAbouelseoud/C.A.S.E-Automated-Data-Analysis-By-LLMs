from typing import Dict, Annotated
from langgraph.types import interrupt,Command
from langgraph.graph import add_messages
from genai_config import model

#define states
class AgentGraphState(Dict):
    df: str
    description: Annotated[list[str], add_messages]
    human_feedback: Annotated[list[str], add_messages]


def data_description_generator_node(state: AgentGraphState) -> AgentGraphState:
    """
    Generates or refines the dataset description considering human feedback if provided.
    """
    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    feedback = state["human_feedback"] if "human_feedback" in state else ["No feedback yet"]
    prompt = f"""
    Human Feedback: {feedback[-1] if feedback else 'No feedback yet'}
       Given the dataset:
        {df}
        Consider previous human feedback to refine the response. 
        Provide the following:
        1. explanation of each column in bullet points.
        2. An overview description of the dataset.
        3. Key patterns in the data distribution.
        4. Notable data quality issues.
        """
        
    response = model.generate_content(prompt)
    description = response.text  
    print(f"current description:\n{response}\n")
   
    return {"description": [description], "human_feedback": feedback}

def human_input(state: AgentGraphState) -> AgentGraphState:
    """
    Interrupts graph execution for capturing human feedback and stores it in the state for the description
    node to process.
    """
    description= state["description"]

    user_feedback = interrupt(
        {"description": description, "message": "Provide feedback or type 'done' to finish."})
    # print(f"[human_input] Received human feedback: {user_feedback}")

    #if user types 'done', transition to end_node
    if user_feedback.lower() == "done":
        
        return Command(update={"human_node": state["human_feedback"] + ["Finalized"]}, goto="end_node")
    
    #otherwise,update feedback and return to first_node for re-generation
    return Command(update={"human_feedback": state["human_feedback"] + [user_feedback]}, goto="data_description")

#for testing purposes
def end_node(state: AgentGraphState) -> AgentGraphState:
    print("end end")