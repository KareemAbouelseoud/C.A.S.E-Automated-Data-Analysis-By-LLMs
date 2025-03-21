from typing import Dict
import os
from dotenv import load_dotenv
load_dotenv()
from .prompts import generate_qugen_prompt,InsightCards
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain import hub
import re
import json
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
from langchain_google_genai import ChatGoogleGenerativeAI



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
        parsed_insight_cards = parse_qugen_response(response)

        if state.get("insight_cards") is None:
            state["insight_cards"] = []
        # Append the new insight cards to the existing list
        state["insight_cards"].extend(parsed_insight_cards.insight_cards)
        return {"insight_cards": state["insight_cards"], "num_cards": int(os.getenv("Insight_cards_number"))}

    except Exception as e:
        print(f"Error in qugen_node: {str(e)}")
        raise

def parse_qugen_response(response):
    
    text = response.content
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```json(.*?)```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)
    # Return the list of matched JSON strings, stripping any leading or trailing whitespace
    try:
        data =json.loads(matches[0].strip())
        return InsightCards(**data)  
    except Exception:
        raise ValueError(f"Failed to parse Insight cards: {text}")
    
async def should_continue(state) -> str:
    """Determine workflow continuation based on state validation"""
    print("Checking if we should continue to the next node...")
    cards=state["insight_cards"]
    if "insight_cards" in state:
        cards_count = len(cards)
        if cards_count<state['num_cards']:
            print(f"Generated {cards_count} cards, expected {state['num_cards']}")
            return "qugen_node"
        else:
            print(f"Generated {cards_count} cards, expected {state['num_cards']}")
            return "filteration_node"
    else:
        print("No recommendations found, returning to selector node")
        return "qugen_node"
