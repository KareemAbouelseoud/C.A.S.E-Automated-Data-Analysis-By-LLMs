from typing import Dict,List
import pandas as pd
from io import StringIO
from genai_config import model,llm
from pydantic import BaseModel, Field

class QUGEN(BaseModel):
    """ Structured output schema for data description node. """
    id: int=Field(description="id of the insight card")
    reason: str = Field(description="Analysis rationale")
    question:str=Field(description="Natural language question")
    breakdown: str=Field(description="Grouping column")
    measure: str=Field(description="[Aggregation function]([Target column])")


class InsightCards(BaseModel):
    """Container for multiple insight cards."""
    insight_cards: List[QUGEN] = Field(
        description="List of generated insight cards",
        min_items=1
    )

def generate_qugen_prompt(state: Dict, num_cards: int = 5) -> str:
    """Construct QUGEN prompt with dynamic card count and validation rules"""
    examples = "\n\n".join(
        f"### Insight Card {c['id']}\n"
        f"REASON: {c['reason']}\n"
        f"QUESTION: {c['question']}\n"
        f"BREAKDOWN: {c['breakdown']}\n"
        f"MEASURE: {c['measure']}"
        for c in state.get("insight_cards", [])[-3:]  
    )
    file_path = r"C:\Users\DEll\Downloads\digital_marketing_campaign_dataset.csv"
    dataset = pd.read_csv(file_path)
    schema = dataset.columns.tolist()
    basic_stats = dataset.describe(include='all').reset_index()

    schema_list = ', '.join(schema)
   

    
    
    return f"""
    Generate {num_cards} analytical questions about this dataset:
    
    Dataset Description:
    {state['description']}
    
    Schema: {schema_list}
    
    Statistics:
    Numerical: { basic_stats.select_dtypes(include=['number']).to_markdown()}
    Categorical: { basic_stats.select_dtypes(include=['object', 'category']).to_markdown()}
    
    Use format:
    ### Insight Card [NUMBER]
    REASON: [Analysis rationale]
    QUESTION: [Natural language question]
    BREAKDOWN: [Grouping column]
    MEASURE: [Aggregation function]([Target column])
    
    **Generation Rules**
    1. Use different aggregations (MIN/MAX/MEAN/COUNT/SUM/STD)
    2. Measure columns must exist in the schema
    3. No duplicate breakdown/measure combinations
    4. Prioritize under-utilized columns from: {schema_list}
    """