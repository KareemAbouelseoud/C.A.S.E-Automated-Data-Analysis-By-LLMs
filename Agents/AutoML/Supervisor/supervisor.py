from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from .supervisorTools import tools
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import logging
import warnings

# Configure logging to suppress specific warnings
logging.getLogger('langsmith._internal._serde').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning, module='langsmith')

load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.5-flash-preview-04-17",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-supervisor").messages[0].prompt.template

def format_message(message):
    if isinstance(message, dict):
        return {"role": message["role"], "content": message["content"]}
    elif isinstance(message, AIMessage):
        # Parse tool calls from AIMessage
        if hasattr(message, 'tool_calls'):
            for tool_call in message.tool_calls:
                if 'args' in tool_call and 'state' in tool_call['args']:
                    del tool_call['args']['state']
        return message
    elif isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    elif isinstance(message, SystemMessage):
        return {"role": "system", "content": message.content}
    return message

async def supervisor_node(state):
    data_report=state['data_report']
    old_messages = state.get('messages',[])
    content=f"latest Data Report:\n {data_report}\n"
    if state.get('user_preferences',None):
        content+=f"Here is the user preferences: {state['user_preferences']}\n"
    if state.get('mode',None):
        content+=f"Here is the mode selected by the user: {state['mode']}\n"
    
    messages=[
        {"role": "system", "content":system_prompt},
        {'role':'user','content':content}
    ]
    
    # Format old messages
    for msg in old_messages:
        formatted_msg = format_message(msg)
        if formatted_msg:
            messages.append(formatted_msg)
    
    model=llm.bind_tools(tools=tools)
    print("Supervisor is being called")
    response= await model.ainvoke(messages)
    return {"messages": messages[2:]+[response]}

async def should_continue(state) -> Literal['tools','__end__','supervisor_node']:
    messages = state["messages"]
    steps = state["steps"]
    if messages[-1].tool_calls and steps<20:
        return "tools"
    else:
        if state.get('completed',{}).get('evaluator',False):
            return '__end__'
        else:
            return "supervisor_node"