from Database import mainDatabase

classification_model_block = {
    "Logistic Regression": """
y_pred = model.predict(X_test)
""",
    "Stochastic Gradient Descent (SGD) Classifier": """
y_pred = model.predict(X_test)
""",
    "Gaussian Naive Bayes": """
y_pred = model.predict(X_test)
""",
    "Multinomial Naive Bayes": """
y_pred = model.predict(X_test)
""",
    "Bernoulli Naive Bayes": """
y_pred = model.predict(X_test)
""",
    "K-Nearest Neighbors (KNN) Classifier": """
y_pred = model.predict(X_test)
""",
    "Decision Tree Classifier": """
y_pred = model.predict(X_test)
""",
    "Random Forest Classifier": """
y_pred = model.predict(X_test)
""",
    "Gradient Boosting Classifier (GBM)": """
y_pred = model.predict(X_test)
""",
    "Extreme Gradient Boosting (XGBoost) Classifier": """y_pred = model.predict(X_test)
""",
    "Light Gradient Boosting Machine (LightGBM) Classifier": """y_pred = model.predict(X_test)
""",
    "Categorical Boosting (CatBoost) Classifier": """y_pred = model.predict(X_test)
""",
    "Support Vector Machine (SVM) Classifier": """
y_pred = model.predict(X_test)
""",
    "Multi-layer Perceptron (MLP) Classifier": """
y_pred = model.predict(X_test)
""",
    "AdaBoost Classifier": """
y_pred = model.predict(X_test)
""",
    "Extra Trees Classifier": """
y_pred = model.predict(X_test)
""",
    "Linear Discriminant Analysis (LDA)": """
y_pred = model.predict(X_test)
""",
    "Quadratic Discriminant Analysis (QDA)": """
y_pred = model.predict(X_test)
""",
    "Gaussian Process Classifier": """
y_pred = model.predict(X_test)
""",
    "Histogram-based Gradient Boosting Classifier": """
y_pred = model.predict(X_test)
""",
    "Bagging Classifier": """
y_pred = model.predict(X_test)
""",
    "Ridge Classifier": """
y_pred = model.predict(X_test)
""",
    "Passive-Aggressive Classifier": """
y_pred = model.predict(X_test)
""",
    "Quadratic Support Vector Classifier (QSVC)": """
degree=2)y_pred = model.predict(X_test)
""",
    "Nearest Centroid Classifier": """
y_pred = model.predict(X_test)
"""
}

regression_model_block = {
    "Ordinary Least Squares (OLS) Linear Regression": """
y_pred = model.predict(X_test)
""",
    "Ridge Regression (L2 Regularization)": """
y_pred = model.predict(X_test)
""",
    "Lasso Regression (L1 Regularization)": """
y_pred = model.predict(X_test)
""",
    "ElasticNet Regression (L1+L2)": """
y_pred = model.predict(X_test)
""",
    "Stochastic Gradient Descent (SGD) Regressor": """
y_pred = model.predict(X_test)
""",
    "Decision Tree Regressor": """
y_pred = model.predict(X_test)
""",
    "Random Forest Regressor": """
y_pred = model.predict(X_test)
""",
    "Gradient Boosting Regressor (GBR)": """
y_pred = model.predict(X_test)
""",
    "Extreme Gradient Boosting (XGBoost) Regressor": """y_pred = model.predict(X_test)
""",
    "Light Gradient Boosting Machine (LightGBM) Regressor": """y_pred = model.predict(X_test)
""",
    "Categorical Boosting (CatBoost) Regressor": """y_pred = model.predict(X_test)
""",
    "Support Vector Regression (SVR)": """
y_pred = model.predict(X_test)
""",
    "Multi-layer Perceptron (MLP) Regressor": """
y_pred = model.predict(X_test)
""",
    "AdaBoost Regressor": """
y_pred = model.predict(X_test)
""",
    "Extra Trees Regressor": """
y_pred = model.predict(X_test)
""",
    "Bayesian Ridge Regression": """
y_pred = model.predict(X_test)
""",
    "Huber Regressor (Robust Regression)": """
y_pred = model.predict(X_test)
""",
    "Theil-Sen Regressor": """
y_pred = model.predict(X_test)
""",
    "Quantile Regression": """
y_pred = model.predict(X_test)
""",
    "Kernel Ridge Regression": """
y_pred = model.predict(X_test)
""",
    "Partial Least Squares Regression": """
y_pred = model.predict(X_test)
""",
    "Passive-Aggressive Regressor": """
y_pred = model.predict(X_test)
""",
    "Gaussian Process Regressor": """
y_pred = model.predict(X_test)
""",
    "Histogram-based Gradient Boosting Regressor": """
y_pred = model.predict(X_test)
""",
    "Isotonic Regression": """
y_pred = model.predict(X_test)
"""
}
metrics_block={
    "HERMES":"",
    "ATHENA":"",
    "HEPHAESTUS":""

}
def evaluator_node(state):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    print("---CHECKING CODE---")

    # State
    messages = state["messages"]
    code_solution = state["generation"]
    iterations = state["iterations"]
    X_train = state["X_train"]
    y_train = state["y_train"]
    project_id = state["project_id"]
    problem_type = state["problem_type"]
    models_selected = state["models_selected"]
    models_completed = state["models_completed"]
    mode = state["mode"]


    df=mainDatabase.fetch_dataset(state['project_id'])
    preprocessing_pipeline=mainDatabase.fetch_pipeline(project_id)

    globals_dict={'mainDatabase':mainDatabase,
                    'project_id':state['project_id'],
                    'df':df,
                    'X_train':X_train,
                    'y_train':y_train,
                    'preprocessing_pipeline':preprocessing_pipeline}


    # Check imports
    for model in models_selected:
        if mode == "HERMES":
            if models_completed < 1:
                if problem_type == "classification":
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
        
        if mode == "ATHENA":
            if models_completed < 3:
                if problem_type == "classification":
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
                                    
        if mode == "HEPHAESTUS":
            if models_completed < 5:
                if problem_type == "classification":
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
        
        
        exec(model_block,globals_dict)
        models_completed+=1
        
        model=globals_dict['model']

        # Save the model to the database

        mainDatabase.save_model(project_id, model,state['model'][state['models_completed']]['model'])
        print("---MODEL SAVED SUCCESSFULLY---")  
    
    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "generation": code_solution,
        "messages": messages,
        "iterations": iterations,
        "error": "no",
        'models_completed':globals_dict['models_completed'],
    }