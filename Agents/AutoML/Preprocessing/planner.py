from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
from langchain import hub
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"deepseek-ai/deepseek-r1",
}

llm = ChatNVIDIA(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
system_prompt = hub.pull("automl-preprocessor-planner").messages[0].prompt.template

async def planner_node(state):
    print("Planning Preprocessing") 
    data_report=state['data_report']
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
    ]
    response= await llm.ainvoke(messages)
    print("PLANNER:",response)
    return {"preprocessing_logic": response}
    