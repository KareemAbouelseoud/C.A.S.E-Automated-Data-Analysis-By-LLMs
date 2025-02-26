from Database import mainDatabase
metrics_block={
    "classification_metrics" :"""
        #import block
        from sklearn.metrics import accuracy_score, f1_score, confusion_matrix,roc_auc_score, roc_curve
        from sklearn.metrics import confusion_matrix
        import seaborn as sns
        import matplotlib.pyplot as plt

        #metrics block
        f1 = f1_score(y_test, y_pred, average='weighted')
        cm = confusion_matrix(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        
        # For binary classification
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
        except:
            print("not a binary classification model")

        roc_auc = roc_auc_score(y_test, y_proba)
        fpr, tpr, _ = roc_curve(y_test, y_proba)

        #print block
        print(f"Accuracy: {accuracy:.4f}")
        print(f"F1-Score: {f1:.4f}")

        #plot block
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc="lower right")
        plt.show()

        plt.figure(figsize=(7,5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.xlabel('Predicted Labels')
        plt.ylabel('True Labels')
        plt.title('Confusion Matrix')
        plt.show()
    """,
    
    "regression_metrics" :"""
        #import block
        import matplotlib.pyplot as plt
        from sklearn.metrics import mean_squared_error,r2_score

        #metrics block
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        r2 = r2_score(y_test, y_pred)
        residuals = y_test - y_pred

        #print block
        print(f"RMSE: {rmse:.4f}")
        print(f"R-squared: {r2:.4f}")

        #plot block
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5, edgecolors='w', s=80)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=3)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Actual vs. Predicted Values')
        plt.show()


        plt.figure(figsize=(10, 6))
        plt.scatter(y_pred, residuals, alpha=0.5, edgecolors='w', s=80)
        plt.axhline(y=0, color='k', linestyle='--', lw=2)
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.title('Residual Analysis')
        plt.show()
    """
    }

eval_code = "y_pred = model.predict(X_test)"

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
    
    if mode == "HERMES" and models_completed < 1:
        model = eval_code

    elif mode == "ATHENA" and models_completed < 3:
        model = eval_code

    elif mode == "HEPHAESTUS" and models_completed < 5:
        model = eval_code

    # defining the evaluation metrics based on the problem type
    if problem_type == "classification":
        metrics = metrics_block["classification_metrics"]
    elif problem_type == "regression":
        metrics = metrics_block["regression_metrics"]

    exec(model,globals_dict)
    exec(metrics,globals_dict)
    
    model=globals_dict['model']
    metrics = globals_dict['metrics']

    # Save the model to the database
    mainDatabase.save_model(project_id, model,state['model'][state['models_completed']]['model'])
    print("---MODEL SAVED SUCCESSFULLY---")  
    
    # No errors
    print("---NO CODE TEST FAILURES---")
    return {
        "messages": messages,
        "iterations": iterations,
        "error": "no",
        'models_completed':globals_dict["models_completed"]+1,
    }