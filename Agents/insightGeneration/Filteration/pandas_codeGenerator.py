
from langchain_google_genai import ChatGoogleGenerativeAI
from Agents.insightGeneration.QUGEN.prompts import InsightCard
from langchain_experimental.agents import create_pandas_dataframe_agent
import re

def parse_agent_response(response):
    
    text = response
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```python(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)
    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        data =matches[0].strip()
        return data
    except Exception:
        raise ValueError(f"Failed to parse Insight cards: {text}")

def generate_pandas_agent_prompt(card: InsightCard) -> str:
    """Generates a prompt for the Pandas DataFrame agent."""
    prompt = f"""
    You are a powerful Pandas DataFrame agent designed to answer data analysis questions. Your goal is to analyze a Pandas DataFrame and provide precise, structured outputs that can be easily used for further calculations and analysis.

    You have been given the following Insight Card information:

    Question: {card.question}
    Reason: {card.reason}
    Breakdown: {card.breakdown}
    Measure: {card.measure}
    Aggregation: {card.aggregation}

    Based on this information, your task is to output a Pandas DataFrame that meets the following criteria:

    1. **Group the DataFrame:** Group the input DataFrame by the '{card.breakdown}' column (the Breakdown dimension).
    2. **Calculate the Measure:** Calculate the '{card.aggregation}' of the '{card.measure}' column (the Measure) for each group. You must analyze what is the best function to use from Pandas
    3. **Output as DataFrame:** Present the results *as a Pandas DataFrame* with two columns: '{card.breakdown}' and '{card.aggregation.lower()}_{card.measure}'. The '{card.breakdown}' column should contain the unique values from the '{card.breakdown}' column, and the '{card.aggregation.lower()}_{card.measure}' column should contain the corresponding aggregated values. *It is critically important that you return a proper, valid Pandas DataFrame. Don't just state what you'd do; actually execute the code and return the DataFrame.*

    Specifically, generate *ONLY* the Python code to perform these steps. Enclose the code in the function called `GetCardDataframe`. Stick to the following sample code structure:

    ```python
    import pandas as pd

    def GetCardDataframe(df: pd.DataFrame) -> pd.DataFrame:
        \"\"\"
        Analyzes the {card.measure} for the {card.breakdown}.

        Args:
            df: The input Pandas DataFrame.

        Returns:
            A Pandas DataFrame with '{card.breakdown}' and '{card.aggregation.lower()}_{card.measure}' columns.
        \"\"\"
        try:
            # You MUST choose the correct aggregation from the card.aggregation description
            grouped = df.groupby('{card.breakdown}')['{card.measure}'].<insert_appropriate_aggregation_function_here>().reset_index()
            grouped.rename(columns={{grouped.columns[1]: '{card.aggregation.lower()}_{card.measure}'}}, inplace=True)
            return grouped.sort_values(by='{card.aggregation.lower()}_{card.measure}', ascended = True if {card.aggregation}=="MIN" else False )
        except Exception as e:
            print('Error during the grouping and renaming, returning the dataset itself', e)
            return pd.DataFrame(df)

    resulted_df = GetCardDataframe(df)
    print(resulted_df)
    ```
    """
    return prompt

def run_pandas_Coder_agent(state:dict) -> list[InsightCard]:
    """Generates a Pandas DataFrame agent based on the provided Insight Card."""
    global_dict={"df":state["df"]}
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    agent_executor = create_pandas_dataframe_agent(
        llm,
        state["df"],
        agent_type="tool-calling",
        verbose=False,
        allow_dangerous_code=True,
    )
    for card in state["insight_cards"]:
        response = agent_executor.invoke(generate_pandas_agent_prompt(card))
        exec(parse_agent_response(response['output']),global_dict)
        card.resulted_df = global_dict['resulted_df']
    return state["insight_cards"]

