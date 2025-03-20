from typing import List
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from dotenv import load_dotenv
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression  # or another estimator
from sklearn.base import BaseEstimator, TransformerMixin
import json
load_dotenv()

class Feature(BaseModel):
    feature_name: str = Field(description="Name of the feature")
    reasoning: str = Field(description="Reasoning for selecting the feature")

class Feature_list(BaseModel):
    """Main structured output model"""
    features: List[Feature] = Field(
        description="List of Features")

class LLMFeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self,estimator,problem_type,data_report):
        """
        Custom feature selector for feature selection.
        """
        self.system_prompt = hub.pull("automl-feature-selector").messages[0].content
        self.selected_features_ = None
        self.feature_names_ = None
        CONFIGURATIONS={
            'temperature':0.7,
            'model':"gemini-2.0-flash",
        }

        self.llm = ChatGoogleGenerativeAI(
        model=CONFIGURATIONS["model"],
        temperature=CONFIGURATIONS["temperature"]
        ).with_structured_output(Feature_list)

        self.estimator = estimator
        self.problem_type = problem_type
        self.data_report = data_report
        self.reasoning = None

    def recursive_feature_elimination(self,X, y, n_features_to_select=5):
        # Check if estimator has feature_importances_ or coef_ attribute
        try:
            selector = RFE(self.estimator, n_features_to_select=n_features_to_select)
            selector = selector.fit(X, y)
            
            selected_features = X.columns[selector.support_]
            ranking = selector.ranking_
            
            return selected_features, ranking
        except Exception as e:
            return None, None
    
    def calculate_vif(self,X):
        X = sm.add_constant(X)
        vif_data = pd.DataFrame()
        vif_data["feature"] = X.columns
        vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                        for i in range(X.shape[1])]
        return vif_data
    
    def compute_mutual_info(self,X, y, task='regression'):
        # Select function based on task type
        if task == 'regression':
            mi = mutual_info_regression(X, y)
        else:
            mi = mutual_info_classif(X, y)
            
        mi_series = pd.Series(mi, index=X.columns)
        mi_series = mi_series.sort_values(ascending=False)
        return mi_series
    
    def fit(self, X, y=None):
        # Convert X to DataFrame if it's a numpy array
        if isinstance(X, pd.DataFrame):
            X_df = X
            self.feature_names_ = X.columns.tolist()
        else:
            # If X is a numpy array, use feature indices as column names if needed
            if hasattr(X, 'feature_names_in_'):  # From previous transformer
                feature_names = X.feature_names_in_
                print("FROM NUMPY",feature_names,flush=True)
            else:
                feature_names = [f"feature_{i}" for i in range(X.shape[1])]
            X_df = pd.DataFrame(X, columns=feature_names)
            self.feature_names_ = feature_names
        
        mutual_info = self.compute_mutual_info(X_df, y, self.problem_type).to_json()
        vif = self.calculate_vif(X_df).to_json()
        rfe_selected_features, rfe_ranking = self.recursive_feature_elimination(X_df, y,n_features_to_select=X_df.columns.size//2)
        
        # Prepare message content based on available data
        rfe_info = ""
        if rfe_selected_features is not None and rfe_ranking is not None:
            rfe_info = f"This is the RFE ranking: {rfe_ranking}\nDon't choose only based on RFE ranking, consider other factors as well. You may choose more or less than what was given from RFE."
        else:
            rfe_info = "RFE analysis was not applicable for this model type."

        messages = [
            {
            "role": "system",
            "content": self.system_prompt
            },
            {
            "role": "user",
            "content": 
                f"This is the data report:{self.data_report}\n\n\n"
                f"\n\nCurrent Mode: {self.problem_type}\n"
                f"This is the mutual information: {mutual_info}\n"
                f"This is the VIF: {vif}\n"
                f"{rfe_info}\n"
                "Please provide recommendations strictly following the format requirements."
            }
        ]
        response = self.llm.invoke(messages)
        self.selected_features_ = [feature.feature_name for feature in response.features]
        self.reasoning = [{"name": feature.feature_name, "reasoning": feature.reasoning} for feature in response.features]
        
        return self

    def transform(self, X):
        # Convert to DataFrame if it's a numpy array
        if isinstance(X, pd.DataFrame):
            return X[self.selected_features_]
        else:
            # Convert numpy array to DataFrame with selected feature names
            X_df = pd.DataFrame(X, columns=self.feature_names_)
            return X_df[self.selected_features_]

    def get_support(self):
        return self.selected_features_
    


class PreselectedFeatureSelector(BaseEstimator, TransformerMixin):
    def __init__(self, feature_names,indices):
        """
        feature_names: List of feature names selected previously.
        """
        self.feature_names = feature_names
        self.indices = indices

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # If X is a NumPy array, convert it to a DataFrame.
        # Assuming the original column order corresponds to your preprocessed features:
        if not isinstance(X, pd.DataFrame):
            # Here you may need to supply the full list of original feature names if available
            # For illustration, assume that `full_feature_names` is available in this context.
            full_feature_names = [f'feature{i}' for i in range(X.shape[1])]
            X = pd.DataFrame(X, columns=full_feature_names)
        
        # Return only the preselected features
        # Return the selected columns by indices
        X_subset = X.iloc[:, self.indices]
        
        # Rename the columns to match the feature names
        X_subset.columns = self.feature_names
        
        return X_subset