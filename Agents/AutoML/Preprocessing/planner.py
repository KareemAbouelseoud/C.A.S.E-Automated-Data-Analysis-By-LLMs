from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.5-flash-preview-04-17",
}

llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])

async def planner_node(state):
    data_report=state['data_report']
    last_message = ""
    
    if state.get('evaluation_metrics', None):
        last_message+=f"Here are the evaluation metrics for your previous steps: {state['evaluation_metrics']}\n\n Attempt to Analyze and Improve, if possible, if not return the same values.\n\n"
    
    if state.get('task', None):
        last_message+=f"Here are the instructions for you given by the supervisor: {state['task']}\n\n"
    
    if state['preprocessing_mode'] == 'X':
        print("Planning Training Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-planner").messages[0].prompt.template
        last_message+=f"Here is the lastest data available: Data Report:\n {data_report}\n\n Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"
    else:
        print("Planning Target Preprocessing")
        system_prompt = hub.pull("automl-preprocessor-y-planner").messages[0].prompt.template
        last_message+=f"Data Report:\n {data_report}\n Target Feature: {state['y_column']}\n ONLY PREPROCESS THE TARGET FEATURE"
    
    if state.get('preprocessing_pipeline', None):
        last_message+=f"Here is the latest preprocessing pipeline {state['preprocessing_pipeline']}\n\n"
        
    if state.get('model_names', None):
        last_message+=f"Here are the models going to be trained potentially do not put major dependence on it: {state['model_names']}\n\n"

    messages=[
            {"role": "system", "content":system_prompt},
        ] + state.get('planner_messages', [])
    messages.append({"role": "user", "content": last_message})
    response= await llm.ainvoke(messages)

    new_messages=[messages[-1],
                  {"role": "assistant", "content": f"Here is the output: {response.model_dump_json()}"}]
    return {"preprocessing_logic": response,'planner_messages':new_messages}