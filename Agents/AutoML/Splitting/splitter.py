from typing import Literal
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain import hub
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
import pandas as pd
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
    X_columns: list[str] = Field(description="The columns to use as features for training the model, Remove any columns that are not needed such as ID columns")
    logic: str = Field(description="The logic used to split the data and selection of features")
    problem_type: Literal["classification", "regression"] = Field(description="The problem type of the data")

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
    print("Beginning Splitter Node")
    
    llm = ChatGoogleGenerativeAI(model=CONFIGURATIONS["model"], temperature=CONFIGURATIONS["temperature"])
    project_id = state["project_id"]
    data_report=mainDatabase.fetch_data_report(project_id)
    df = mainDatabase.fetch_dataset(project_id)

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
    new_X_columns = response.X_columns

    new_X_columns = list(set(new_X_columns).intersection(set(X_columns)))
    X_train,X_test, y_train, y_test=train_test_split(df,new_X_columns, state["y_column"], test_size, shuffle, stratify)
    
    X_train['row_id'] = range(len(X_train))
    y_train = pd.DataFrame({'y': y_train, 'row_id': range(len(y_train))})

    X_test['row_id'] = range(len(X_test))
    y_test = pd.DataFrame({'y': y_test, 'row_id': range(len(y_test))})
    

    return {"X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test, 
            "splitting_logic": response.logic,
            'X_columns':new_X_columns,
            "problem_type": response.problem_type}