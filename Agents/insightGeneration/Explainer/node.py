from io import StringIO
import threading
from .config import *
system_prompt = hub.pull("insight-explainer-system-prompt").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':1.0,
    'model':"gemini-2.0-flash",
    'number of retries':3
}

async def ExplainerNode(state: dict) -> str:
    """
    This function is responsible for generating advanced insights based on the original insight card.
    It uses the LangChain framework to interact with the LLM and generate new insights.
    """
    insights_explanation_dict={}
    print("Running Subspace Search Node...")
    df = pd.read_json(StringIO(state['df']))
    thread_function(state["insight_cards"], state["description"],state["advanced_insight_cards"],insights_explanation_dict)
    # Extracting the original insight card from the state
    
    return ({"insights_explanation" : insights_explanation_dict})

def thread_function(unique_cards, ds,advanced_cards_dict,insights_explanation_dict):
    threads = []
    for card in unique_cards:
        thread = threading.Thread(target=Explain_InsightCard, args=(card,advanced_cards_dict,ds,insights_explanation_dict))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def Explain_InsightCard(card:InsightCard,advanced_cards_dict:Dict[str, List[Tuple[Dict[str,List],InsightCard]]],ds:DataDescription, insights_explanation:Dict[str, str]):
    """
    Explain the unique insight cards using the ChatGoogleGenerativeAI model.

    Args:
        unique_cards (List[InsightCard]): List of unique insight cards to be explained.
        advanced_cards_dict (Dict[str, List[InsightCard]]): Dictionary mapping unique card IDs to their advanced insight cards.
        ds (DataDescription): Data description object containing metadata about the dataset.
        df (pd.DataFrame): DataFrame containing the dataset.

    Returns:
        None
    """
    # Initialize the language model with the specified configuration
    llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": explainer_prompt(card,advanced_cards_dict[card.id],ds)
        }
    ]

    response = llm.invoke(messages)
    # Extract the explanation from the response
    explanation = response.content
    # Store the explanation in the insights_explanation dictionary using the unique card ID as the key
    insights_explanation[card.id] = explanation

def explainer_prompt(basic_insight_card:InsightCard,advanced_insight_card:Dict[str, List[Tuple[Dict[str,List],InsightCard]]],ds:DataDescription):
    prompt = f"""
    Fisrt Here's the data description for the dataset of the insight card:
    {ds}
    Here is the basic Insight:
    1- Insight Type: {basic_insight_card.insight_type}
    2-Question: {basic_insight_card.question}
    3-Reason: {basic_insight_card.reason}
    4-Breakdown (B) : {basic_insight_card.breakdown} 
    5-Measure (M) : {basic_insight_card.measure}
    6-Aggregation: {basic_insight_card.aggregation}
    7-Subspace S: {basic_insight_card.subSpace}
    8-Score: {basic_insight_card.Score}
    9-Resulted dataframe: {basic_insight_card.resulted_df}
    
    And here are the Advanced Insights for this card:
    """
    for ss,card in advanced_insight_card:
        prompt += f"""
        1- Insight Type: {card.insight_type}
        2-Question: {card.question}
        3-Reason: {card.reason}
        4-Breakdown (B) : {card.breakdown} 
        5-Measure (M) : {card.measure}
        6-Aggregation: {card.aggregation}
        7-Subspace S: {card.subSpace}
        8-Score: {card.Score}
        9-Resulted dataframe: {card.resulted_df}
        ANd here is the subspace used to get this insight card: {ss}
        """
    prompt += f"""
    Now, I want you to explain the basic insight card and the advanced insight cards in a detailed way.
    """ 
    return prompt