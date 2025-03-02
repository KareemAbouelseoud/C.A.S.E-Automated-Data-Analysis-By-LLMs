from typing import Dict
from .core import parse_insight_cards, validate_insight_card
from .prompts import generate_qugen_prompt
from genai_config import model

def qugen_node(state: Dict) -> Dict:
    """Generate questions based on current data description"""
    prompt = generate_qugen_prompt(state)
    
    response = model.generate_content(prompt)
    new_cards = parse_insight_cards(response.text)
    
    # Filter valid cards
    valid_cards = [
        card for card in new_cards
        if validate_insight_card(card, state["schema"])
    ]
    
    # Deduplicate
    existing_questions = {c["question"].lower() for c in state.get("insight_cards", [])}
    unique_cards = [c for c in valid_cards if c["question"].lower() not in existing_questions]
    
    # Update state
    state.setdefault("insight_cards", []).extend(unique_cards)
    
    return state