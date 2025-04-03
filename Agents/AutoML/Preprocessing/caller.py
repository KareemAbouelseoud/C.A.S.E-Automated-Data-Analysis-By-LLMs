from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import Literal
from langgraph.graph import END
from langchain import hub
from preprocessingTools import tools
from langchain_core.messages import ToolMessage


load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-preprocessor-caller").messages[0].prompt.template

async def caller_node(state):
    # data_report=state['data_report']        
    messages=[
        {"role": "system", "content":system_prompt },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}\n Preprocessing Logic: {state['preprocessing_logic']}"},
    ]+state.get('preprocessing_messages', [])
    
    last_message= messages[-1]
    if isinstance(last_message,ToolMessage):
        last_message.content+=f"The current Preprocessor has these steps: {state.get('preprocessing_pipeline',[])}"
    
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages)

    return {'preprocessing_messages': [response]}


async def should_continue(state)->Literal['tools','__end__']:
    messages = state["preprocessing_messages"]
    last_message = messages[-1]
    if last_message.tool_calls!=[]:
        return "tools"
    return END