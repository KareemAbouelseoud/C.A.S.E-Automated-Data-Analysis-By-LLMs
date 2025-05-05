import re
from typing import List, Dict 

import pandas as pd
from .prompts import QUGEN
from io import StringIO
from typing import List, Union
from pydantic import ValidationError

def parse_insight_cards(response: Union[str, QUGEN, List[QUGEN]]) -> List[QUGEN]:
    if isinstance(response, QUGEN):
        return [response] 
    elif isinstance(response, list) and all(isinstance(card, QUGEN) for card in response):
        return response 
    
    cards = []
    card_blocks = re.split(r'### Insight Card \d+', response)
    
    for idx, block in enumerate(card_blocks[1:], start=1):
        block = block.strip()
        if not block:
            continue
        
        components = {
            'reason': re.search(r'REASON:\s*(.*?)(?=\nQUESTION|\n$)', block, re.DOTALL),
            'question': re.search(r'QUESTION:\s*(.*?)(?=\nBREAKDOWN|\n$)', block, re.DOTALL),
            'breakdown': re.search(r'BREAKDOWN:\s*(.*?)(?=\nMEASURE|\n$)', block, re.DOTALL),
            'measure': re.search(r'MEASURE:\s*(.*?)(?=\n|$)', block, re.DOTALL)
        }
        
        if all(components.values()):
            try:
                card = QUGEN(
                    id=idx,
                    reason=components['reason'].group(1).strip(),
                    question=components['question'].group(1).strip(),
                    breakdown=components['breakdown'].group(1).strip(),
                    measure=components['measure'].group(1).strip()
                )
                cards.append(card)
            except ValidationError as e:
                print(f"Error validating card {idx}: {e}")
    
    return cards





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
