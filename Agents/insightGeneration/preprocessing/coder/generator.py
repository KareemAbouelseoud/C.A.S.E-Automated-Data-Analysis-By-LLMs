import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from google.api_core import client_options
import sys
import os
import json

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


system_prompt = hub.pull("preprocessing-coder-generator").messages[0].prompt.template

class CODE(BaseModel):
    """Schema for code solutions."""
    description: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")

async def generator_node(state):
    """
    Generate code solutions for a preprocessing task, expecting df as a JSON string.

    Args:
        state (dict): The current graph state containing:
            - preprocessing_tasks: The task to perform
            - target_column: The column to process
            - strategy: The strategy to use
            - dataframe: JSON string of the input DataFrame
            - messages: List of messages in the conversation

    Returns:
        state (dict): Updated state with generated code solutions
    """
    print("---GENERATING CODE SOLUTIONS---")

    task = state["preprocessing_tasks"]
    column = state["target_column"]
    strategy = state["strategy"]
    df_json_str = state["dataframe"]

    #check
    try:
        #if DataFrame, convert to JSON string
        if hasattr(df_json_str, "to_json") and callable(df_json_str.to_json):
            df_json_str = df_json_str.to_json()
        #check if string
        if not isinstance(df_json_str, str):
            raise TypeError(f"Expected JSON string for dataframe, got {type(df_json_str)}")

        #parse JSON string to DataFrame
        df = pd.read_json(df_json_str)
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Parsed data is not a DataFrame")
        
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


    try:
        code_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"""
            Preprocessing Task: {task}
            Target Column: {column}
            Strategy: {strategy}
            Assume `df` is a JSON string containing a DataFrame (not a pandas object).
            Convert it to a pandas DataFrame using `pd.read_json(df)`.
            Do not redefine or overwrite `df`, just transform it in-place if needed and return as JSON.
            """)
        ])

        code_chain_raw = code_gen_prompt | structured_llm
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
