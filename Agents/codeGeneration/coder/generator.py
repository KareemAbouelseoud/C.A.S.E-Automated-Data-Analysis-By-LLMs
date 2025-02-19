from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from Database import mainDatabase



load_dotenv()
CONFIGURATIONS={
    'temperature':0.0,
    'model':"gemini-2.0-flash",
    'number of retries':3
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("viz-generation-coder-generator").messages[0].prompt.template
class CODE(BaseModel):
    """Schema for code solutions."""

    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")

    
async def generator_node(state):
    """
    Generate a code solution

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """
    

    print("---GENERATING CODE SOLUTION---")
    # Model
    structured_llm_gemini = llm.with_structured_output(CODE, include_raw=True)
    # Prompt to enforce tool use
    code_gen_prompt_gemini = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt,),
        ("placeholder", "{messages}"),
    ]
)
    code_chain_gemini_raw = (code_gen_prompt_gemini | structured_llm_gemini)

    # This will be run as a fallback chain
    fallback_chain = insert_errors | code_chain_gemini_raw
    code_gen_chain_re_try = code_chain_gemini_raw.with_fallbacks(
        fallbacks=[fallback_chain] * CONFIGURATIONS["number of retries"], exception_key="error"
    )
    code_gen_chain = code_gen_chain_re_try | parse_output  


    messages = []
    if 'iterations' in state:
        iterations = state["iterations"]
    else:
        iterations = 0 

    if 'error' in state:
        error = state["error"]
    else:
        error=''

    # We have been routed back to generation with an error
    if error == "yes":
        messages += [
            (
                "human",
                "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:",
            )
        ]
            # Solution
        code_solution = await code_gen_chain.ainvoke(
            {"messages": state['messages']+messages}
        )
    else:
        old_messages = state["messages"]
        data_report= mainDatabase.fetch_data_report(state['project_id'])
        old_messages[-1]['content']=old_messages[-1]['content']+f"Here is the data report crucial for the plot: \n {data_report}\n"
        # Solution
        code_solution = await code_gen_chain.ainvoke(
            {"messages":old_messages}
        )
    messages += [
        (
            "assistant",
            f"{code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
        )
    ]

    # Increment
    iterations = iterations + 1
    return {"generation": code_solution, "messages": messages, "iterations": iterations}




async def parse_output(solution):
    """When we add 'include_raw=True' to structured output,
    it will return a dict w 'raw', 'parsed', 'parsing_error'."""

    return solution["parsed"]    

async def insert_errors(inputs):
    """Insert errors for tool parsing in the messages"""

    # Get errors
    error = inputs["error"]
    messages = inputs["messages"]
    messages += [
        (
            "assistant",
            f"Retry. You are required to fix the parsing errors: {error}",
        )
    ]
    return {
        "messages": messages,
    }










    
