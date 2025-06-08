from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
import pandas as pd
from google.api_core import client_options

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
load_dotenv()



CONFIGURATIONS = {
    'temperature': 0.5,
    'model': "gemini-2.0-flash",
    'number of retries': 3
}

client_options = client_options.ClientOptions(
    api_endpoint="generativelanguage.googleapis.com",
    quota_project_id=os.getenv("GOOGLE_PROJECT_ID")
)


llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

# Custom system prompt for preprocessing tasks
system_prompt = hub.pull("preprocessing-coder-generator").messages[0].prompt.template

class CODE(BaseModel):
    """Schema for code solutions."""
    description: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements") 
    code: str = Field(description="Code block not including import statements")

async def generator_node(state):
    """
    Generate code solutions for a preprocessing task

    Args:
        state (dict): The current graph state containing:
            - preprocessing_tasks: The task to perform
            - target_column: The column to process
            - strategy: The strategy to use
            - dataframe: The input DataFrame
            - messages: List of messages in the conversation

    Returns:
        state (dict): Updated state with generated code solutions
    """
    print("---GENERATING CODE SOLUTIONS---")
    
    # Get task details
    task = state["preprocessing_tasks"]
    column = state["target_column"]
    strategy = state["strategy"]
    
    # Get the current dataframe from state
    try:
        df = state['dataframe']
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Invalid DataFrame in state")
        
        # Model with structured output
        structured_llm = llm.with_structured_output(CODE, include_raw=True)
    except Exception as e:
        error_msg = f"Data initialization failed: {str(e)}"
        print(f"!!! CRITICAL ERROR: {error_msg}")
        return {
            "generation": [],
            "messages": [("system", error_msg)],
            "error": "yes",
            "iterations": state.get("iterations", 0) + 1,
            "preprocessed_dataframe": None,
            "preprocessing_tasks": task,
            "target_column": column,
            "strategy": strategy
        }

    # Generate code for the task
    try:
        # Prompt template with task and column information
        code_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"""
            Preprocessing Task: {task}
            Target Column: {column}
            Strategy: {strategy}
            Assume there is a pandas DataFrame named df already available in memory.
            Do not redefine or recreate it.
            """)
        ])

        code_chain_raw = (code_gen_prompt | structured_llm)
        fallback_chain = insert_errors | code_chain_raw
        code_gen_chain_retry = code_chain_raw.with_fallbacks(
            fallbacks=[fallback_chain] * CONFIGURATIONS["number of retries"],
            exception_key="error"
        )
        code_gen_chain = code_gen_chain_retry | parse_output

        code_solution = await code_gen_chain.ainvoke({"messages": state["messages"]})
        generated_solutions = [{
            "task": task,
            "column": column,
            "strategy": strategy,
            "solution": code_solution
        }]

        return {
            "generation": generated_solutions,
            "messages": state["messages"],
            "iterations": state.get("iterations", 0) + 1,
            "preprocessing_tasks": task,
            "target_column": column,
            "strategy": strategy,
        }

    except Exception as e:
        print(f"Error generating code: {str(e)}")
        return {
            "generation": [],
            "messages": state["messages"] + [("system", f"Error generating code: {str(e)}")],
            "error": "yes",
            "iterations": state.get("iterations", 0) + 1,
            "preprocessing_tasks": task,
            "target_column": column,
            "strategy": strategy,
        }

async def parse_output(solution):
    """Parse structured output that includes raw response"""
    return solution["parsed"]

async def insert_errors(inputs):
    """Insert errors for tool parsing in the messages"""
    error = inputs["error"]
    messages = inputs["messages"]
    messages += [
        (
            "assistant",
            f"Retry. You are required to fix the parsing errors: {error}"
        )
    ]
    return {"messages": messages}