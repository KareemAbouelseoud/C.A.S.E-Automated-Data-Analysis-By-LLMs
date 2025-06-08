
"""
planner.py

This module sets up a language model to plan the next steps in the workflow based on the state messages.
The language model is configured to choose the next node in the workflow.

Dependencies:
- typing
- pydantic
- langchain_google_genai
- langchain
- dotenv

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the planner_node function to plan the next steps in the workflow.
4. Use the planner_brancher function to branch the state messages based on the next node.

Functions:
- planner_node: Plan the next steps in the workflow.
- planner_brancher: Branch the state messages based on the next node.

Variables:
- system_prompt: The system prompt template pulled from the hub.
- Planner: A Pydantic model for the structured output of the language model.
"""

from typing import Literal, List, Tuple
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

system_prompt = hub.pull("preprocessing-planner").messages[0].prompt.template

class Planner(BaseModel):
    next: Literal["coder", "caller"] = Field(description="The next step in the workflow")
    reasoning: str = Field(description="The reasoning for the next step in the workflow")

class PlannerList(BaseModel):
    """Main structured output model for batch processing"""
    next_list: List[Planner] = Field(
        description="List of whether each task should go to coder or caller",
        min_length=1
    )

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

async def planner_node(state) -> Tuple[List[dict], List[dict]]:
    """
    Plan the next steps in the workflow based on the current state.
    
    Args:
        state (dict): The current state of the workflow containing:
            - preprocessing_tasks: List of preprocessing tasks
            - messages: List of messages in the conversation
    
    Returns:
        Tuple[List[dict], List[dict]]: A tuple containing:
            - List of tasks for the coder
            - List of tasks for the caller
    """
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
    preprocessing_tasks = state["preprocessing_tasks"]
    messages = state.get("messages", [])
    print(f"preprocessing_tasks: {preprocessing_tasks}")
    # Prepare messages for batch processing
    messages.append({
        "role": "system",
        "content": system_prompt
    })
    messages.append({
        "role": "user",
        "content": f"Here are the preprocessing tasks to route: {str(preprocessing_tasks)}"
    })
    
    try:
        # Get routing decisions for all tasks
        response = await llm.with_structured_output(PlannerList).ainvoke(messages)
        
        # Split tasks between coder and caller
        coder_tasks = []
        caller_tasks = []
        
        for idx, preprocessing_task in enumerate(preprocessing_tasks):
            if response.next_list[idx].next == "coder":
                coder_tasks.append(preprocessing_task)
            else:
                caller_tasks.append(preprocessing_task)
        
        print(f"Planner routed {len(coder_tasks)} tasks to coder and {len(caller_tasks)} tasks to caller")
        print(f"coder_tasks: {coder_tasks}")
        print(f"caller_tasks: {caller_tasks}")
        return coder_tasks, caller_tasks
        
    except Exception as e:
        print(f"Planner failed to route tasks. Error: {e}")
        return [], []

async def planner_brancher(state) -> Literal["caller", "coder"]:
    """
    Branch the state messages based on the next node.
    
    Args:
        state (dict): The current state of the workflow
        
    Returns:
        str: The next node to execute
    """
    # If we have tasks for both coder and caller, start with coder
    if state.get("coder_tasks") and state.get("caller_tasks"):
        return "coder"
    # If we only have caller tasks, go to caller
    elif state.get("caller_tasks"):
        return "caller"
    # If we only have coder tasks, go to coder
    elif state.get("coder_tasks"):
        return "coder"
    # If no tasks, end the workflow
    else:
        return "__end__"