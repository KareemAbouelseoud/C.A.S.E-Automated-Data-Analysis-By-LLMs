import operator
from langchain_core.messages import  AIMessageChunk, AnyMessage
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict,Annotated
from .chatter import chatter_node,should_continue
from .botTools import tool_node
from dotenv import load_dotenv
import json
import numpy as np
from langchain.load import dump,load
from langgraph.checkpoint.memory import MemorySaver
import fireducks.pandas as pd
from API.Requests import chatbotRequests
checkpointer = MemorySaver()

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
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj
    
load_dotenv()
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    data_report: str
    project_id:str
    messages: Annotated[list[AnyMessage], operator.add]
    visual: Annotated[list[AnyMessage], operator.add]


builder = StateGraph(State)

builder.add_node("chatter_node", chatter_node) 
builder.add_node("tools",tool_node)

builder.add_edge(START, "chatter_node")
builder.add_conditional_edges('chatter_node', should_continue)
builder.add_edge('tools', 'chatter_node')
graph = builder.compile(checkpointer=checkpointer)


async def chat(user_input,thread_id=None):
    visuals=[]
    config={'configurable':{'thread_id':thread_id}}
    result=graph.get_state(config=config)

    if result[0]:
        graph_input = {'input':{'messages':[{'role':'user','content':user_input}]},'config':config,'stream_mode':["messages",'updates','values']}
    else:
        response=await chatbotRequests.get_history(thread_id)
        if response:
            print("History Retrieved")
            try:
                messages=json.loads(response[0])
            except:
                messages=[]
            data_report=response[1]
            project_id=response[2]
            messages.append({'role':'user','content':user_input})
            graph_input = {'input':{"messages": messages,'data_report':data_report,'project_id':project_id},'config':config,'stream_mode':["messages",'updates','values']}
    
    
    async for chunk in graph.astream(**graph_input,subgraphs=True):
        if chunk[1] == 'messages' and "chatter_node" in chunk[0][0]:
            if chunk[2][0].content and isinstance(chunk[2][0], AIMessageChunk):
                if chunk[2][0].content:
                    yield chunk[2][0].content
        elif chunk[1] == 'values':
            ## TODO:Save AGent used tools
            # print(chunk)
            pass

        elif chunk[1] == 'updates':
            
            if 'tools' in chunk[2]:
                if 'visual' in chunk[2]['tools']:
                    for visual in chunk[2]['tools']['visual']:
                        try:
                            visual=visual['figure_data']
                        except:
                            pass
                        visuals.append(visual)
            else:      
                status=json.dumps({'status':list(chunk[2].keys())[0]})
                print(status)
                yield status
            
        elif isinstance(chunk,dict):
            yield chunk
    
    for visual in visuals:
        yield json.dumps(visual)
                        
