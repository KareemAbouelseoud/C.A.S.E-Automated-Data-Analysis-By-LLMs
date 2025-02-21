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
from Backend.services.project_service import ProjectService
_project_service=ProjectService()
from pydantic import BaseModel,Field

load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}
class LOGIC(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    logic: str = Field(description="The logic used to preprocess the data.")


llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-preprocessor-caller").messages[0].prompt.template

async def caller_node(state):
    project_id = state["project_id"]
    data_report=await _project_service.fetch_data_report(project_id)
    if 'preprocessing_messages' not in state or state['preprocessing_messages'] is None:
        old_messages= []
    else:
        old_messages = state["preprocessing_messages"]
        
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}\n Preprocessing Logic: {state['preprocessing_logic']}"},
    ]+old_messages
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages)
    return {"preprocessing_messages": [response]}





async def should_continue(state)->Literal['tools','__end__']:
    print(state['preprocessing_messages'])
    messages = state["preprocessing_messages"][-1]
    if messages.tool_calls!=[]:
        return "tools"
    return END