
from io import StringIO
from .config import *
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")




async def qugen_node(state: Dict) -> Dict:
    """Generate questions based on current data description"""
    print("Generating questions using QUGEN...")
    print(f"Current state:\n{state.keys()}\n")

    system_prompt = hub.pull("qugen-system-prompt").messages[0].content
    CONFIGURATIONS={
        'temperature':1.0,
        'model':"gemini-2.0-flash",
        'number of retries':3
    }

    llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
    try:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": generate_qugen_prompt(state)
            }
        ]

        response = llm.invoke(messages)
        # Parse the response to extract the JSON data
        df = pd.read_json(StringIO(state['df']))
        parsed_insight_cards = parse_qugen_response(df,response)

        if state.get("insight_cards") is None:
            state["insight_cards"] = []
        # Append the new insight cards to the existing list
        state["insight_cards"].extend(parsed_insight_cards.insight_cards)
        return {"insight_cards": state["insight_cards"], "num_cards": str(os.getenv("Insight_cards_number"))}

    except Exception as e:
        print(f"Error in qugen_node: {str(e)}")
        raise

def parse_qugen_response(df:pd.DataFrame,response):
    
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
        for card in parsed_InsightCards.insight_cards:
            if not validate_card(df, card):
                print(f"Invalid card: {card}")
                continue
            else:
                card.used_columns.append(card.breakdown)
                card.used_columns.append(card.measure)
                valid_cards.insight_cards.append(card)
        return parsed_InsightCards
    except Exception:
        raise ValueError(f"Failed to parse Insight cards: {text}")
    


def validate_card(df:pd.DataFrame, card:InsightCard)-> bool:
    """
    Validates the generated Insight Card by checking if the columns exist in the DataFrame.
    """
    # Check if the columns exist in the DataFrame
    valid_card = True
    if card.breakdown not in df.columns:
        print(f"Warning: Dropping card - Breakdown column '{card.breakdown}' does not exist in the DataFrame.")
        valid_card = False
    if card.measure not in df.columns:
        print(f"Warning: Dropping card - Measure column '{card.measure}' does not exist in the DataFrame.")
        valid_card = False
    return valid_card
    
async def should_continue(state) -> str:
    """Determine workflow continuation based on state validation"""
    print("Checking if we should continue to the next node...")
    if "insight_cards" in state:
        cards=state["insight_cards"]
        cards_count = len(cards)
        if cards_count<int(state['num_cards']):
            print(f"Generated {cards_count} cards, expected {int(state['num_cards'])}")
            return "qugen_node"
        else:
            print(f"Generated {cards_count} cards, expected {int(state['num_cards'])}")
            return "filteration_node_A"
    else:
        print("No recommendations found, returning to selector node")
        return "qugen_node"
    

def validate_card(df:pd.DataFrame, card:InsightCard)-> bool:
    """
    Validates the generated Insight Card by checking if the columns exist in the DataFrame.
    """
    # Check if the columns exist in the DataFrame
    valid_card = True
    if card.breakdown not in df.columns:
        print(f"Warning: Dropping card - Breakdown column '{card.breakdown}' does not exist in the DataFrame.")
        valid_card = False
    if card.measure not in df.columns:
        print(f"Warning: Dropping card - Measure column '{card.measure}' does not exist in the DataFrame.")
        valid_card = False
    return valid_card