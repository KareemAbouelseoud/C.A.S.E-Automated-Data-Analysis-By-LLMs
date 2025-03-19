from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import END
from langchain import hub
from preprocessingTools import tools
from API.Requests import projectRequests


load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-preprocessor-caller").messages[0].prompt.template

async def caller_node(state):
    # data_report=state['data_report']
    if state['preprocessing_mode']=='X':
        if 'X_preprocessing_messages' not in state or state['X_preprocessing_messages'] is None:
            old_messages= []
        else:
            old_messages = state["X_preprocessing_messages"]
    else:
        if 'Y_preprocessing_messages' not in state or state['Y_preprocessing_messages'] is None:
            old_messages= []
        else:
            old_messages = state["Y_preprocessing_messages"]
        
    messages=[
        {"role": "system", "content":system_prompt },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}\n Preprocessing Logic: {state['X_preprocessing_logic'] if state['preprocessing_mode']=='X' else state['Y_preprocessing_logic']}"},
    ]+old_messages
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages)

    if state['preprocessing_mode']=='X':
        return {"X_preprocessing_messages": [response]}
    else:
        return {"Y_preprocessing_messages": [response]}




async def should_continue(state) -> Literal['tools','__end__','planner_node']:
    mode = state['preprocessing_mode']
    
    messages = state["X_preprocessing_messages"][-1] if mode == 'X' else state["Y_preprocessing_messages"][-1]

    if messages.tool_calls:
        return "tools"
    else:
        if mode == 'X':
            print("X Preprocessing Done, Moving to Y Preprocessing")
            return "planner_node"
    return '__end__'
