from Database import mainDatabase

classification_import_block = {
    "Logistic Regression": "from sklearn.linear_model import LogisticRegression",
    "Stochastic Gradient Descent (SGD) Classifier": "from sklearn.linear_model import SGDClassifier",
    "Gaussian Naive Bayes": "from sklearn.naive_bayes import GaussianNB",
    "Multinomial Naive Bayes": "from sklearn.naive_bayes import MultinomialNB",
    "Bernoulli Naive Bayes": "from sklearn.naive_bayes import BernoulliNB",
    "K-Nearest Neighbors (KNN) Classifier": "from sklearn.neighbors import KNeighborsClassifier",
    "Decision Tree Classifier": "from sklearn.tree import DecisionTreeClassifier",
    "Random Forest Classifier": "from sklearn.ensemble import RandomForestClassifier",
    "Gradient Boosting Classifier (GBM)": "from sklearn.ensemble import GradientBoostingClassifier",
    "Extreme Gradient Boosting (XGBoost) Classifier": "from xgboost import XGBClassifier",
    "Light Gradient Boosting Machine (LightGBM) Classifier": "from lightgbm import LGBMClassifier",
    "Categorical Boosting (CatBoost) Classifier": "from catboost import CatBoostClassifier",
    "Support Vector Machine (SVM) Classifier": "from sklearn.svm import SVC",
    "Multi-layer Perceptron (MLP) Classifier": "from sklearn.neural_network import MLPClassifier",
    "AdaBoost Classifier": "from sklearn.ensemble import AdaBoostClassifier",
    "Extra Trees Classifier": "from sklearn.ensemble import ExtraTreesClassifier",
    "Linear Discriminant Analysis (LDA)": "from sklearn.discriminant_analysis import LinearDiscriminantAnalysis",
    "Quadratic Discriminant Analysis (QDA)": "from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis",
    "Gaussian Process Classifier": "from sklearn.gaussian_process import GaussianProcessClassifier",
    "Histogram-based Gradient Boosting Classifier": "from sklearn.ensemble import HistGradientBoostingClassifier",
    "Bagging Classifier": "from sklearn.ensemble import BaggingClassifier",
    "Ridge Classifier": "from sklearn.linear_model import RidgeClassifier",
    "Passive-Aggressive Classifier": "from sklearn.linear_model import PassiveAggressiveClassifier",
    "Quadratic Support Vector Classifier (QSVC)": "from sklearn.svm import SVC",
    "Nearest Centroid Classifier": "from sklearn.neighbors import NearestCentroid"
}

classification_model_block = {
    "Logistic Regression": '''model = LogisticRegression()
model.fit(X_train, y_train)''',
    "Stochastic Gradient Descent (SGD) Classifier": '''model = SGDClassifier()
model.fit(X_train, y_train)''',
    "Gaussian Naive Bayes": '''model = GaussianNB()
model.fit(X_train, y_train)''',
    "Multinomial Naive Bayes": '''model = MultinomialNB()
model.fit(X_train, y_train)''',
    "Bernoulli Naive Bayes": '''model = BernoulliNB()
model.fit(X_train, y_train)''',
    "K-Nearest Neighbors (KNN) Classifier": '''model = KNeighborsClassifier()
model.fit(X_train, y_train)''',
    "Decision Tree Classifier": '''model = DecisionTreeClassifier()
model.fit(X_train, y_train)''',
    "Random Forest Classifier": '''model = RandomForestClassifier()
model.fit(X_train, y_train)''',
    "Gradient Boosting Classifier (GBM)": '''model = GradientBoostingClassifier()
model.fit(X_train, y_train)''',
    "Extreme Gradient Boosting (XGBoost) Classifier": '''model = XGBClassifier()
model.fit(X_train, y_train)''',
    "Light Gradient Boosting Machine (LightGBM) Classifier": '''model = LGBMClassifier()
model.fit(X_train, y_train)''',
    "Categorical Boosting (CatBoost) Classifier": '''model = CatBoostClassifier()
model.fit(X_train, y_train)''',
    "Support Vector Machine (SVM) Classifier": '''model = SVC()
model.fit(X_train, y_train)''',
    "Multi-layer Perceptron (MLP) Classifier": '''model = MLPClassifier()
model.fit(X_train, y_train)''',
    "AdaBoost Classifier": '''model = AdaBoostClassifier()
model.fit(X_train, y_train)''',
    "Extra Trees Classifier": '''model = ExtraTreesClassifier()
model.fit(X_train, y_train)''',
    "Linear Discriminant Analysis (LDA)": '''model = LinearDiscriminantAnalysis()
model.fit(X_train, y_train)''',
    "Quadratic Discriminant Analysis (QDA)": '''model = QuadraticDiscriminantAnalysis()
model.fit(X_train, y_train)''',
    "Gaussian Process Classifier": '''model = GaussianProcessClassifier()
model.fit(X_train, y_train)''',
    "Histogram-based Gradient Boosting Classifier": '''model = HistGradientBoostingClassifier()
model.fit(X_train, y_train)''',
    "Bagging Classifier": '''model = BaggingClassifier()
model.fit(X_train, y_train)''',
    "Ridge Classifier": '''model = RidgeClassifier()
model.fit(X_train, y_train)''',
    "Passive-Aggressive Classifier": '''model = PassiveAggressiveClassifier()
model.fit(X_train, y_train)''',
    "Quadratic Support Vector Classifier (QSVC)": '''model = SVC(kernel='poly', degree=2)
model.fit(X_train, y_train)''',
    "Nearest Centroid Classifier": '''model = NearestCentroid()
model.fit(X_train, y_train)'''
}

regression_import_block = {
    "Ordinary Least Squares (OLS) Linear Regression": "from sklearn.linear_model import LinearRegression",
    "Ridge Regression (L2 Regularization)": "from sklearn.linear_model import Ridge",
    "Lasso Regression (L1 Regularization)": "from sklearn.linear_model import Lasso",
    "ElasticNet Regression (L1+L2)": "from sklearn.linear_model import ElasticNet",
    "Stochastic Gradient Descent (SGD) Regressor": "from sklearn.linear_model import SGDRegressor",
    "Decision Tree Regressor": "from sklearn.tree import DecisionTreeRegressor",
    "Random Forest Regressor": "from sklearn.ensemble import RandomForestRegressor",
    "Gradient Boosting Regressor (GBR)": "from sklearn.ensemble import GradientBoostingRegressor",
    "Extreme Gradient Boosting (XGBoost) Regressor": "from xgboost import XGBRegressor",
    "Light Gradient Boosting Machine (LightGBM) Regressor": "from lightgbm import LGBMRegressor",
    "Categorical Boosting (CatBoost) Regressor": "from catboost import CatBoostRegressor",
    "Support Vector Regression (SVR)": "from sklearn.svm import SVR",
    "Multi-layer Perceptron (MLP) Regressor": "from sklearn.neural_network import MLPRegressor",
    "AdaBoost Regressor": "from sklearn.ensemble import AdaBoostRegressor",
    "Extra Trees Regressor": "from sklearn.ensemble import ExtraTreesRegressor",
    "Bayesian Ridge Regression": "from sklearn.linear_model import BayesianRidge",
    "Huber Regressor (Robust Regression)": "from sklearn.linear_model import HuberRegressor",
    "Theil-Sen Regressor": "from sklearn.linear_model import TheilSenRegressor",
    "Quantile Regression": "from sklearn.linear_model import QuantileRegressor",
    "Kernel Ridge Regression": "from sklearn.kernel_ridge import KernelRidge",
    "Partial Least Squares Regression": "from sklearn.cross_decomposition import PLSRegression",
    "Passive-Aggressive Regressor": "from sklearn.linear_model import PassiveAggressiveRegressor",
    "Gaussian Process Regressor": "from sklearn.gaussian_process import GaussianProcessRegressor",
    "Histogram-based Gradient Boosting Regressor": "from sklearn.ensemble import HistGradientBoostingRegressor",
    "Isotonic Regression": "from sklearn.isotonic import IsotonicRegression"
}

regression_model_block = {
    "Ordinary Least Squares (OLS) Linear Regression": '''model = LinearRegression()
model.fit(X_train, y_train)''',
    "Ridge Regression (L2 Regularization)": '''model = Ridge()
model.fit(X_train, y_train)''',
    "Lasso Regression (L1 Regularization)": '''model = Lasso()
model.fit(X_train, y_train)''',
    "ElasticNet Regression (L1+L2)": '''model = ElasticNet()
model.fit(X_train, y_train)''',
    "Stochastic Gradient Descent (SGD) Regressor": '''model = SGDRegressor()
model.fit(X_train, y_train)''',
    "Decision Tree Regressor": '''model = DecisionTreeRegressor()
model.fit(X_train, y_train)''',
    "Random Forest Regressor": '''model = RandomForestRegressor()
model.fit(X_train, y_train)''',
    "Gradient Boosting Regressor (GBR)": '''model = GradientBoostingRegressor()
model.fit(X_train, y_train)''',
    "Extreme Gradient Boosting (XGBoost) Regressor": '''model = XGBRegressor()
model.fit(X_train, y_train)''',
    "Light Gradient Boosting Machine (LightGBM) Regressor": '''model = LGBMRegressor()
model.fit(X_train, y_train)''',
    "Categorical Boosting (CatBoost) Regressor": '''model = CatBoostRegressor()
model.fit(X_train, y_train)''',
    "Support Vector Regression (SVR)": '''model = SVR()
model.fit(X_train, y_train)''',
    "Multi-layer Perceptron (MLP) Regressor": '''model = MLPRegressor()
model.fit(X_train, y_train)''',
    "AdaBoost Regressor": '''model = AdaBoostRegressor()
model.fit(X_train, y_train)''',
    "Extra Trees Regressor": '''model = ExtraTreesRegressor()
model.fit(X_train, y_train)''',
    "Bayesian Ridge Regression": '''model = BayesianRidge()
model.fit(X_train, y_train)''',
    "Huber Regressor (Robust Regression)": '''model = HuberRegressor()
model.fit(X_train, y_train)''',
    "Theil-Sen Regressor": '''model = TheilSenRegressor()
model.fit(X_train, y_train)''',
    "Quantile Regression": '''model = QuantileRegressor()
model.fit(X_train, y_train)''',
    "Kernel Ridge Regression": '''model = KernelRidge()
model.fit(X_train, y_train)''',
    "Partial Least Squares Regression": '''model = PLSRegression()
model.fit(X_train, y_train)''',
    "Passive-Aggressive Regressor": '''model = PassiveAggressiveRegressor()
model.fit(X_train, y_train)''',
    "Gaussian Process Regressor": '''model = GaussianProcessRegressor()
model.fit(X_train, y_train)''',
    "Histogram-based Gradient Boosting Regressor": '''model = HistGradientBoostingRegressor()
model.fit(X_train, y_train)''',
    "Isotonic Regression": '''model = IsotonicRegression()
model.fit(X_train, y_train)'''
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
                    if model in classification_import_block:
                        import_block = classification_import_block[model]
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_import_block:
                        import_block = regression_import_block[model]
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
        
        if mode == "ATHENA":
            if models_completed < 3:
                if problem_type == "classification":
                    if model in classification_import_block:
                        import_block = classification_import_block[model]
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_import_block:
                        import_block = regression_import_block[model]
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
                                    
        if mode == "HEPHAESTUS":
            if models_completed < 5:
                if problem_type == "classification":
                    if model in classification_import_block:
                        import_block = classification_import_block[model]
                    if model in classification_model_block:
                        model_block = classification_model_block[model]
                elif problem_type == "regression":
                    if model in regression_import_block:
                        import_block = regression_import_block[model]
                    if model in regression_model_block:
                        model_block = regression_model_block[model]
        
        
        exec(import_block + "\n" + model_block,globals_dict)
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