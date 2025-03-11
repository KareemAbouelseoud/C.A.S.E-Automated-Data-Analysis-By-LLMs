import sys
import os
from typing_extensions import TypedDict,NotRequired
from langgraph.graph import StateGraph, START
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from AutoML.Splitting.splitter import splitter_node
from AutoML.Preprocessing.pipeline import graph as preprocessor_graph
from AutoML.ModelSelection.selector import model_selector_node,brancher as model_selector_brancher
from AutoML.modelTraining.trainer import trainer_node, decide_to_finish as trainer_decide_to_finish
from AutoML.modelEvaluation.evaluator import evaluator_node
from AutoML.HPO.tuner import tuner_node,tuner_decide_to_finish
from API.Requests import projectRequests

CONFIGURATIONS= {
    'recursion_limit': 100,
}
class State(TypedDict):
    """
    A class to represent the state of the application.
    """
    project_id:str # Project ID
    data_report: NotRequired[str] # Data Report
    mode: str # Mode Selected by the User
    user_preferences: NotRequired[str] # User Preferences
    
    #Data Names
    X_columns: NotRequired[list[str]] # X Columns (user then LLM defined)
    y_column: NotRequired[str] # Y Column (user defined)
    problem_type: NotRequired[str] # Problem Type Identified by the LLM

    #Splitting
    splitting_logic: NotRequired[str] # Splitting Steps Documented for the User and rest of Agents
    test_size: NotRequired[float] # Test Size
    shuffle: NotRequired[bool] # Shuffle
    stratify: NotRequired[bool] # Stratify
    cross_validation: NotRequired[bool] # Cross Validation
    
    n_splits: NotRequired[int] # Number of Splits
    val_size: NotRequired[float] # Validation Size
    
    #Tuning
    n_iter: NotRequired[int] # Number of Iterations
    params_distribution: NotRequired[dict] # Parameters Distribution

    #Preprocessing Pipeline
    X_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    Y_preprocessing_logic: NotRequired[str] # Preprocessing Steps Documented for the User and rest of Agents
    
    #Model
    training_logic: NotRequired[str] # Training Steps Documented for the User and rest of Agents
    models: NotRequired[list] # Model Names Selected by LLM
    models_completed: NotRequired[int] # Number of Models Completed

    #Evaluation
    evaluation_reports: NotRequired[list] # Evaluation Reports


builder = StateGraph(State)
builder.add_node('splitter_node', splitter_node)
builder.add_node('preprocessor_node', preprocessor_graph)
builder.add_node("model_selector_node", model_selector_node)
builder.add_node("model_trainer_node",trainer_node)
builder.add_node("model_tuner_node",tuner_node)
builder.add_node("model_evaluator_node",evaluator_node)

builder.add_edge(START, 'splitter_node')
builder.add_edge('splitter_node', 'preprocessor_node')
builder.add_edge('preprocessor_node', "model_selector_node")
builder.add_conditional_edges('model_selector_node',model_selector_brancher)
builder.add_conditional_edges("model_tuner_node", tuner_decide_to_finish)
builder.add_conditional_edges('model_trainer_node',trainer_decide_to_finish)

graph = builder.compile()




async def automl(project_id,data_report,mode,label,features=None,user_preferences=None):
    print("AUTOML STARTED")
    async for chunk in graph.astream({'data_report':data_report,'project_id':project_id,'mode':mode,'X_columns':features,'y_column':label,'user_preferences':user_preferences},config=CONFIGURATIONS, stream_mode=['updates','values']):
        if chunk[0] == 'values':
            response=chunk[1]
        elif chunk[0] == 'updates':
            # print("Update:",chunk[1])
            pass

    print("Final Response:",response)
import asyncio
asyncio.run(automl('67c1ba76e833b024ca9cb615',
                   """{
  "General Info": {
      "Number of Rows": 891,
      "Number of Columns": 12,
      "Missing Data Summary": {
          "PassengerId": 0,
          "Survived": 0,
          "Pclass": 0,
          "Name": 0,
          "Sex": 0,
          "Age": 177,
          "SibSp": 0,
          "Parch": 0,
          "Ticket": 0,
          "Fare": 0,
          "Cabin": 687,
          "Embarked": 2
      },
      "Feature Types Summary": {
          "int64": 5,
          "object": 4,
          "float64": 2,
          "category": 0,
          "bool": 0
      }
  },
  "Feature Details": {
      "PassengerId": {
          "Column Description": "Unique identifier for passengers",
          "Data Type": "int64",
          "Unique Values Count": 891,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 446.0,
              "Median": 446.0,
              "Standard Deviation": 257.353842,
              "Min": 1.0,
              "Max": 891.0
          }
      },
      "Survived": {
          "Column Description": "Survival status (0 = No, 1 = Yes)",
          "Data Type": "int64",
          "Unique Values Count": 2,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 0.383838,
              "Median": 0.0,
              "Standard Deviation": 0.486592,
              "Min": 0.0,
              "Max": 1.0
          },
          "Value Distribution": {
              "0": 549,
              "1": 342
          }
      },
      "Pclass": {
          "Column Description": "Ticket class (1 = 1st, 2 = 2nd, 3 = 3rd)",
          "Data Type": "int64",
          "Unique Values Count": 3,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 2.308642,
              "Median": 3.0,
              "Standard Deviation": 0.836071,
              "Min": 1.0,
              "Max": 3.0
          },
          "Value Distribution": {
              "1": 216,
              "2": 184,
              "3": 491
          }
      },
      "Sex": {
          "Column Description": "Gender of the passenger",
          "Data Type": "object",
          "Unique Values Count": 2,
          "Missing Values": 0,
          "Value Distribution": {
              "male": 577,
              "female": 314
          }
      },
      "Age": {
          "Column Description": "Age of the passenger in years",
          "Data Type": "float64",
          "Unique Values Count": 88,
          "Missing Values": 177,
          "Descriptive Statistics": {
              "Mean": 29.699118,
              "Median": 28.0,
              "Standard Deviation": 14.526497,
              "Min": 0.42,
              "Max": 80.0
          }
      },
      "SibSp": {
          "Column Description": "Number of siblings/spouses aboard",
          "Data Type": "int64",
          "Unique Values Count": 7,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 0.523008,
              "Median": 0.0,
              "Standard Deviation": 1.102743,
              "Min": 0.0,
              "Max": 8.0
          }
      },
      "Parch": {
          "Column Description": "Number of parents/children aboard",
          "Data Type": "int64",
          "Unique Values Count": 7,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 0.381594,
              "Median": 0.0,
              "Standard Deviation": 0.806057,
              "Min": 0.0,
              "Max": 6.0
          }
      },
      "Fare": {
          "Column Description": "Fare paid by the passenger",
          "Data Type": "float64",
          "Unique Values Count": 248,
          "Missing Values": 0,
          "Descriptive Statistics": {
              "Mean": 32.204208,
              "Median": 14.4542,
              "Standard Deviation": 49.693429,
              "Min": 0.0,
              "Max": 512.3292
          }
      },
      "Cabin": {
          "Column Description": "Cabin number",
          "Data Type": "object",
          "Unique Values Count": 147,
          "Missing Values": 687
      },
      "Embarked": {
          "Column Description": "Port of embarkation (C = Cherbourg, Q = Queenstown, S = Southampton)",
          "Data Type": "object",
          "Unique Values Count": 3,
          "Missing Values": 2,
          "Value Distribution": {
              "S": 644,
              "C": 168,
              "Q": 77
          }
      }
  },
  "Correlations": {
      "Survived": {
          "Pclass": -0.338481,
          "Age": -0.077221,
          "SibSp": -0.035322,
          "Parch": 0.081629,
          "Fare": 0.257307
      },
      "Pclass": {
          "Age": -0.369226,
          "Fare": -0.549500
      },
      "Fare": {
          "Pclass": -0.549500,
          "Survived": 0.257307
      }
  },
  "Numeric-Categorical Relationships": {
      "Sex -> Survived": {
          "mean": {
              "male": 0.188908,
              "female": 0.742038
          }
      },
      "Pclass -> Survived": {
          "mean": {
              "1": 0.629630,
              "2": 0.472826,
              "3": 0.242363
          }
      },
      "Embarked -> Survived": {
          "mean": {
              "C": 0.553571,
              "Q": 0.389610,
              "S": 0.336957
          }
      },
      "Sex -> Fare": {
          "mean": {
              "male": 25.523893,
              "female": 44.479818
          }
      },
      "Pclass -> Fare": {
          "mean": {
              "1": 84.154688,
              "2": 20.662183,
              "3": 13.675550
          }
      }
  }
}
""",
                        'ATHENA','Survived'))