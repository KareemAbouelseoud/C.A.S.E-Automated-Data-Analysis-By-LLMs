from typing import Dict
from .prompts import generate_qugen_prompt,QUGEN
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain import hub
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
from langchain_google_genai import ChatGoogleGenerativeAI

system_prompt = hub.pull("qugen-system-prompt").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.0,
    'model':"gemini-2.0-flash",
    'number of retries':3
}
llm=ChatGoogleGenerativeAI(model=CONFIGURATIONS['model'], temperature=CONFIGURATIONS['temperature'])
def qugen_node(state: Dict) -> Dict:
    """Generate questions based on current data description"""
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        ]
    prompt = generate_qugen_prompt(state)
  
    structured_llm = llm.with_structured_output(QUGEN).ainvoke(messages)

    return structured_llm

async def should_continue(state) -> str:
    """Determine workflow continuation based on state validation"""
    if "insight_cards" in state:
        cards_count = len(state["insight_cards"])
        if cards_count<state["num_cards"]:
            print(f"Generated {cards_count} cards, expected {state['num_cards']}")
            return "qugen_node"
        else:
            print(f"Generated {cards_count} cards, expected {state['num_cards']}")
            return "filteration_node"
    else:
        print("No recommendations found, returning to selector node")
        return "selector_node"
    