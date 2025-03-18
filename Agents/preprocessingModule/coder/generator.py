from langchain_google_genai import ChatGoogleGenerativeAI
from API.Requests.projectRequests import get_dataset
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class PreprocessingCode(BaseModel):
    """Schema for preprocessing code solution"""
    description: str = Field(description="Brief description of the preprocessing approach")
    imports: str = Field(description="Required import statements")
    code: str = Field(description="Python code implementing the preprocessing step")

CONFIG = {
    'model': "gemini-2.0-pro",
    'temperature': 0.3,
    'max_retries': 3
}

llm = ChatGoogleGenerativeAI(model=CONFIG['model'], temperature=CONFIG['temperature'])
system_prompt = """You are a data preprocessing expert. Generate Python code to perform the requested preprocessing step.

Guidelines:
1. Use pandas and scikit-learn when possible
2. Never modify the DataFrame index
3. Handle missing values appropriately
4. Preserve original data dimensions unless explicitly requested
5. Add comments explaining key steps

Return only the necessary imports and code. The code should modify the 'df' DataFrame in-place."""

async def generator_node(state):
    """Generate preprocessing code using LLM"""
    print("---GENERATING PREPROCESSING CODE---")
    
    structured_llm = llm.with_structured_output(PreprocessingCode)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Preprocessing task: {task_description}\n\nCurrent data schema:\n{data_schema}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        df = await get_dataset(state['project_id'])
        data_schema = {
            "columns": df.columns.tolist(),
            "dtypes": dict(df.dtypes),
            "sample_data": df.head().to_dict()
        }
        
        code_solution = await chain.ainvoke({
            "task_description": state['current_step'],
            "data_schema": data_schema
        })
        
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