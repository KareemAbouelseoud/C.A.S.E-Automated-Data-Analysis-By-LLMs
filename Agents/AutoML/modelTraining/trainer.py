from API.Requests import projectRequests
import fireducks.pandas as pd
from typing import Literal, List
from sklearn import model_selection
import importlib
from sklearn.metrics import mean_squared_error
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from joblib import Parallel, delayed
from tqdm import tqdm
import sys
from AutoML.Deployment.deployer import deployer_node
import numpy as np
import asyncio
from langchain_core.tools import tool,InjectedToolArg
from typing import Annotated
from AutoML.modelEvaluation.evaluator import evaluator_node
from AutoML.Explanation.explainer import explainer_node
from AutoML.Preprocessing.pipeline import preprocess_without_cross_validation
classification_models = {
    "Logistic Regression": ("sklearn.linear_model", "LogisticRegression"),
    "Stochastic Gradient Descent (SGD) Classifier": ("sklearn.linear_model", "SGDClassifier"),
    "Gaussian Naive Bayes": ("sklearn.naive_bayes", "GaussianNB"),
    "Multinomial Naive Bayes": ("sklearn.naive_bayes", "MultinomialNB"),
    "Bernoulli Naive Bayes": ("sklearn.naive_bayes", "BernoulliNB"),
    "K-Nearest Neighbors (KNN) Classifier": ("sklearn.neighbors", "KNeighborsClassifier"),
    "Decision Tree Classifier": ("sklearn.tree", "DecisionTreeClassifier"),
    "Random Forest Classifier": ("sklearn.ensemble", "RandomForestClassifier"),
    "Gradient Boosting Classifier (GBM)": ("sklearn.ensemble", "GradientBoostingClassifier"),
    "Extreme Gradient Boosting (XGBoost) Classifier": ("xgboost", "XGBClassifier"),
    "Light Gradient Boosting Machine (LightGBM) Classifier": ("lightgbm", "LGBMClassifier"),
    "Categorical Boosting (CatBoost) Classifier": ("catboost", "CatBoostClassifier"),
    "Support Vector Machine (SVM) Classifier": ("sklearn.svm", "SVC"),
    "Multi-layer Perceptron (MLP) Classifier": ("sklearn.neural_network", "MLPClassifier"),
    "AdaBoost Classifier": ("sklearn.ensemble", "AdaBoostClassifier"),
    "Extra Trees Classifier": ("sklearn.ensemble", "ExtraTreesClassifier"),
    "Linear Discriminant Analysis (LDA)": ("sklearn.discriminant_analysis", "LinearDiscriminantAnalysis"),
    "Quadratic Discriminant Analysis (QDA)": ("sklearn.discriminant_analysis", "QuadraticDiscriminantAnalysis"),
    "Gaussian Process Classifier": ("sklearn.gaussian_process", "GaussianProcessClassifier"),
    "Histogram-based Gradient Boosting Classifier": ("sklearn.ensemble", "HistGradientBoostingClassifier"),
    "Bagging Classifier": ("sklearn.ensemble", "BaggingClassifier"),
    "Ridge Classifier": ("sklearn.linear_model", "RidgeClassifier"),
    "Passive-Aggressive Classifier": ("sklearn.linear_model", "PassiveAggressiveClassifier"),
    "Nearest Centroid Classifier": ("sklearn.neighbors", "NearestCentroid"),
}

regression_models = {
    "Ordinary Least Squares (OLS) Linear Regression": ("sklearn.linear_model", "LinearRegression"),
    "Ridge Regression (L2 Regularization)": ("sklearn.linear_model", "Ridge"),
    "Lasso Regression (L1 Regularization)": ("sklearn.linear_model", "Lasso"),
    "ElasticNet Regression (L1+L2)": ("sklearn.linear_model", "ElasticNet"),
    "Stochastic Gradient Descent (SGD) Regressor": ("sklearn.linear_model", "SGDRegressor"),
    "Decision Tree Regressor": ("sklearn.tree", "DecisionTreeRegressor"),
    "Random Forest Regressor": ("sklearn.ensemble", "RandomForestRegressor"),
    "Gradient Boosting Regressor (GBR)": ("sklearn.ensemble", "GradientBoostingRegressor"),
    "Extreme Gradient Boosting (XGBoost) Regressor": ("xgboost", "XGBRegressor"),
    "Light Gradient Boosting Machine (LightGBM) Regressor": ("lightgbm", "LGBMRegressor"),
    "Categorical Boosting (CatBoost) Regressor": ("catboost", "CatBoostRegressor"),
    "Support Vector Regression (SVR)": ("sklearn.svm", "SVR"),
    "Multi-layer Perceptron (MLP) Regressor": ("sklearn.neural_network", "MLPRegressor"),
    "AdaBoost Regressor": ("sklearn.ensemble", "AdaBoostRegressor"),
    "Extra Trees Regressor": ("sklearn.ensemble", "ExtraTreesRegressor"),
    "Bayesian Ridge Regression": ("sklearn.linear_model", "BayesianRidge"),
    "Huber Regressor (Robust Regression)": ("sklearn.linear_model", "HuberRegressor"),
    "Theil-Sen Regressor": ("sklearn.linear_model", "TheilSenRegressor"),
    "Quantile Regression": ("sklearn.linear_model", "QuantileRegressor"),
    "Kernel Ridge Regression": ("sklearn.kernel_ridge", "KernelRidge"),
    "Partial Least Squares Regression": ("sklearn.cross_decomposition", "PLSRegression"),
    "Passive-Aggressive Regressor": ("sklearn.linear_model", "PassiveAggressiveRegressor"),
    "Gaussian Process Regressor": ("sklearn.gaussian_process", "GaussianProcessRegressor"),
    "Histogram-based Gradient Boosting Regressor": ("sklearn.ensemble", "HistGradientBoostingRegressor"),
    "Isotonic Regression": ("sklearn.isotonic", "IsotonicRegression"),
}

def get_model(model_name, task="classification"):
    """
    Dynamically loads a model based on the given name.
    
    Parameters:
    - model_name (str): The name of the model.
    - task (str): "classification" or "regression".
    
    Returns:
    - model instance
    """
    model_dict = classification_models if task == "classification" else regression_models

    if model_name not in model_dict:
        raise ValueError(f"Model '{model_name}' not found in {task} models")

    module_name, class_name = model_dict[model_name]
    module = importlib.import_module(module_name)
    model_class = getattr(module, class_name)
    return model_class()  # Instantiate the model

@tool
async def trainer_node(state: Annotated[dict, InjectedToolArg] = None,
                       use_X_preprocessing: Annotated[bool, "Whether to use preprocessing steps for X"] = True,
                       use_Y_preprocessing: Annotated[bool, "Whether to use preprocessing steps for Y"] = True,
                       use_feature_selection: Annotated[bool, "Whether to use feature selection steps"] = True,
                       use_tuning: Annotated[bool, "Whether to use tuning steps"] = True,
                       models: Annotated[list[str], "Models to be trained as named by the Model Selection TOOL, this can be a list of models or a single model. This should be identical to the models that were selected by the Model Selection Tool"] = None):
    """
    Trains a model on the given data. and also evaluates the model and returns an evaluation report.
    """

    problem_type = state["problem_type"]
    X_train=state['X_train']
    y_train=state['y_train']
    X_test=state['X_test']
    y_test=state['y_test']
    selected_features=state.get('selected_features',None)

    X_preprocessing_pipeline=state.get('X_preprocessing_pipeline',None)
    y_preprocessing_pipeline=state.get('Y_preprocessing_pipeline',None)
    if use_X_preprocessing and X_preprocessing_pipeline:
        X_train,X_final_imputer,X_Dropper,X_preprocessing_pipeline=preprocess_without_cross_validation(X_train,X_preprocessing_pipeline)
        X_test,_,_,_=preprocess_without_cross_validation(X_test,X_preprocessing_pipeline,final_imputer=X_final_imputer,Dropper=X_Dropper,fit=False)
    if use_Y_preprocessing and y_preprocessing_pipeline:
        y_train,y_final_imputer,y_Dropper,y_preprocessing_pipeline=preprocess_without_cross_validation(y_train,y_preprocessing_pipeline)
        y_test,_,_,_=preprocess_without_cross_validation(y_test,y_preprocessing_pipeline,final_imputer=y_final_imputer,Dropper=y_Dropper,fit=False)
    
    
    
    if use_feature_selection and selected_features:
        X_train=X_train[selected_features]
        X_test=X_test[selected_features]

    # Remove object columns from X_train and X_test
    X_train = X_train.select_dtypes(exclude=['object'])
    X_test = X_test.select_dtypes(exclude=['object'])


    model_results={}
    cache_results={}
    for model_name in models:
        model = get_model(model_name, problem_type)
        try:
            
            if state['cross_validation']:
                best_model=train_with_cross_validation(X_train=X_train,
                                                        y_train=y_train,
                                                        model=model,
                                                        state=state)
            else:
                if use_X_preprocessing and X_preprocessing_pipeline:
                    X_val,_,_,_=preprocess_without_cross_validation(state['X_val'],X_preprocessing_pipeline,final_imputer=X_final_imputer,Dropper=X_Dropper,fit=False)
                else:
                    X_val=state['X_val']
                if use_Y_preprocessing and y_preprocessing_pipeline:
                    y_val,_,_,_=preprocess_without_cross_validation(state['y_val'],y_preprocessing_pipeline,final_imputer=y_final_imputer,Dropper=y_Dropper,fit=False)
                else:
                    y_val=state['y_val']
                
                if use_feature_selection and selected_features:
                    X_val=X_val[selected_features]
                
                X_val = X_val.select_dtypes(exclude=['object'])
                
                best_model=train_without_cross_validation(X_train=X_train,
                                                            y_train=y_train,
                                                            state=state,
                                                            X_val=X_val,
                                                            y_val=y_val,
                                                            model_name=model_name,
                                                            model=model)

            if use_X_preprocessing and X_preprocessing_pipeline:
                if X_Dropper:
                    X_preprocessing_pipeline.transformers.insert(0,X_Dropper)
                X_preprocessing_pipeline.transformers.append(('Final Imputer',X_final_imputer, X_train.columns))
            metrics=await evaluator_node(model=best_model,X_test=X_test,y_test=y_test,problem_type=state['problem_type'],y_column=state['y_column'])
            past_metrics=state['models'][model_name].get('metrics')
            if problem_type=='classification':
                if not past_metrics or past_metrics['accuracy']<metrics['accuracy']:
                    state['models'][model_name]['metrics']=metrics
                    state['models'][model_name]['model']=best_model
                    if use_X_preprocessing:
                        state['models'][model_name]['X_pipeline']=state.get('X_preprocessing_pipeline',None)
                        state['models'][model_name]['X_preprocessing_logic']=cache_results['X_preprocessing_logic'] if cache_results.get('X_preprocessing_logic',None) else await explainer_node(state.get('X_preprocessing_logic',None))
                        cache_results['X_preprocessing_logic']=state['models'][model_name]['X_preprocessing_logic']
                        state['models'][model_name]['X_pipeline_html']=state.get('X_pipeline_html',None)
                    if use_Y_preprocessing:
                        state['models'][model_name]['Y_pipeline']=state.get('Y_preprocessing_pipeline',None)
                        state['models'][model_name]['Y_preprocessing_logic']=cache_results['Y_preprocessing_logic'] if cache_results.get('Y_preprocessing_logic',None) else await explainer_node(state.get('Y_preprocessing_logic',None))
                        cache_results['Y_preprocessing_logic']=state['models'][model_name]['Y_preprocessing_logic']
                        state['models'][model_name]['Y_pipeline_html']=state.get('Y_pipeline_html',None)
                        y_pipeline=state.get('Y_preprocessing_pipeline',None)
                        if y_pipeline:
                            encoder_mapping = extract_encoder_from_ypreprocessing_pipeline(y_pipeline)
                            if encoder_mapping:
                                state['models'][model_name]['encoder_mapping'] = encoder_mapping



                    state['models'][model_name]['features']=X_train.columns
                    state['models'][model_name]['splitting_logic']=state['splitting_logic']
                    state['models'][model_name]['test_size']=state['test_size']
                    state['models'][model_name]['test_count']=state['test_count']
                    state['models'][model_name]['shuffle']=state['shuffle']
                    if state.get('stratify',None):
                        state['models'][model_name]['stratify']=state['stratify']

                    state['models'][model_name]['cross_validation']=state['cross_validation']

                    if state.get('n_splits',None):
                        state['models'][model_name]['n_splits']=state['n_splits']
                    if state.get('val_size',None):
                        state['models'][model_name]['val_size']=state['val_size']
                        state['models'][model_name]['val_count']=state['val_count']
                    if not cache_results.get('deployment_features',None):
                        deployment_features = await deployer_node(data_report=state['data_report'],X_columns=state['X_columns'])
                        if deployment_features:
                            deployment_features = [feature.dict() if hasattr(feature, 'dict') else 
                                                feature.model_dump() if hasattr(feature, 'model_dump') else 
                                                vars(feature) 
                                                for feature in deployment_features]
                            state['models'][model_name]['deployment'] = deployment_features
                            cache_results['deployment_features']=deployment_features
                    else:
                        state['models'][model_name]['deployment']=cache_results['deployment_features']

            else:
                #regression metrics
                pass

            model_results[model_name]=f'Evaluation metrics: {str(metrics)}'
            state['models'][model_name]['completed']=True

                    

        except Exception as e:
            raise e
            print(f"Failed to train the model for {model_name} with error: {str(e)}")
            model_results[model_name]="Failed to train the model for error: "+str(e)
            continue

    print("---MODELS TRAINED SUCCESSFULLY---")   
    completed=state.get('completed',{})
    completed['trainer']=True
    completed['evaluator']=True
    new_state={
        'models':state['models'],
        'completed':completed
    }
    return [f'Finished training process with these results {str(model_results)}\n\n analyze the metrics and decide whether optimization is needed and how to proceed',new_state]
    

def train_model(param_list, model, X_train, y_train, X_val, y_val, problem_type):
        # Define a function to evaluate a single parameter set
        def evaluate_params(params):
            try:
                model_clone = clone(model)
                model_clone.set_params(**params)
                model_clone.fit(X_train, y_train)
                
                if problem_type == 'classification':
                    score = model_clone.score(X_val, y_val)
                else:
                    y_pred = model_clone.predict(X_val)
                    score = -mean_squared_error(y_val, y_pred)
                    
                sys.stdout.flush()
                return score, model_clone, params
            except Exception as e:
                print(f"Parameter combination failed: {params}")
                print(f"Error: {str(e)}")
                sys.stdout.flush()
                return float('-inf'), None, params

        # Parallel execution with all available cores (n_jobs=-1)
        results = Parallel(n_jobs=-1)(delayed(evaluate_params)(params) for params in tqdm(param_list, desc="Evaluating parameters",file=sys.stdout))
        
        # Find the best model from results
        best_score = float('-inf')
        best_model = None
        best_params = None
        for score, model_clone, params in results:
            if model_clone is not None and score > best_score:
                best_score = score
                best_model = model_clone
                best_params = params
        
        if best_model is None:
            print("All parameter combinations failed, using default model")
            best_model = clone(model)
            best_model.fit(X_train, y_train)
                
        return best_model
    

def train_with_cross_validation(X_train,y_train,model,state):
    # Add 'Model__' prefix to parameter names for Pipeline compatibility
    if 'params_distribution' in state:
        if isinstance(state['params_distribution'], dict):
            prefixed_params = {}
            for param_name, param_value in state['params_distribution'].items():
                prefixed_params[f"Model__{param_name}"] = param_value
            state['params_distribution'] = prefixed_params
    

    if state.get('stratify',None):
        kf=model_selection.StratifiedKFold(n_splits=state['n_splits'], shuffle=state['shuffle'], random_state=42)
    else:
        kf=model_selection.KFold(n_splits=state['n_splits'], shuffle=state['shuffle'], random_state=42)

    if state['mode']=='HERMES':
        model.fit(X_train, y_train)
        best_model = model
    elif state['mode']=='ATHENA':

        random_search =model_selection.RandomizedSearchCV(
            model,
            param_distributions=state['params_distribution'],
            n_iter=state['n_iter'], 
            scoring='accuracy' if state['problem_type'] == 'classification' else 'neg_mean_squared_error',
            n_jobs=-1, cv=kf,
            random_state=42,
            error_score=np.nan
        )
        random_search.fit(X_train, y_train)
        best_model = random_search.best_estimator_
    
    else:

        grid_search = model_selection.GridSearchCV(
            model,
            param_grid=state['params_distribution'],
            scoring='accuracy' if state['problem_type'] == 'classification' else 'neg_mean_squared_error',
            n_jobs=-1, cv=kf,
            error_score=np.nan
            )
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_


    return best_model

def train_without_cross_validation(X_train,y_train,state,X_val,y_val,model_name,model):

    print(f"---Training {model_name}---")
    if state['mode']=='HERMES':        
        model.fit(X_train, y_train)
        best_model = model
    
    elif state['mode']=='ATHENA':
        # Generate random parameter combinations
        param_list = list(model_selection.ParameterSampler(state['params_distribution'], n_iter=state['n_iter'], random_state=42))
        best_model = train_model(param_list, model, X_train, y_train, X_val, y_val, state['problem_type'])

    else:
        param_list = list(model_selection.ParameterGrid(state['params_distribution']))
        best_model = train_model(param_list, model, X_train, y_train, X_val, y_val, state['problem_type'])
    return best_model
    

def extract_encoder_from_ypreprocessing_pipeline(ypreprocessing_pipeline):
    """
    Iterates through the transformers in ypreprocessing_pipeline until it finds
    a transformer named 'Encoder' at index 0.
    
    Args:
        ypreprocessing_pipeline: The preprocessing pipeline for y
        
    Returns:
        The encoder transformer if found, otherwise None
    """
    if ypreprocessing_pipeline is None:
        return None
        
    for transformer in ypreprocessing_pipeline.transformers:
        if transformer[0] == 'Encoder':
            return transformer[1].get_mapping_dict()
            
    return None