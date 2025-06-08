from typing import List
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
import fireducks.pandas as pd
from AutoML.Preprocessing.pipeline import preprocess_without_cross_validation
from typing import Optional,Annotated
from sklearn.feature_selection import RFE
from langchain_core.tools import InjectedToolArg,tool
from AutoML.modelTraining.trainer import get_model
import numpy as np

load_dotenv()

class Feature(BaseModel):
    feature_name: str = Field(description="Name of the feature")
    reasoning: str = Field(description="Reasoning for selecting the feature")

class Feature_list(BaseModel):
    """Main structured output model"""
    features: List[Feature] = Field(
        description="List of Features")

system_prompt= hub.pull("automl-feature-selector").messages[0].content
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.5-flash-preview-04-17",
}
llm = ChatGoogleGenerativeAI(
        model=CONFIGURATIONS["model"],
        temperature=CONFIGURATIONS["temperature"]
        ).with_structured_output(Feature_list)


def recursive_feature_elimination(X, y, estimators, n_features_to_select=5):
    # Make sure X contains only numeric values
    numeric_X = X.select_dtypes(include=['number'])
    
    # If no numeric columns available, return empty results
    if numeric_X.empty:
        return {}
        
    # Ensure n_features_to_select is valid
    n_features_to_select = min(max(1, n_features_to_select), numeric_X.shape[1])
    
    results = {}
    for estimator in estimators:
        try:
            model = get_model(estimator)
            selector = RFE(model, n_features_to_select=n_features_to_select)
            selector = selector.fit(numeric_X, y)
            results[estimator] = {'support': selector.support_.tolist(), 'ranking': selector.ranking_.tolist()}
        except Exception as e:
            print(f"Error in RFE for estimator {estimator}: {str(e)}")
            # Don't add failed estimator to results
            
    return results

def calculate_vif(X):
    try:
        # Check if there are enough features to calculate VIF (need at least 2)
        if X.shape[1] < 2:
            vif_data = pd.DataFrame()
            vif_data["feature"] = X.columns
            vif_data["VIF"] = [1.0] * len(X.columns)  # Default to 1.0 when not computable
            return vif_data
            
        X = sm.add_constant(X)
        vif_data = pd.DataFrame()
        vif_data["feature"] = X.columns
        
        # Calculate VIF for each feature
        vif_values = []
        for i in range(X.shape[1]):
            try:
                vif_val = variance_inflation_factor(X.values, i)
                # Handle infinite or NaN values
                if pd.isna(vif_val) or np.isinf(vif_val):
                    vif_val = 999.0  # Use a high value to indicate potential issues
                vif_values.append(vif_val)
            except:
                vif_values.append(999.0)  # Use a high value to indicate potential issues
                
        vif_data["VIF"] = vif_values
        return vif_data
    except Exception as e:
        # Return an empty DataFrame if an error occurs
        print(f"Error in VIF calculation: {str(e)}")
        vif_data = pd.DataFrame()
        vif_data["feature"] = X.columns
        vif_data["VIF"] = [999.0] * len(X.columns)  # Use a high value to indicate potential issues
        return vif_data

def compute_mutual_info(X, y, task='regression'):
    # Make sure X contains only numeric values
    try:
        # Try to convert non-numeric columns to numeric if possible
        numeric_X = X.select_dtypes(include=['number'])
        
        # If no numeric columns are available, return empty Series
        if numeric_X.empty:
            return pd.Series([], index=[])
            
        # Select function based on task type
        if task == 'regression':
            mi = mutual_info_regression(numeric_X, y)
        else:
            # Ensure y is flattened and in correct format for classification
            if hasattr(y, 'values'):
                y_values = y.values.ravel()
            else:
                y_values = y.ravel()
            
            mi = mutual_info_classif(numeric_X, y_values)
            
        mi_series = pd.Series(mi, index=numeric_X.columns)
        mi_series = mi_series.sort_values(ascending=False)
        return mi_series
    except Exception as e:
        # Return empty series if there's an error
        print(f"Error in compute_mutual_info: {str(e)}")
        return pd.Series([], index=[])

@tool 
async def feature_selector_node(state: Annotated[dict,InjectedToolArg] = None):
            # task: Optional[Annotated[str,"This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]] = None):
    """
    Selects the best features from the given data.
    """
    print("Feature Selection Started")
    X_train = state['X_train']
    y_train = state['y_train']
    X_preprocessing_pipeline=state.get('X_preprocessing_pipeline',None)
    y_preprocessing_pipeline=state.get('Y_preprocessing_pipeline',None)
    if X_preprocessing_pipeline:
       X_train,_,_,_= preprocess_without_cross_validation(X_train,X_preprocessing_pipeline)
    if y_preprocessing_pipeline:
        y_train,_,_,_=preprocess_without_cross_validation(y_train,y_preprocessing_pipeline)

    problem_type = state['problem_type']
    data_report=state['data_report']
    models=state.get('models',{})
    if models:
        models=list(models.keys())
    else:
        if problem_type=='regression':
            models=['LinearRegression','Random Forest Regressor']
        else:
            models=['Logistic Regression','Random Forest Classifier']

    # Safely compute mutual information and VIF with error handling
    try:
        mutual_info = compute_mutual_info(X_train, y_train, problem_type).to_json()
    except Exception as e:
        mutual_info = "{}"
        print(f"Error computing mutual info: {str(e)}")
    
    try:
        # Filter to numeric columns for VIF calculation
        numeric_X = X_train.select_dtypes(include=['number'])
        if not numeric_X.empty:
            vif = calculate_vif(numeric_X).to_json()
        else:
            vif = "{}"
    except Exception as e:
        vif = "{}"
        print(f"Error computing VIF: {str(e)}")
    
    try:
        rfe_results = recursive_feature_elimination(X_train, y_train,estimators=models,n_features_to_select=max(1, X_train.columns.size//2))
    except Exception as e:
        rfe_results = None
        print(f"Error in recursive feature elimination: {str(e)}")
    
    # Prepare message content based on available data
    rfe_info = ""
    if rfe_results is not None:
        rfe_info = f"This is the RFE results based on different models: {rfe_results}\nDon't choose only based on RFE ranking, consider other factors as well. You may choose more or less than what was given from RFE."
    else:
        rfe_info = "RFE analysis was not applicable for this data."

    messages= [{"role": "system","content": system_prompt}]+state.get('feature_selection_messages', [])
    content=""
    if state.get('evaluation_metrics', None):
        content+=f"Here are the evaluation metrics for your previous steps: {state['evaluation_metrics']}\n\n Attempt to Analyze and Improve, if possible, if not return the same values.\n\n"
    # if task:
    #     content+=f"Here are the instructions for you given by the supervisor: {task}\n\n"
    content+=f"""\n\nCurrent Mode: {problem_type}\n
            This is the data report:{data_report}\n\n\n
            This is the mutual information: {mutual_info}\n
            This is the VIF: {vif}\n
            {rfe_info}\n
            Please provide recommendations strictly following the format requirements."""
    
    messages.append({"role": "user", "content": content})

    response = await llm.ainvoke(messages)

    selected_features_ = [feature.feature_name for feature in response.features]

    # Ensure all selected features exist in the dataframe
    valid_features = [f for f in selected_features_ if f in X_train.columns]
    if not valid_features:
        # If no valid features selected, use all columns
        valid_features = X_train.columns.tolist()
        
    X_train=X_train[valid_features]
    completed=state.get('completed',{})
    completed['feature_selector']=True
    new_state={
        'feature_selection_messages':messages[1:]+[{"role": "assistant", "content": f"Here is the output: {response.model_dump_json()}"}],
        'selected_features': valid_features,
        'completed':completed
    }

    return [f'The selected features are now {valid_features}',new_state]