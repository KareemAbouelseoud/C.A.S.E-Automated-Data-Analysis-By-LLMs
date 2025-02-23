import pandas as pd
from typing import Dict
import google.generativeai as genai
from langgraph.types import interrupt
class AgentGraphState(Dict):

    pass
def data_description_generator_node(state: AgentGraphState, model, user_feedback=None, temperature=0):
    """
    Generates a dataset description, schema, and basic statistics.
    If user feedback is provided, it refines the description accordingly.
    """
    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    schema = df.columns.tolist()
    basic_stats = df.describe(include='all').reset_index()

    prompt = f"""
    Given the dataset:
    {df.head()}

    Provide the following:
    1. A detailed explanation of each column in bullet points.
    2. An overview description of the dataset.

    {f'Consider the following user feedback for improvement: {user_feedback}' if user_feedback else ''}
    """

    response = model.generate_content(prompt)

    state["description"] = response.text
    state["schema"] = schema
    state["basic_stats"] = basic_stats

    return state


def human_input(state: AgentGraphState) -> AgentGraphState:
    human_message = input("human_input")
    state["human_feedback"] = human_message
    return state



