from typing import Dict
from .core import parse_insight_cards, validate_insight_card,filter_unique_cards
from .prompts import generate_qugen_prompt,QUGEN
from genai_config import model
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain import hub
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
from genai_config import model,llm

def qugen_node(state: Dict) -> Dict:
    """Generate questions based on current data description"""
    prompt = generate_qugen_prompt(state)
  
    structured_llm = llm.with_structured_output(QUGEN, include_raw=True)
    response = structured_llm.invoke(prompt)

    #new_cards = parse_insight_cards( parsed_cards)
    file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
    dataset = pd.read_csv(file_path)
 
    schema = dataset.columns.tolist()
    
   
    
    # print(response)
    # print(type(response))
    # for card in new_cards:
    #     print(f"ID: {card.id}")
    #     print(f"Reason: {card.reason}")
    #     print(f"Question: {card.question}")
    #     print(f"Breakdown: {card.breakdown}")
    #     print(f"Measure: {card.measure}")
   
    print(response)

    
    # Update state
    # state.setdefault("insight_cards", []).extend(parsed_cards )
    
    return state