import operator
from langchain_core.messages import HumanMessage, SystemMessage, AIMessageChunk, AnyMessage
from langgraph.graph import START, MessagesState, StateGraph
from typing_extensions import TypedDict,Annotated,NotRequired
from Agents.Chatbot.chatter import chatter_node,should_continue
from Agents.Chatbot.botTools import tool_node
from dotenv import load_dotenv


load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str
    messages: Annotated[list[AnyMessage], operator.add]
    visual: NotRequired[Annotated[list[AnyMessage], operator.add]]

builder = StateGraph(State)

builder.add_node("chatter_node", chatter_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "chatter_node")
builder.add_conditional_edges('chatter_node', should_continue)

graph = builder.compile()


async def chat(user_input,project_id,messages=None):
    print(user_input)
    if not messages:
        # New Chat
        messages=[]
    messages.append({"role": "user", "content": user_input})
    visuals=[]
    async for chunk in graph.astream({"messages": messages,'project_id':project_id}, stream_mode=["messages",'updates']):
        print(chunk)
        if chunk[0] == 'messages':
            if chunk[1][0].content and isinstance(chunk[1][0], AIMessageChunk):
                if chunk[1][0].content:
                    yield chunk[1][0].content

        elif chunk[0] == 'updates':
            if 'tools' in chunk[1]:
                if 'visual' in chunk[1]['tools']:
                    for visual in chunk[1]['tools']['visual']:
                        visuals.append(visual)
    
    for visual in visuals:
        yield visual
                        
