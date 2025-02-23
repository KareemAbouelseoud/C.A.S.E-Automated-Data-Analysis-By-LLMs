import pandas as pd
from typing import Dict
import google.generativeai as genai
from langgraph.types import interrupt


class AgentGraphState(Dict):
    pass
def data_description_generator_node(state: AgentGraphState, model, user_feedback=None, temperature=0) -> AgentGraphState:
    """
    Generates a dataset description, schema, and basic statistics.
    If user feedback is provided, it refines the description accordingly.
    """
    if "df" not in state:
        raise ValueError("No dataset provided in state.")

    df = state["df"]
    schema = df.columns.tolist()
    numerical_stats = df.describe(include=["number"]).reset_index()
    categorical_stats = df.describe(include=["object", "category"]).reset_index()

    basic_stats = {"numerical": numerical_stats, "categorical": categorical_stats}
    prompt = f"""
    Given the dataset:
    {df.head().to_markdown()}

    Provide the following:
    1. A detailed explanation of each column in bullet points.
    2. An overview description of the dataset.
    3. Key patterns in the data distribution
    ~~4. Notable data quality issues

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



