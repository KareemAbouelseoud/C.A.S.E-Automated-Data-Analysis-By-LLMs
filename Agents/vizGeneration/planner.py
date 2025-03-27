"""
planner.py

This module sets up a language model to plan the next steps in the workflow based on the state messages.
The language model is configured to choose the next node in the workflow.

Dependencies:
- langchain_google_genai
- pydantic
- langgraph.graph
- langchain_core.messages
- langchain
- dotenv

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the planner_node function to determine the next step in the workflow based on the state messages.

Classes:
- Planner: A Pydantic model to structure the output of the language model.

Functions:
- load_dotenv: Loads environment variables from a .env file.
- planner_node: Determines the next step in the workflow based on the state messages.
- planner_brancher: Returns the next node in the workflow based on the state.
- tool_brancher: Returns the next node in the workflow based on the state.

Variables:
- system_prompt: The system prompt template pulled from the hub.
"""
from typing import Literal
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
from pydantic import Field
from typing import List
load_dotenv()

system_prompt = hub.pull("viz-generation-planner").messages[0].prompt.template
class Planner(BaseModel):
    next: Literal["coder", "caller"] = Field(description="The next step in the workflow")

CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}


async def planner_node(design):
    class PlannerList(BaseModel):
        """Main structured output model"""
        next_list: List[Planner] = Field(
            description="List of whether the next step is coder or caller",
            min_length=len(design),
            max_length=len(design)
        )    
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": str(design)}
    ]
    if len(design)>1:
        while True:
            response =await llm.with_structured_output(PlannerList).ainvoke(messages)
            if len (response.next_list)==len(design):
                coder = []
                caller = []
                for idx,item in enumerate(design):
                    print(response.next_list[idx])
                    if response.next_list[idx].next == "coder":
                        coder.append(item)
                    elif response.next_list[idx].next == "caller":
                        caller.append(item)
                        
                if len(caller)+len(coder)==len(design):
                    return caller,coder
    else:
        response= await llm.with_structured_output(Planner).ainvoke(messages)
        return response.next