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

from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

system_prompt = hub.pull("preprocessing-planner").messages[0].prompt.template

class Planner(BaseModel):
    next: Literal["coder", "caller"] = Field(description="The next step in the workflow")
    reasoning: str = Field(description="The reasoning for the next step in the workflow")

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

async def planner_node(state):
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
    current_task_index = state["current_task_index"]
    preprocessing_tasks = state["preprocessing_tasks"]
    
    if current_task_index >= len(preprocessing_tasks):
        return {"next": "__end__", "preprocessed_dataframe": state.get('dataframe')}
    
    current_task = preprocessing_tasks[current_task_index]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"preprocessing task: {current_task['task']}, strategy: '{current_task['strategy']}'"}
    ]
    try:
        response = await llm.with_structured_output(Planner).ainvoke(messages)
        print(f"Planner decided next step: {response.next}\n")
        return {"next": response.next, "reasoning": response.reasoning}
    except Exception as e:
        print(f"Planner failed to determine next step. Error: {e}")
        return {"next": "planner"}

async def planner_brancher(state) -> Literal["caller", "coder"]:
    return state['next']