from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
from langchain import hub
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"deepseek-ai/deepseek-r1",
}

llm = ChatNVIDIA(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])

async def planner_node(state):
    if 'preprocessing_mode' not in state or state['preprocessing_mode']=='X':
        print("Planning Training Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-planner").messages[0].prompt.template
    else:
        print("Planning Target Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-Yplanner").messages[0].prompt.template

    print(f"=======================================\nthis is the state in planner:{state}\n====================================")
    
    project_id = state["project_id"]
    data_report=mainDatabase.fetch_data_report(project_id)
    messages=[
        {"role": "system", "content":system_prompt },
        {"role": "user", "content": f"Data Report:\n {data_report}\n\nTrain Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
    ]
    
    response= await llm.ainvoke(messages)
    print(f"=======================================\nthis is the state in planner (end):{state}\n====================================")
    if 'preprocessing_mode' not in state or state['preprocessing_mode']=='X':
        if response.tool_calls!=[]:
            return {"X_preprocessing_messages": [response],"preprocessing_mode":'X'}
        else:
            return {"X_preprocessing_logic": response,"preprocessing_mode":'X'}
    else:
        if response.tool_calls!=[]:
            return {"Y_preprocessing_messages": [response],"preprocessing_mode":'Y'}
        else:
            return {"Y_preprocessing_logic": response,"preprocessing_mode":'Y'}
    