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

load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("preprocessor").messages[0].prompt.template

async def preprocessor_node(state):
    project_id = state["project_id"]
    data_report=mainDatabase.fetch_data_report(project_id)
    old_messages = state["preprocessing_messages"]
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
    ]+old_messages
    model=llm.bind_tools(tools=tools,tool_choice='any')
    response= await model.ainvoke(messages)
    return {"preprocessing_messages": [response]}

async def should_continue(state)->Literal['preprocessor_node','__end__']:
    messages = state["preprocessing_messages"]
    last_message = messages[-1]
    if last_message.status == "error":
        return "preprocessor_node"
    return END