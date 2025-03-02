from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal,List
from langgraph.graph import END
from langchain import hub
from preprocessingTools import tools
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
from pydantic import BaseModel,Field

load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-preprocessor-caller").messages[0].prompt.template

async def caller_node(state):

    print("Calling Preprocessor Tools")
    project_id = state["project_id"]
    data_report=mainDatabase.fetch_data_report(project_id)
    print(f"=======================================\nthis is the state in caller:{state}\n====================================") 

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
        {"role": "user", "content": f"Data Report:\n {data_report} \n\nTrain Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}\n Preprocessing Logic: {state['X_preprocessing_logic'] if state['preprocessing_mode']=='X' else state['Y_preprocessing_logic']}"},
    ]+old_messages
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages)

    if state['preprocessing_mode']=='X':
        return {"X_preprocessing_messages": [response]}
    else:
        return {"Y_preprocessing_messages": [response]}





async def should_continue(state)->Literal['tools','__end__','caller_node']:
    if state['preprocessing_mode']=='X':
        messages = state["X_preprocessing_messages"][-1]
    else:
        messages = state["Y_preprocessing_messages"][-1]

    if messages.tool_calls!=[]:
        return "tools"
    else:
        if state['preprocessing_mode']=='X':
            state['preprocessing_mode']='Y'
            return "caller_node"
    return END