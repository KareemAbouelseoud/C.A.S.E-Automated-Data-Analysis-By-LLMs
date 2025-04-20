from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from API.Requests import projectRequests
load_dotenv()

CONFIGURATIONS = {
    'temperature': 0.0,
    'model': "gemini-2.0-flash",
    'number of retries': 3
}

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
    Generate a code solution for preprocessing the dataframe

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """
    print("---GENERATING CODE SOLUTION---")
    
    # Get the current dataframe from state
    if state['preprocessed_dataframe'] is None:
        # If no preprocessed dataframe exists yet, get the original dataset
        state['preprocessed_dataframe'] = await projectRequests.get_dataset(state['project_id'])
    
    # Model with structured output
    structured_llm = llm.with_structured_output(CODE, include_raw=True)
    
    # Prompt template with task and column information
    code_gen_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"""
        Preprocessing Task: {state['preprocessing_task']}
        Target Column: {state['target_column']}
        Assume there is a pandas DataFrame named `df` already available in memory.
        Do not redefine or recreate it.
        """)

    ])

    code_chain_raw = (code_gen_prompt | structured_llm)

    # Fallback chain for retries
    fallback_chain = insert_errors | code_chain_raw
    code_gen_chain_retry = code_chain_raw.with_fallbacks(
        fallbacks=[fallback_chain] * CONFIGURATIONS["number of retries"],
        exception_key="error"
    )
    code_gen_chain = code_gen_chain_retry | parse_output

    messages = []
    iterations = state.get("iterations", 0)
    error = state.get("error", "")

    if error == "yes":
        messages += [
            (
                "human",
                "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:"
            )
        ]
        code_solution = await code_gen_chain.ainvoke({"messages": state['messages'] + messages})
    else:
        code_solution = await code_gen_chain.ainvoke({"messages": state["messages"]})

    messages += [
        (
            "assistant",
            f"{code_solution.prefix}\nImports: {code_solution.imports}\nCode: {code_solution.code}"
        )
    ]

    iterations += 1
    return {"generation": code_solution, "messages": messages, "iterations": iterations}

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