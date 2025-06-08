from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
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

    messages = state["messages"]
    iterations = state["iterations"]
    generated_errors = state.get("generated_errors", [])
    preprocessing_tasks = state["preprocessing_tasks"]

    if not generated_errors:
        return {
            "generation": state.get("generation", []),
            "messages": messages + [("assistant", "No errors to reflect on")],
            "iterations": iterations,
            "preprocessing_tasks": preprocessing_tasks,
            "generated_errors": []
        }

    for idx, error_case in enumerate(generated_errors):
        current_task = error_case.get("task", {})
        error_msg = error_case.get("error", "No error message provided.")

        # Safely handle task info whether dict or str
        if isinstance(current_task, dict):
            task_name = current_task.get('task', 'Unknown Task')
            column_name = current_task.get('column', 'Unknown Column')
            strategy = current_task.get('strategy', 'No Strategy Provided')
        else:
            task_name = str(current_task)
            column_name = 'Unknown Column'
            strategy = 'No Strategy Provided'

        human_content = f"""
Current Task: {task_name}
Target Column: {column_name}
Strategy: {strategy}
Error Message: {error_msg}
Please analyze the error and suggest improvements.
"""

        reflector_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_content)
        ])

        reflector_chain = (reflector_prompt | llm)
        reflections = await reflector_chain.ainvoke({"messages": messages})

        messages.append(("assistant", f"Reflections for task {idx}: {reflections}"))

    return {
        "generation": state.get("generation", []),
        "messages": messages,
        "iterations": iterations,
        "current_task_index": state.get("current_task_index", 0),
        "preprocessing_tasks": preprocessing_tasks,
        "generated_errors": []  # clear errors after reflection
    }
