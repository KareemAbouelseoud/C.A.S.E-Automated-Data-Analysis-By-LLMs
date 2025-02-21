from typing import List
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END
from langchain import hub
from dotenv import load_dotenv
import sys
import os
from Backend.services.project_service import ProjectService
_project_service=ProjectService()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Database import mainDatabase
load_dotenv()

system_prompt = hub.pull("automl-model-selection-planner").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

classification_models = ["Logistic Regression",
    "Stochastic Gradient Descent (SGD) Classifier",
    "Gaussian Naive Bayes",
    "Multinomial Naive Bayes",
    "Bernoulli Naive Bayes",
    "K-Nearest Neighbors (KNN) Classifier",
    "Decision Tree Classifier",
    "Random Forest Classifier",
    "Gradient Boosting Classifier (GBM)",
    "Extreme Gradient Boosting (XGBoost) Classifier",
    "Light Gradient Boosting Machine (LightGBM) Classifier",
    "Categorical Boosting (CatBoost) Classifier",
    "Support Vector Machine (SVM) Classifier",
    "Multi-layer Perceptron (MLP) Classifier",
    "AdaBoost Classifier",
    "Extra Trees Classifier",
    "Linear Discriminant Analysis (LDA)",
    "Quadratic Discriminant Analysis (QDA)",
    "Gaussian Process Classifier",
    "Histogram-based Gradient Boosting Classifier",
    "Bagging Classifier",
    "Ridge Classifier",
    "Passive-Aggressive Classifier",
    "Quadratic Support Vector Classifier (QSVC)",
    "Nearest Centroid Classifier",
    "Dummy Classifier (Stratified)"]

regression_models = [
    "Ordinary Least Squares (OLS) Linear Regression",
    "Ridge Regression (L2 Regularization)",
    "Lasso Regression (L1 Regularization)",
    "ElasticNet Regression (L1+L2)",
    "Stochastic Gradient Descent (SGD) Regressor",
    "Decision Tree Regressor",
    "Random Forest Regressor",
    "Gradient Boosting Regressor (GBR)",
    "Extreme Gradient Boosting (XGBoost) Regressor",
    "Light Gradient Boosting Machine (LightGBM) Regressor",
    "Categorical Boosting (CatBoost) Regressor",
    "Support Vector Regression (SVR)",
    "Multi-layer Perceptron (MLP) Regressor",
    "AdaBoost Regressor",
    "Extra Trees Regressor",
    "Bayesian Ridge Regression",
    "Huber Regressor (Robust Regression)",
    "Theil-Sen Regressor",
    "Quantile Regression",
    "Kernel Ridge Regression",
    "Partial Least Squares Regression",
    "Passive-Aggressive Regressor",
    "Gaussian Process Regressor",
    "Histogram-based Gradient Boosting Regressor",
    "Isotonic Regression"
]

class ModelRecommendation(BaseModel):
    """Individual model recommendation structure"""
    model: str = Field(description="Full name of the recommended ML model")
    reasoning: str = Field(description="Explanation for selecting this model")


class Selector(BaseModel):
    """Main structured output model"""
    models: List[ModelRecommendation] = Field(
        description="List of recommended models with explanations",
        min_items=1,
        max_items=5
    )


async def model_selector_node(state):
    print(f"Model Selection Started")
    llm = ChatGoogleGenerativeAI(
        model=CONFIGURATIONS["model"],
        temperature=CONFIGURATIONS["temperature"]
    )
    
    project_id = state["project_id"]
    data_report = await _project_service.fetch_data_report(project_id)
    problem_type = state['problem_type']
    X_columns = state['X_columns']
    y_column = state['y_column']
    mode = state['mode']
    
    model_list = classification_models if problem_type == 'classification' else regression_models


    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": 
                f"\n\nCurrent Mode: {mode}\nProblem Type: {problem_type}"
                f"this is the model list: {model_list}\n" 
                f"this is the data report:{data_report}\n"
                f"this is the X columns: {X_columns}\n And this is the y column: {y_column}\n"
                f"This is the preprocessing steps that are going to be done: {state['preprocessing_logic']}\n"
                "Please provide recommendations strictly following the format requirements."
        }
    ]
    response = await llm.with_structured_output(Selector).ainvoke(messages)
    
    return {
        "models": [
            {"model": rec.model, "reasoning": rec.reasoning}
            for rec in response.models
        ]
    }


async def should_continue(state) -> str:
    """Determine workflow continuation based on state validation"""
    if "recommendations" in state:
        rec_count = len(state["recommendations"])
        mode = state["mode"]
        
        if mode == "HERMES" and rec_count != 1:
            print(f"Hermes mode requires 1 recommendation, got {rec_count}, returning to selector node")
            return "selector_node"
            
        elif mode == "ATHENA" and rec_count != 3:
            print(f"Athena mode requires 3 recommendations, got {rec_count}, returning to selector node")
            return "selector_node"
            
        elif mode == "HEPHAESTUS" and rec_count != 5:
            print(f"Hephaestus mode requires 5 recommendations, got {rec_count}, returning to selector node")
            return "selector_node"
    else:
        print("No recommendations found, returning to selector node")
        return "selector_node"
    return END