from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from supervisorTools import tools
from typing import Literal

load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("automl-supervisor").messages[0].prompt.template

async def supervisor_node(state):
    data_report=state['data_report']
    old_messages = state["messages"]
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n latest Data Report:\n {data_report}"+f"Here is the user preferences: {state['user_preferences']}" if state.get('user_preferences',None) else ""},
    ]+old_messages
    model=llm.bind_tools(tools=tools)
    response= await model.ainvoke(messages)
    return {"messages": [response]}

async def should_continue(state) -> Literal['tools','__end__','supervisor_node']:
    messages = state["messages"]
    steps = state["steps"]
    if messages[-1].tool_calls and steps<20:
        return "tools"
    else:
        if state['completed']['evaluator']:
            return '__end__'
        else:
            return "supervisor_node"