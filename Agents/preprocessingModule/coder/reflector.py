from langchain_google_genai import ChatGoogleGenerativeAI
from API.Requests.projectRequests import get_dataset
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

#TODO : Refine Propmt and state variables
reflector_llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro", temperature=0.5)
reflector_prompt = """Analyze this preprocessing code error and provide specific feedback:

Task: {task}
Code: {code}
Error: {error}

Provide:
1. Clear explanation of the error
2. Suggested fix
3. Common pitfalls to avoid"""

async def reflector_node(state):
    """Analyze errors and provide improvement feedback"""
    print("---ANALYZING PREPROCESSING ERROR---")
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", reflector_prompt),
        ("human", "Additional context: {data_schema}")
    ])
    
    chain = prompt_template | reflector_llm
    
    df = await get_dataset(state['project_id'])
    data_schema = {
        "columns": df.columns.tolist(),
        "dtypes": dict(df.dtypes)
    }
    
    reflection = await chain.ainvoke({
        "task": state['current_step'],
        "code": state['generation'].code,
        "error": state['error'],
        "data_schema": data_schema
    })
    
    return {
        **state,
        "messages": state["messages"] + [
            ("assistant", f"Error analysis: {reflection.content}")
        ],
        "feedback": reflection.content
    }