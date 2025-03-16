from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])

async def planner_node(state):
    data_report=state['data_report']

    if 'preprocessing_mode' not in state:
        print("Planning Training Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-planner").messages[0].prompt.template
        mode = 'X'
        messages=[
            {"role": "system", "content":system_prompt },
            {"role": "user", "content": f"Data Report:\n {data_report}\n\nTrain Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
        ]

    else:
        print("Planning Target Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-y-planner").messages[0].prompt.template
        mode = 'Y'
        messages=[
            {"role": "system", "content":system_prompt },
            {"role": "user", "content": f"Data Report:\n {data_report}\n Target Feature: {state['y_column']}\n ONLY PREPROCESS THE TARGET FEATURE"},
        ]
    
    response= await llm.ainvoke(messages)
    if 'preprocessing_mode' not in state:
        return {"X_preprocessing_logic": response,"preprocessing_mode":mode}
    else:
        return {"Y_preprocessing_logic": response,"preprocessing_mode":mode}
    