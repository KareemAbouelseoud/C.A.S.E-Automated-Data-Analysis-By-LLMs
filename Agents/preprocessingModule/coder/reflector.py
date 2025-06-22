from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

load_dotenv()

CONFIGURATIONS = {
    'temperature': 0.7,
    'model': "gemini-2.0-flash",
}

llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
system_prompt = hub.pull("preprocessing-coder-reflector").messages[0].prompt.template

async def reflector_node(state):
    """
    Reflect on errors in failed code solutions

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updated state with reflections
    """
    print("---REFLECTING ON ERRORS---")

    # State
    messages = state["messages"]
    iterations = state["iterations"]
    generated_errors = state["generated_errors"]
    preprocessing_tasks = state["preprocessing_tasks"]

    if not generated_errors:
        return {
            "generation": state.get("generation", []),
            "messages": messages + [("assistant", "No errors to reflect on")],
            "iterations": iterations,
            "preprocessing_tasks": preprocessing_tasks,
            "generated_errors": []
        }

    # Process each error
    for error_case in generated_errors:
        task_index = error_case["task_index"]
        current_task = error_case["task"]
        error_msg = error_case["error"]

        # Prompt to enforce tool use
        reflector_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"""
            Current Task: {current_task['task']}
            Target Column: {current_task['column']}
            Strategy: {current_task['strategy']}
            Error Message: {error_msg}
            Please analyze the error and suggest improvements.
            """)
        ])

        reflector_chain = (reflector_prompt | llm)
        reflections = await reflector_chain.ainvoke({"messages": messages})
        
        messages.append(("assistant", f"Reflections for task {task_index}: {reflections}"))

    return {
        "generation": state["generation"],
        "messages": messages,
        "iterations": iterations,
        "current_task_index": state["current_task_index"],
        "preprocessing_tasks": preprocessing_tasks,
        "generated_errors": []
    }