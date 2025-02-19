import operator
from langchain_core.messages import HumanMessage, SystemMessage, AIMessageChunk, AnyMessage
from langgraph.graph import START, MessagesState, StateGraph
from typing_extensions import TypedDict,Annotated,NotRequired
from Agents.Chatbot.chatter import chatter_node,should_continue
from Agents.Chatbot.botTools import tool_node
from dotenv import load_dotenv
import json
import numpy as np
from langchain.load import dump,load
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
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj
    
load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str
    messages: Annotated[list[AnyMessage], operator.add]
    visual: Annotated[list[AnyMessage], operator.add]


builder = StateGraph(State)

builder.add_node("chatter_node", chatter_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "chatter_node")
builder.add_conditional_edges('chatter_node', should_continue)
builder.add_edge('tools', 'chatter_node')
graph = builder.compile()


async def chat(user_input,project_id,messages=None):
    if not messages:
        # New Chat
        messages=[]
    messages.append({"role": "user", "content": user_input})
    visuals=[]
    async for chunk in graph.astream({"messages": messages,'project_id':project_id}, stream_mode=["messages",'updates','values']):
        if chunk[0] == 'messages':
            if chunk[1][0].content and isinstance(chunk[1][0], AIMessageChunk):
                if chunk[1][0].content:
                    yield chunk[1][0].content
        elif chunk[0] == 'values':
            pass
        elif chunk[0] == 'updates':
            if 'tools' in chunk[1]:
                if 'visual' in chunk[1]['tools']:
                    for visual in chunk[1]['tools']['visual']:
                        visuals.append(visual)
    
    for visual in visuals:
        yield json.dumps(make_serializable(visual))
                        
