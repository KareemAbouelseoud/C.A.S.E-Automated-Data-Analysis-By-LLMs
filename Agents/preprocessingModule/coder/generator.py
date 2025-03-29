from langchain_google_genai import ChatGoogleGenerativeAI
from API.Requests.projectRequests import get_dataset
from pydantic import BaseModel, Field
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class PreprocessingCode(BaseModel):
    """Schema for preprocessing code solution"""
    description: str = Field(description="Brief description of the preprocessing approach")
    imports: str = Field(description="Required import statements")
    preprocessing_logic: str = Field(description="Python code implementing the preprocessing step")

CONFIG = {
    'model': "gemini-2.0-pro",
    'temperature': 0.3,
    'max_retries': 3
}

#TODO: further improvmements to the system prompt and add to langsmith hub
llm = ChatGoogleGenerativeAI(model=CONFIG['model'], temperature=CONFIG['temperature'])
system_prompt = hub.pull("preprocessing-coder-generator").messages[0].prompt.template

async def generator_node(state):
    """Generate preprocessing code using LLM"""
    print("---GENERATING PREPROCESSING CODE---")
    
    preprocessing_step = state['preprocessing_steps']
    target_columns = state['target_columns']

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Preprocessing step: {preprocessing_step} \n\n traget column: \n {target_columns}"
            "please generate the code for the preprocessing step following the required format and the constraints specified by the system"
        }
    ]
    
    try:
        code_solution = await llm.with_structured_output(PreprocessingCode).ainvoke(messages)
        
        return {
            **state,
            "generation": code_solution,
            "messages": state["messages"] + [
                ("assistant", f"Generated code for: {state['current_step']}")
            ]
        }
        
    except Exception as e:
        return {
            **state,
            "error": f"Generation failed: {str(e)}",
            "messages": state["messages"] + [
                ("user", f"Code generation error: {str(e)}")
            ]
        }