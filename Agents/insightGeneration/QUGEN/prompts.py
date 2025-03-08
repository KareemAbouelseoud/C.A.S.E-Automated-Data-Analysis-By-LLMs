from typing import Dict
from dotenv import load_dotenv , find_dotenv
load_dotenv()


import pandas as pd
from io import StringIO
from pydantic import BaseModel, Field

class InsightCard(BaseModel):
    """ Structured output schema for data description node. """
    insight_type: str = Field(description="Type of insight card")
    reason: str = Field(description="Analysis rationale")
    question:str=Field(description="Natural language question")
    breakdown: str=Field(description="Grouping column")
    measure: str=Field(description="[Aggregation function]([Target column])")
##TODO: Add Class List QUGEN
class QUGEN(BaseModel):
    insight_cards: list[InsightCard] = Field(description="List of insight cards")
    
def generate_qugen_prompt(state: Dict, num_cards: int = 5) -> str:
    """Construct QUGEN prompt with dynamic card count and validation rules"""
    examples = "\n\n".join(
        f"### Insight Card {i+1}\n"
        f"Insight Type: {c.insight_type}\n"
        f"REASON: {c.reason}\n"
        f"QUESTION: {c.question}\n"
        f"BREAKDOWN: {c.breakdown}\n"
        f"MEASURE: {c.measure}"
        for i,c in enumerate(state.get("insight_cards", [])[-3:])
    )
    print(state.keys())
    
    df = pd.read_json(StringIO(state['df']))
    schema = df.columns.tolist()
    numerical_stats = df.describe(include=["number"]).reset_index()
    categorical_stats = df.describe(include=["object", "category"]).reset_index()
    basic_stats = {
        "numerical": numerical_stats,
        "categorical": categorical_stats
    }

    schema_list = ', '.join(schema)
    print(f"Schema List: {schema_list}")
    print(f"Numerical Stats: {numerical_stats.to_markdown()}")
    print(f"Categorical Stats: {categorical_stats.to_markdown()}")

    
    
    return f"""
    Generate {num_cards} analytical questions about this dataset:
    
    Dataset Description:
    {state['description']}
    
    Schema: {schema_list}
    
    Statistics:
    Numerical: { basic_stats['numerical'].to_markdown()}
    Categorical: { basic_stats['categorical'].to_markdown()}
    
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
    Also here are some examples of previous cards:
    {examples}
    """