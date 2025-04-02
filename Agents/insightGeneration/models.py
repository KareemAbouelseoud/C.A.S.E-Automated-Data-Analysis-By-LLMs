import uuid
import pandas as pd
from typing import Dict, Annotated,List, Optional, Union
from pydantic import BaseModel, ConfigDict,Field
class DataDescription(BaseModel):
    """ Structured output schema for data description node. """
   
    col_explanation: str = Field(description="explanation of each column")
    overview:str=Field(description="overview description of the dataset")
    key_patterns: str=Field(description="Key patterns in the data distribution")
    qual_issues:str=Field(description="Notable data quality issues in dataset")
    
class InsightCard(BaseModel):
    """Structured output schema for insight cards."""
    model_config = ConfigDict(arbitrary_types_allowed=True,populate_by_name=True) #Add this line
    id: str = Field(default_factory=lambda: str(uuid.uuid4()),description="Unique identifier for the insight card",alias="id")
    insight_type: str = Field(description="Type of insight (e.g., distribution, trend, difference)",alias="insight_type")
    reason: str = Field(description="Analysis rationale",alias="reason")
    question: str = Field(description="Natural language question",alias="question")
    breakdown: str = Field(description="Grouping column name",alias="breakdown")
    measure: str = Field(description="target column",alias="measure")
    aggregation: str = Field(description="Aggregation function (e.g., MIN, MAX, MEAN, COUNT, SUM, STD)",alias="aggregation")
    resulted_df: str = Field(default="", description="Generated DataFrame", alias="resulted_df")
    Score: float = Field(default=0.0, description="Score of the insight card", alias="score")
    Considered: bool = Field(default=False, description="Whether the card was considered important", alias="considered")
    subSpace: str = Field(default=None,description="Subspace of the DataFrame",alias="SubSpace")
    used_columns: list = Field(default=[], description="Columns used in the analysis", alias="used_columns")
    
class InsightCards(BaseModel):
    """Container for multiple insight cards."""
    insight_cards: List[InsightCard] = Field(
        description="List of generated insight cards",
        min_items=0
    )