import re
from typing import List, Dict 

#pasrse & validate 
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

def validate_insight_card(card: Dict[str, str], schema: List[str]) -> bool:
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