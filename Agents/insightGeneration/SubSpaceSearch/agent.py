import re
import json
import pandas as pd
import logging
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from models import InsightCards, InsightCard
from Filteration.pandas_codeGenerator import parse_agent_response, generate_pandas_agent_prompt

CONFIGURATIONS={
    'temperature':0.5,
    'model':"gemini-2.0-flash",
    'number of retries':3,
    "beam_width":100,
    "exp_factor":100,
    "max_depth":1,
    "w_llm":0.5,
}
system_prompt = hub.pull("subspace-system-prompt").messages[0].prompt.template
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

def run_advanced_insight_agent(df:pd.DataFrame,desc:str,card:InsightCard,subspace):
    """Runs the advanced insight agent"""
    try:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": generate_Advanced_insight_cards(original_insight_card=card,df=df, data_description=desc,subspace=subspace)
            }
        ]
        response = llm.invoke(messages)
        insight_cards_containter = parse_advanced_insights_response(df,response,OriginalCard=card)
        return insight_cards_containter
    except Exception as e:
        print(f"Error in qugen_node: {str(e)}")
        raise

def run_pandas_Coder_agent_ad_card(filtered_df:pd.DataFrame,card:InsightCard) -> InsightCard:
    """Generates a Pandas DataFrame agent based on the provided Insight Card."""
    global_dict={"df":filtered_df}
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    agent_executor = create_pandas_dataframe_agent(
        llm,
        filtered_df,
        agent_type="tool-calling",
        verbose=False,
        allow_dangerous_code=True,
    )
    response = agent_executor.invoke(generate_pandas_agent_prompt(card))
    try:
        exec(parse_agent_response(response['output']),global_dict)
        card.resulted_df = str(global_dict['resulted_df'].to_json()) if global_dict['resulted_df'] is not None or global_dict["resulted_df"].empty else ""
    except Exception as e:
        # logger.error(f"Error in executing the agent response: {e}")
        card.resulted_df = pd.DataFrame()
    return card
def parse_advanced_insights_response(df:pd.DataFrame,response,OriginalCard:InsightCard):
    """
    Parses the response from the advanced insight agent and validates the generated insight cards.
    """
    
    text = response.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)
    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        data =json.loads(matches[0].strip())
        parsed_InsightCards=InsightCards(**data)  
        # Validate each card
        valid_cards = InsightCards(insight_cards=[])

        for i,card in enumerate(parsed_InsightCards.insight_cards):
            if not validate_card(df, card,OriginalCard):
                # Validating the card if the columns exist in the DataFrame and if the used columns are not empty
                # and if they are greater than the original card's used columns
                print(f"Invalid card: {card}")
                continue
            for other_cards in parsed_InsightCards.insight_cards[i+1:]:
                if card.used_columns == other_cards.used_columns:
                    # Check if the used columns are the same in any other card
                    print(f"Duplicate card found: {card}")
                    continue
            # If the card is valid, append it to the valid cards list
            valid_cards.insight_cards.append(card)
        return valid_cards
    except Exception:
        raise ValueError(f"Failed to parse Insight cards: {text}")

def generate_Advanced_insight_cards(original_insight_card: InsightCard, df:pd.DataFrame, data_description: str,subspace) -> str:
  
    """
    Generates a list of potential "Insight Cards" based on the original insight card and available columns.
    """
    original_insight_card.used_columns = original_insight_card.used_columns if original_insight_card.used_columns!=[] else []
    if original_insight_card.used_columns == []:
        original_insight_card.used_columns.append(original_insight_card.breakdown)
        original_insight_card.used_columns.append(original_insight_card.measure)

    
    original_insight_card.used_columns = list(set(original_insight_card.used_columns))
    avb_cols = set(df.columns.values.tolist()) - set(original_insight_card.used_columns) - set(subspace["used_cols"]) 
  # Define the prompt for the LLM
    prompt = f"""
  You are a highly skilled data exploration expert assisting in a subspace search algorithm. Your task is to generate a list of potential "Insight Cards" that could reveal interesting patterns in the given dataset. Each Insight Card suggests a direction for further exploration by refining the subspace.

  Here's the context:

  *   **Original Insight Card:**
      *   Insight Type: {original_insight_card.insight_type}
      *   Question: {original_insight_card.question}
      *   Breakdown: {original_insight_card.breakdown}
      *   Measure: {original_insight_card.measure}
      *   Aggregation: {original_insight_card.aggregation}
      *   Reason: {original_insight_card.reason}
      *   Used Columns: {original_insight_card.used_columns}

  *   Available Columns (not yet used as filters): {avb_cols}
  *   Data description: {data_description}


  Your output MUST be a valid JSON structure conforming to the following schema. Generate as many Insight Cards as you think are promising refinements of the "Original Insight Card", based on the available information, but make sure the format is followed. Focus on suggesting different "SubSpace" values to filter the data and potentially reveal deeper insights related to the original question and insight type.

  ```json
  {{
    "insight_cards": [
      {{
        "insight_type": "Trend | Outstanding Value | Distribution Difference | Attribution",
        "reason": "Concise rationale for the selected column (SubSpace) and why it's likely to reveal a *refined* insight, building upon the Original Insight Card and related to the chosen Insight Type.",
        "question": "A clear, natural language question that this *refined* Insight Card aims to answer.  This should often be similar to the Original Insight Card's question, but potentially more focused due to the subspace.",
        "breakdown": "{original_insight_card.breakdown}", // Inherit Breakdown from Original Card
        "measure": "{original_insight_card.measure}",   // Inherit Measure from Original Card
        "aggregation": "{original_insight_card.aggregation}", // Inherit Aggregation from Original Card
        "SubSpace": "The column name from Available columns where we use as a filter to best reveal patterns in the given dataset based on the provided information. This should be *different* from columns already used in the Original Insight Card's Breakdown or Measure if possible, to explore new dimensions."
        "used_columns": This should contain the list of columns used in the Original Insight Card and the new SubSpace column.,

      }}
      // Add more refined Insight Cards here, as many as you deem promising.
    ]
  }}
  ```
  Here are some important guidelines:

  Refinement Focus: The generated Insight Cards should be refinements of the "Original Insight Card". Think of them as exploring the original question in more detail by adding a subspace filter.

  Insight Types: Maintain or adjust the "Insight Type" if appropriate for the refined Insight Card. Justify your choice in the "reason" field, explaining how the SubSpace helps to explore that insight type further. Crucially, if the Original Insight Card's "insight_type" is "Distribution Difference", then all generated refined Insight Cards MUST also have "insight_type": "Distribution Difference". Distribution Difference insights require comparison across different subspaces, so refinements must maintain this focus. and here are the available insight types: "Trend", "Outstanding Value", "Distribution Difference", "Attribution".

  Inheritance: The "breakdown", "measure", and "aggregation" should generally be inherited from the "Original Insight Card" to maintain focus. The key variation is the "SubSpace".

  SubSpace Selection: The "SubSpace" column must be chosen from the "Available Columns" list. Prioritize choosing a "SubSpace" column that is different from the "Breakdown" and "Measure" columns of the "Original Insight Card" to explore new dimensions.

  Conciseness: Keep the "reason" field brief and to the point, focusing on the refinement provided by the SubSpace and how it enhances the chosen Insight Type.

  Validity: Ensure the generated JSON is valid and well-formed. The entire response MUST be valid JSON.

  Here's an example for illustrative purposes (but your output should contain multiple refined Insight Cards):


  Now, generate the JSON output containing a list of potential refined Insight Cards, building upon the provided "Original Insight Card".
  """
    return prompt

def validate_card(df:pd.DataFrame, card:InsightCard,OriginalCard:InsightCard)-> bool:
    """
    Validates the generated Insight Card by checking if the columns exist in the DataFrame.
    It also checks if the used columns are not empty and if they are greater than the original card's used columns.
    """
    # Check if the columns exist in the DataFrame
    valid_card = True
    if card.breakdown not in df.columns:
        print(f"Warning: Dropping card - Breakdown column '{card.breakdown}' does not exist in the DataFrame.")
        valid_card = False
    if card.measure not in df.columns:
        print(f"Warning: Dropping card - Measure column '{card.measure}' does not exist in the DataFrame.")
        valid_card = False
    if card.subSpace not in df.columns:
        print(f"Warning: Dropping card - subspace column '{card.subSpace}' does not exist in the DataFrame.")
        valid_card = False
    if card.used_columns.__len__() == 0:
        print(f"Warning: Dropping card - No used columns in the Insight Card.")
        valid_card = False
    if  len(set(card.used_columns)) - len(set(OriginalCard.used_columns)) == 0  :
        print(f"Warning: Dropping card - Used columns in the Insight Card Must be greater than its parent.")
        valid_card = False
    return valid_card