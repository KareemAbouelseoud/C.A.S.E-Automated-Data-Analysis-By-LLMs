from typing import Dict


class AgentGraphState(Dict):
    pass


def data_description_generator_node(
    state: AgentGraphState, model, temperature=0
) -> AgentGraphState:
    """
    A node in the graph that generates a description of the dataset, its schema, and basic statistics.

    Args:
        model: The generative AI model (e.g., Gemini).
        temperature: Controls the randomness of the model's output.

    Returns:
        The updated state with the description, schema, and basic statistics.
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
    {df.to_markdown()}

    Provide the following:
    1. A detailed explanation of each column in bullet points.
    2. An overview description of the dataset.
    3. Key patterns in the data distribution
    4. Notable data quality issues

    """

    response = model.generate_content(prompt)

    state["description"] = response.text
    state["schema"] = schema
    state["basic_stats"] = basic_stats

    return state
