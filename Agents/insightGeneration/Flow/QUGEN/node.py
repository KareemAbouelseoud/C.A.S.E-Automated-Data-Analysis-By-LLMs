from typing import Dict
from .core import parse_insight_cards, validate_insight_card,semantic_filter,pandas_query_filter 
from .prompts import generate_qugen_prompt
from genai_config import model
import pandas as pd

def qugen_node(state: Dict) -> Dict:
    """Generate questions based on current data description"""
    prompt = generate_qugen_prompt(state)
    
    response = model.generate_content(prompt)
    new_cards = parse_insight_cards(response.text)
    file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
    dataset = pd.read_csv(file_path)
    schema = dataset.columns.tolist()
    # Filter valid cards that match schema
    valid_cards = [
        card for card in new_cards
        if validate_insight_card(card, state)
    ]
    
    # Deduplicate by checking semantic similarity between questions
    existing_questions = {c["question"].lower() for c in state.get("insight_cards", [])}
    unique_cards = [
    c for c in valid_cards 
    if not any(semantic_filter(c["question"].lower(), existing_q) for existing_q in existing_questions)
]
    #filter out rudimentary questions 
    query_filtered_cards = [
    c for c in unique_cards 
    if pandas_query_filter(c, state["df"])  
]
    

    
    # Update state
    state.setdefault("insight_cards", []).extend(query_filtered_cards)
    
    return state