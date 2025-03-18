"""
planner.py

This module determines if preprocessing steps should use existing tools or require code generation.
"""

from typing import Literal
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

system_prompt = hub.pull("preprocessing-planner").messages[0].prompt.template

class Planner(BaseModel):
    next: Literal["coder", "caller"]

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

async def planner_node(state):
    """Determine if step can be handled by existing tools"""
    llm = ChatGoogleGenerativeAI(
        model=CONFIGURATIONS['model'],
        temperature=CONFIGURATIONS['temperature']
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Current step: {state['current_step']}"}
    ]
    
    response = await llm.with_structured_output(Planner).ainvoke(messages)
    return {'next': response.next}

async def planner_brancher(state) -> Literal["coder", "caller"]:
    return state['next']