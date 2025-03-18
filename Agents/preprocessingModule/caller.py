"""
caller.py

This module invokes the appropriate preprocessing tool.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
from preprocessingtools import tools
from typing import Literal

load_dotenv()

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

system_prompt = hub.pull("preprocessing-caller").messages[0].content

async def caller_node(state):
    """Invoke the selected preprocessing tool"""
    llm = ChatGoogleGenerativeAI(
        model=CONFIGURATIONS['model'],
        temperature=CONFIGURATIONS['temperature']
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Tool needed: {state['current_step']}"}
    ]
    
    model_with_tools = llm.bind_tools(tools, tool_choice='any')
    response = await model_with_tools.ainvoke(messages)
    
    return {
        **state,
        "messages": [*state.get("messages", []), response],
        "next": "tool_node"
    }

async def tool_brancher(state) -> Literal["caller", "__end__"]:
    return state['next']