## Inside QUGEN Core 

from typing import Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def filter_unique_cards(valid_cards, state, threshold=0.6):

    existing_questions = {c["question"].lower() for c in state.get("insight_cards", [])}
    unique_cards = []
    for c in valid_cards:
     current_question = c["question"].lower()
     for existing_q in existing_questions:
                similarity = cosine_similarity(
                    semantic_model.encode(current_question).reshape(1, -1),
                    semantic_model.encode(existing_q).reshape(1, -1)
                )[0][0]
                print(f"Comparing:\n - New: {current_question}\n - Existing: {existing_q}\n - Similarity: {similarity:.4f}")
    return unique_cards 

def validate_insight_card(card: Dict[str, str], schema) -> bool:
    """Validate insight card structure and schema compliance"""
    try:
        breakdown_col = card['breakdown'].split('(')[-1].split(')')[0].strip()
        measure_col = card['measure'].split('(')[-1].split(')')[0].strip()
        return all([
            breakdown_col in schema,
            measure_col in schema,
            'reason' in card,
            'question' in card
        ])
    except Exception:
        return False
async def filterationA_node(state) -> str:
    
    """
    Filteration A: Filter out invalid or duplicate insight cards.
    """
    if "insight_cards" not in state:
        raise ValueError("No insight cards provided in state.")
    
    # # Extracting the DataFrame from the state
    # df = pd.read_json(StringIO(state['df']))
    
    # # Extracting the schema from the DataFrame
    # schema = df.columns.tolist()
    
    # # Extracting the insight cards from the state
    # insight_cards = state["insight_cards"]
    
    # # Filtering valid cards
    # valid_cards = []
    # for card in insight_cards:
    #     if validate_insight_card(card, schema):
    #         valid_cards.append(card)
    
    # # Filtering unique cards
    # unique_cards = filter_unique_cards(valid_cards, state)
    
    # # Updating the state with filtered cards
    # state["insight_cards"] = unique_cards
##TODO: Filteration B Is RANKING AND INSIGHT CARDS are scored 