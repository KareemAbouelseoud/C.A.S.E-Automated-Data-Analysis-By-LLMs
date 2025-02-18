from typing import Literal
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain import hub
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
from Backend.services.project_service import ProjectService
_project_service=ProjectService()
load_dotenv()

system_prompt = hub.pull("automl-splitter").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

class Splitter(BaseModel):
    """ A Pydantic model to structure the output of the language model. """
    test_size: float = Field(description="Test size for splitting the data")
    shuffle: bool = Field(description="Whether to shuffle the data before splitting")
    stratify: bool = Field(description="Whether to stratify the data before splitting")
    logic: str = Field(description="The logic used to split the data")

def train_test_split(df, X_columns, y_column, test_size, shuffle, stratify):
    """ Split the data into training and testing sets. """
    from sklearn.model_selection import train_test_split
    
    X=df[X_columns]
    y=df[y_column]

    return train_test_split(
        X, y,
        test_size=test_size,
        shuffle=shuffle,
        stratify=y if stratify else None
    )


async def splitter_node(state):
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    project_id = state["project_id"]
    data_report=_project_service.fetch_data_report(project_id)
    df = _project_service.fetch_dataset(project_id)
    if 'X_columns' not in state or state['X_columns'] is None:
        X_columns = df.columns.tolist()
    else:
        X_columns = state['X_columns']
    
    messages=[
        {"role": "system", "content":system_prompt+f"\n\n Data Report:\n {data_report}" },
        {"role": "user", "content": f"Train Feature(s): {state['X_columns']} \n Target Feature: {state['y_column']}"},
    ]
    response = await llm.with_structured_output(Splitter).ainvoke(messages)
    test_size = response.test_size
    shuffle = response.shuffle
    stratify = response.stratify
    X_train,X_test, y_train, y_test=train_test_split(df,X_columns, state["y_column"], test_size, shuffle, stratify)
    return {"X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test, 
            "splitting_logic": response.logic,
            'X_columns':X_columns}