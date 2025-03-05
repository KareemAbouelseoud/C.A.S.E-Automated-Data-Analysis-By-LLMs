import re
from typing import List, Dict 
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
semantic_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
import pandas as pd
from io import StringIO

#pasrse 
def parse_insight_cards(response_text: str) -> List[Dict[str, str]]:
    
    cards = []
    
    card_blocks = re.split(r'### Insight Card \d+', response_text)
    
    for idx, block in enumerate(card_blocks[1:], start=1):
        block = block.strip()
        if not block:
            continue
            
        components = {
            
            # """ \s*	Matches any ( spaces or tabs) after "REASON:", if present
            #      2ai txt (.*?) , ensures non-greedy matching
            #      """
            'reason': re.search(r'REASON:\s*(.*?)(?=\nQUESTION|\n$)', block, re.DOTALL),
            'question': re.search(r'QUESTION:\s*(.*?)(?=\nBREAKDOWN|\n$)', block, re.DOTALL),
            'breakdown': re.search(r'BREAKDOWN:\s*(.*?)(?=\nMEASURE|\n$)', block, re.DOTALL),
            'measure': re.search(r'MEASURE:\s*(.*?)(?=\n|$)', block, re.DOTALL)
        }
        
        if all(components.values()):
            cards.append({
                'id': idx,
                'reason': components['reason'].group(1).strip(),
                'question': components['question'].group(1).strip(),
                'breakdown': components['breakdown'].group(1).strip(),
                'measure': components['measure'].group(1).strip()
            })
    return cards

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
def semantic_filter(q1,q2,threshold=0) ->bool:
    """ Return True if a "question" in an insight card is semantically similar to another """

    #embedding & cos similarity
    emb1 =semantic_model .encode(q1).reshape(1, -1)
    emb2 = semantic_model .encode(q2).reshape(1, -1)
    similarity = cosine_similarity(emb1, emb2)[0][0]

    return similarity>threshold

def pandas_query_filter (card: Dict[str, str],df_str:str) ->bool:
    """Returns True if a card retrieves 1 row when converting the card to a pandas query then apply it on df"""
    file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
    dataset = pd.read_csv(file_path)
    
    aggregation = card["breakdown"].split("(")[0].strip()
    numeric_col = card["breakdown"].split("(")[1].replace(")", "").strip()
    categorical_col = card["measure"]

    agg_map = {
        "MEAN": "mean",
        "SUM": "sum",
        "COUNT": "count",
        "MIN": "min",
        "MAX": "max",
        "STD": "std",
        "VAR": "var"
    }

    if aggregation not in agg_map:
        raise ValueError("Unsupported aggregation function")

    query_result = dataset.groupby(categorical_col)[numeric_col].agg(agg_map[aggregation])
    num_rows = query_result.shape[0]
    if (num_rows<=1):
        return False
    return True
