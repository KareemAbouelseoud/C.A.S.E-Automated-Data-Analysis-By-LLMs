
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("reflector").messages[0].prompt.template

async def reflector_node(state):
    """
    Reflect on errors

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation
    """

    print("---GENERATING CODE SOLUTION---")

    # State
    messages = state["messages"]
    iterations = state["iterations"]
    code_solution = state["generation"]

    # Prompt to enforce tool use
    reflector_prompt_gemini = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt,),
        ("placeholder", "{messages}"),
    ]
)
    reflector_chain = (reflector_prompt_gemini | llm)
    # Add reflection
    reflections = await reflector_chain.ainvoke(
        {"messages": messages}
    )
    return {"generation": code_solution, "messages": [("assistant", f"Here are reflections on the error: {reflections}")], "iterations": iterations}