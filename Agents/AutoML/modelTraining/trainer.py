from sklearn.impute import SimpleImputer
from API.Requests import projectRequests
import pandas as pd
from typing import Literal
from sklearn import model_selection
import importlib
from sklearn.metrics import mean_squared_error
from sklearn.base import clone
from sklearn.pipeline import Pipeline

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

async def trainer_node(state):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    problem_type = state["problem_type"]
    project_id = state["project_id"]
    models_completed = state["models_completed"] if 'models_completed' in state else 0
    model_name = state["models"][models_completed]['model']
    model = get_model(model_name, problem_type)

    Xpreprocessing_pipeline=projectRequests.get_X_pipeline(project_id)
    Ypreprocessing_pipeline=projectRequests.get_Y_pipeline(project_id)
    stratify=state['stratify'] if 'stratify' in state else False

    print(f"---Splitting---")
    df= await projectRequests.get_dataset(project_id)
    X=df[state['X_columns']]
    y=df[state['y_column']]

    X_train,_, y_train,_=model_selection.train_test_split(X,y,test_size=state['test_size'],shuffle=state['shuffle'],stratify=y if stratify else None,random_state=42)
    print(f"---Preprocessing---")
   
    # Giving each row a unique identifier so we can merge them back together later on.
    # This is important because when dropping rows with missing values, the normal row indices will no longer match between X and y.
    try:
        
        if state['cross_validation']:
            best_model,X_Dropper,Xpreprocessing_pipeline,Y_Dropper,Ypreprocessing_pipeline,final_imputer=train_with_cross_validation(X_train=X_train,
                                                                                                                                     y_train=y_train,
                                                                                                                                     model=model,
                                                                                                                                     Xpreprocessing_pipeline=Xpreprocessing_pipeline,
                                                                                                                                     Ypreprocessing_pipeline=Ypreprocessing_pipeline,
                                                                                                                                     state=state,
                                                                                                                                     stratify=stratify)
        else:
            best_model,X_Dropper,Xpreprocessing_pipeline,Y_Dropper,Ypreprocessing_pipeline,final_imputer=train_without_cross_validation(X_train=X_train,
                                                                                                                                        y_train=y_train,
                                                                                                                                        state=state,
                                                                                                                                        stratify=stratify,
                                                                                                                                        Xpreprocessing_pipeline=Xpreprocessing_pipeline,
                                                                                                                                        Ypreprocessing_pipeline=Ypreprocessing_pipeline,
                                                                                                                                        model_name=model_name,
                                                                                                                                        model=model)
        
        print("---MODEL TRAINED SUCCESSFULLY---")   
        
        if Xpreprocessing_pipeline:
            if X_Dropper:
                Xpreprocessing_pipeline.transformers.insert(0,X_Dropper)
            Xpreprocessing_pipeline.transformers.append(('Final Imputer',final_imputer, X_train.columns))
            projectRequests.save_X_pipeline(project_id,Xpreprocessing_pipeline)
        
        if Ypreprocessing_pipeline:
            if Y_Dropper:
                Ypreprocessing_pipeline.transformers.insert(0,Y_Dropper)
            
            projectRequests.save_Y_pipeline(project_id,Ypreprocessing_pipeline)
        
        projectRequests.save_model(model_name,best_model,project_id) 
        print("---MODEL SAVED SUCCESSFULLY---")
        
        models=state['models']
        models[models_completed]['completed']=True
        return {
            'models_completed':models_completed+1,
            'models':models
        }
    
    except Exception as e:
        raise e
        print(f"---ERROR TRAINING MODEL {model_name}---")
        print(e)
        return {
            'models_completed':models_completed+1
        }
    

def train_model(param_list,model,X_train,y_train,X_val,y_val,problem_type):
    best_model = None
    best_score = float('-inf')

    # Loop through sampled parameter sets
    for params in param_list:
        # Clone the model to ensure independence
        model_clone = clone(model)
        model_clone.set_params(**params)
        model_clone.fit(X_train, y_train)  # Train on full training set

        # Evaluate on validation data
        if problem_type == 'classification':
            score = model_clone.score(X_val, y_val)  # Higher is better
        else:
            y_pred = model_clone.predict(X_val)
            score = -mean_squared_error(y_val, y_pred)  # Lower MSE is better, so negate

        if score > best_score:
            best_score = score
            best_model = model_clone
    return best_model
    
def merge_data(X,y,y_column):
    merged=X.merge(y, on='row_id',how='inner')
    X_new = merged.drop(columns=['row_id', y_column])
    y_new = merged[y_column]
    return X_new,y_new

def preprocess_without_cross_validation(data,preprocessor,final_imputer=None,Dropper=None,fit=True):
    preprocessor.transformers = [t for t in preprocessor.transformers if t is not None]

    # Remove duplicates from transformers
    if fit:
        seen_transformers = set()
        unique_transformers = []
        for transformer in preprocessor.transformers:
            if not transformer[1].steps:
                    continue
            if transformer[0] not in seen_transformers:
                unique_transformers.append(transformer)
                seen_transformers.add(transformer[0])
        preprocessor.transformers = unique_transformers
    
    # Separate the Dropper transformer if it exists
    if Dropper:
        temp_data = Dropper[1].fit_transform(data) if fit else Dropper[1].transform(data)
    else:
        if preprocessor.transformers[0][0]=='Drop':
            Dropper=preprocessor.transformers.pop(0)
            if Dropper[1].steps:
                temp_data=Dropper[1].fit_transform(data) if fit else Dropper[1].transform(data)
            else:
                temp_data=data
        else:
            temp_data=data

    # if there are any transformers left, apply them
    if preprocessor.transformers:
        temp_data=preprocessor.fit_transform(temp_data) if fit else preprocessor.transform(temp_data)

        # temp_data is a numpy array, so we need to convert it to a DataFrame and assign column names
        columns=preprocessor.get_feature_names_out()
        # The names of the columns are in the format 'step__column_name', so we need to remove the 'step__' part
        columns=[column.split('__',1)[1] if '__' in column else column for column in columns]
        temp_data=pd.DataFrame(temp_data,columns=columns)
    
    # Last Defence for any missing values
    if final_imputer:
        temp_data=final_imputer.fit_transform(temp_data) if fit else final_imputer.transform(temp_data)
        temp_data=pd.DataFrame(temp_data,columns=columns)
    else:
        temp_data=temp_data.dropna()
    
    return temp_data,final_imputer,Dropper,preprocessor

def train_with_cross_validation(X_train,y_train,model,Xpreprocessing_pipeline,Ypreprocessing_pipeline,state,stratify):
    steps=[]
    X_train['row_id'] = range(len(X_train))
    y_train = pd.DataFrame({state['y_column']: y_train, 'row_id': range(len(y_train))})
    X_columns = X_train.columns.tolist()
    y_columns = y_train.columns.tolist()
    if Xpreprocessing_pipeline:
        seen_transformers = set()
        unique_transformers = []
        if Xpreprocessing_pipeline.transformers[0][0]=='Drop':
            X_Dropper=Xpreprocessing_pipeline.transformers.pop(0)
            if X_Dropper[1].steps:
                X_train=X_Dropper[1].fit_transform(X_train)
        else:
            X_Dropper=None
        
        if Xpreprocessing_pipeline.transformers[-1][0]=='Final Imputer':
            final_imputer=Xpreprocessing_pipeline.transformers.pop(-1)[1]
        else:
            final_imputer=SimpleImputer(strategy='median')

        for transformer in Xpreprocessing_pipeline.transformers:
            if not transformer[1].steps:
                    continue
            if transformer[0] not in seen_transformers:
                unique_transformers.append(transformer)
                seen_transformers.add(transformer[0])
        
        Xpreprocessing_pipeline.transformers = unique_transformers

        steps.append(('preprocessing',Xpreprocessing_pipeline))
        steps.append(('Final Imputer',final_imputer))
    
    else:
        X_Dropper=None
        steps.append(('Final Imputer',SimpleImputer(strategy='median',)))


        
    if Ypreprocessing_pipeline:
        seen_transformers = set()
        unique_transformers = []
        for transformer in Ypreprocessing_pipeline.transformers:
            if not transformer[1].steps:
                    continue
            if transformer[0] not in seen_transformers:
                unique_transformers.append(transformer)
                seen_transformers.add(transformer[0])
        Ypreprocessing_pipeline.transformers = unique_transformers

        if Ypreprocessing_pipeline.transformers[0][0]=='Drop':
            Y_Dropper=Ypreprocessing_pipeline.transformers.pop(0)
            if Y_Dropper[1].steps:
                y_train=Y_Dropper[1].fit_transform(y_train)
        else:
            Y_Dropper=None

        y_train=Ypreprocessing_pipeline.fit_transform(y_train)
    
    else:
        Y_Dropper=None
    X_train= pd.DataFrame(X_train,columns=X_columns)
    y_train= pd.DataFrame(y_train,columns=y_columns)
    X_train,y_train=merge_data(X_train,y_train,state['y_column'])
    
    y_train= y_train.dropna()

    steps.append(('Model',model))
    pipeline = Pipeline(steps)
    # Add 'Model__' prefix to parameter names for Pipeline compatibility
    if 'params_distribution' in state:
        if isinstance(state['params_distribution'], dict):
            prefixed_params = {}
            for param_name, param_value in state['params_distribution'].items():
                prefixed_params[f"Model__{param_name}"] = param_value
            state['params_distribution'] = prefixed_params

    if stratify:
        kf=model_selection.StratifiedKFold(n_splits=state['n_splits'], shuffle=state['shuffle'], random_state=42)
    else:
        kf=model_selection.KFold(n_splits=state['n_splits'], shuffle=state['shuffle'], random_state=42)

    if state['mode']=='HERMES':
        pipeline.fit(X_train, y_train)
        
    elif state['mode']=='ATHENA':

        random_search =model_selection.RandomizedSearchCV(
            pipeline,
            param_distributions=state['params_distribution'],
            n_iter=state['n_iter'], 
            scoring='accuracy' if state['problem_type'] == 'classification' else 'neg_mean_squared_error',
            n_jobs=-1, cv=kf,
            random_state=42
        )
        random_search.fit(X_train, y_train)
        pipeline = random_search.best_estimator_
    
    else:

        grid_search = model_selection.GridSearchCV(
            pipeline,
            param_grid=state['params_distribution'],
            scoring='accuracy' if state['problem_type'] == 'classification' else 'neg_mean_squared_error',
            n_jobs=-1, cv=kf,
            )
        grid_search.fit(X_train, y_train)
        pipeline = grid_search.best_estimator_

    best_model = pipeline.steps.pop(-1)[1]
    final_imputer = pipeline.steps.pop(-1)[1]
    Xpreprocessing_pipeline = pipeline.steps.pop(0)[1]

    return best_model,X_Dropper,Xpreprocessing_pipeline,Y_Dropper,Ypreprocessing_pipeline,final_imputer

def train_without_cross_validation(X_train,y_train,state,stratify,Xpreprocessing_pipeline,Ypreprocessing_pipeline,model_name,model):
    X_train, X_val, y_train, y_val = model_selection.train_test_split(X_train, y_train, test_size=state['val_size'], shuffle=state['shuffle'], stratify=y_train if stratify else None, random_state=42)
    
    X_train['row_id'] = range(len(X_train))
    y_train = pd.DataFrame({state['y_column']: y_train, 'row_id': range(len(y_train))})
    X_val['row_id'] = range(len(X_val))
    y_val = pd.DataFrame({state['y_column']: y_val, 'row_id': range(len(y_val))})
    
    if Xpreprocessing_pipeline:
        if Xpreprocessing_pipeline.transformers[-1][0]=='Final Imputer':
            final_imputer=Xpreprocessing_pipeline.transformers.pop(-1)[1]
        else:
            final_imputer=SimpleImputer(strategy='median')

        X_temp,final_imputer,X_Dropper,Xpreprocessing_pipeline=preprocess_without_cross_validation(data=X_train,preprocessor=Xpreprocessing_pipeline,final_imputer=final_imputer,fit=True)
        X_val_temp,_,_,_=preprocess_without_cross_validation(data=X_val,preprocessor=Xpreprocessing_pipeline,Dropper=X_Dropper, final_imputer=final_imputer,fit=False)
    
    else:
        final_imputer=SimpleImputer(strategy='median')
        X_temp= final_imputer.fit_transform(X_train)
        X_temp=pd.DataFrame(X_temp,columns=X_train.columns.tolist())
        X_val_temp=final_imputer.transform(X_val)
        X_val_temp=pd.DataFrame(X_val_temp,columns=X_val.columns.tolist())

    
    if Ypreprocessing_pipeline:
        y_temp,_,Y_Dropper,Ypreprocessing_pipeline=preprocess_without_cross_validation(data=y_train,preprocessor=Ypreprocessing_pipeline,fit=True)
        y_val_temp,_,_,_=preprocess_without_cross_validation(data=y_val,preprocessor=Ypreprocessing_pipeline,Dropper=Y_Dropper,fit=False)
    else:
        y_temp=y_train.dropna()
        y_val_temp=y_val.dropna()
        Y_Dropper=None

    X_train,y_train=merge_data(X_temp,y_temp,state['y_column'])
    X_val,y_val=merge_data(X_val_temp,y_val_temp,state['y_column'])

    print(f"Object columns in X_train: {X_train.select_dtypes(include=['object']).columns.tolist()}")
    print(f"Object columns in X_val: {X_val.select_dtypes(include=['object']).columns.tolist()}")
    
    X_train = X_train.select_dtypes(exclude=['object'])
    X_val = X_val.select_dtypes(exclude=['object'])

    # Ensure both X_train and X_val contain the same features
    common_columns = X_train.columns.intersection(X_val.columns)
    X_train = X_train[common_columns]
    X_val = X_val[common_columns]
    #endregion
    
    #region Training
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
    return best_model,X_Dropper,Xpreprocessing_pipeline,Y_Dropper,Ypreprocessing_pipeline,final_imputer
    
def decide_to_finish(state)->Literal["model_tuner_node", "model_evaluator_node"]:
    """
    Determines whether to finish training.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    length = len(state['models'])

    if state['models_completed']>=length:
            return "model_evaluator_node"
    else:
        return "model_tuner_node"