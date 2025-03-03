from sklearn.impute import SimpleImputer
from API.Requests import projectRequests
import pandas as pd
classification_import_block = {
    "Logistic Regression": 
        """from sklearn.linear_model import LogisticRegression
model = LogisticRegression()""",
    
    "Stochastic Gradient Descent (SGD) Classifier": 
        """from sklearn.linear_model import SGDClassifier
model = SGDClassifier()""",
    
    "Gaussian Naive Bayes": 
        """from sklearn.naive_bayes import GaussianNB
model = GaussianNB()""",
    
    "Multinomial Naive Bayes": 
        """from sklearn.naive_bayes import MultinomialNB
model = MultinomialNB()""",
    
    "Bernoulli Naive Bayes": 
        """from sklearn.naive_bayes import BernoulliNB
model = BernoulliNB()""",
    
    "K-Nearest Neighbors (KNN) Classifier": 
        """from sklearn.neighbors import KNeighborsClassifier
model = KNeighborsClassifier()""",
    
    "Decision Tree Classifier": 
        """from sklearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier()""",
    
    "Random Forest Classifier": 
        """from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()""",
    
    "Gradient Boosting Classifier (GBM)": 
        """from sklearn.ensemble import GradientBoostingClassifier
model = GradientBoostingClassifier()""",
    
    "Extreme Gradient Boosting (XGBoost) Classifier": 
        """from xgboost import XGBClassifier
model = XGBClassifier()""",

    "Light Gradient Boosting Machine (LightGBM) Classifier": 
        """from lightgbm import LGBMClassifier
model = LGBMClassifier()""",

    "Categorical Boosting (CatBoost) Classifier": 
        """from catboost import CatBoostClassifier
model = CatBoostClassifier()""",

    "Support Vector Machine (SVM) Classifier": 
        """from sklearn.svm import SVC
model = SVC()""",
    
    "Multi-layer Perceptron (MLP) Classifier": 
        """from sklearn.neural_network import MLPClassifier
model = MLPClassifier()""",
    
    "AdaBoost Classifier": 
        """from sklearn.ensemble import AdaBoostClassifier
model = AdaBoostClassifier()""",
    
    "Extra Trees Classifier": 
        """from sklearn.ensemble import ExtraTreesClassifier
model = ExtraTreesClassifier()""",
    
    "Linear Discriminant Analysis (LDA)": 
        """from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
model = LinearDiscriminantAnalysis()""",
    
    "Quadratic Discriminant Analysis (QDA)": 
        """from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
model = QuadraticDiscriminantAnalysis()""",
    
    "Gaussian Process Classifier": 
        """from sklearn.gaussian_process import GaussianProcessClassifier
model = GaussianProcessClassifier()""",
    
    "Histogram-based Gradient Boosting Classifier": 
        """from sklearn.ensemble import HistGradientBoostingClassifier
model = HistGradientBoostingClassifier()""",
    
    "Bagging Classifier": 
        """from sklearn.ensemble import BaggingClassifier
model = BaggingClassifier()""",
    
    "Ridge Classifier": 
        """from sklearn.linear_model import RidgeClassifier
model = RidgeClassifier()""",
    
    "Passive-Aggressive Classifier": 
        """from sklearn.linear_model import PassiveAggressiveClassifier
model = PassiveAggressiveClassifier()""",
    
    "Quadratic Support Vector Classifier (QSVC)": 
        """from sklearn.svm import SVC
model   = SVC(kernel""",
    
    "Nearest Centroid Classifier": 
        """from sklearn.neighbors import NearestCentroid
model = NearestCentroid()"""
}

regression_import_block = {
    "Ordinary Least Squares (OLS) Linear Regression": 
        """from sklearn.linear_model import LinearRegression
model = LinearRegression()""",
    
    "Ridge Regression (L2 Regularization)": 
        """from sklearn.linear_model import Ridge
model = Ridge()""",
    
    "Lasso Regression (L1 Regularization)": 
        """from sklearn.linear_model import Lasso
model = Lasso()""",
    
    "ElasticNet Regression (L1+L2)": 
        """from sklearn.linear_model import ElasticNet
model = ElasticNet()""",
    
    "Stochastic Gradient Descent (SGD) Regressor": 
        """from sklearn.linear_model import SGDRegressor
model = SGDRegressor()""",
    
    "Decision Tree Regressor": 
        """from sklearn.tree import DecisionTreeRegressor
model = DecisionTreeRegressor()""",
    
    "Random Forest Regressor": 
        """from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()""",
    
    "Gradient Boosting Regressor (GBR)": 
        """from sklearn.ensemble import GradientBoostingRegressor
model = GradientBoostingRegressor()""",
    
    "Extreme Gradient Boosting (XGBoost) Regressor":
        """from xgboost import XGBRegressor
model = XGBRegressor()""",
    
    "Light Gradient Boosting Machine (LightGBM) Regressor": 
        """from lightgbm import LGBMRegressor
model = LGBMRegressor()""",
    
    "Categorical Boosting (CatBoost) Regressor": 
        """from catboost import CatBoostRegressor
model = CatBoostRegressor()""",
    
    "Support Vector Regression (SVR)": 
        """from sklearn.svm import SVR
model = SVR()""",
    
    "Multi-layer Perceptron (MLP) Regressor": 
        """from sklearn.neural_network import MLPRegressor
model = MLPRegressor()""",
    
    "AdaBoost Regressor": 
        """from sklearn.ensemble import AdaBoostRegressor
model = AdaBoostRegressor()""",
    
    "Extra Trees Regressor": 
        """from sklearn.ensemble import ExtraTreesRegressor
model = ExtraTreesRegressor()""",
    
    "Bayesian Ridge Regression": 
        """from sklearn.linear_model import BayesianRidge
model = BayesianRidge()""",
    
    "Huber Regressor (Robust Regression)": 
        """from sklearn.linear_model import HuberRegressor
model = HuberRegressor()""",
    
    "Theil-Sen Regressor": 
        """from sklearn.linear_model import TheilSenRegressor
model = TheilSenRegressor()""",
    
    "Quantile Regression": 
        """from sklearn.linear_model import QuantileRegressor
model = QuantileRegressor()""",
    
    "Kernel Ridge Regression": 
        """from sklearn.kernel_ridge import KernelRidge
model = KernelRidge()""",
    
    "Partial Least Squares Regression": 
        """from sklearn.cross_decomposition import PLSRegression
model = PLSRegression()""",
    
    "Passive-Aggressive Regressor": 
        """from sklearn.linear_model import PassiveAggressiveRegressor
model = PassiveAggressiveRegressor()""",
    
    "Gaussian Process Regressor": 
        """from sklearn.gaussian_process import GaussianProcessRegressor
model = GaussianProcessRegressor()""",
    
    "Histogram-based Gradient Boosting Regressor": 
        """from sklearn.ensemble import HistGradientBoostingRegressor
model = HistGradientBoostingRegressor()""",
    
    "Isotonic Regression": 
        """from sklearn.isotonic import IsotonicRegression
model = IsotonicRegression()"""
}

train_code = "model.fit(X_train, y_train)"

async def trainer_node(state):
    """
    Check code

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, error
    """

    print("---CHECKING CODE---")
    print(f"=======================================\nthis is the state in trainer:{state}\n====================================")
    # State
    if "models_completed" not in state:
        state["models_completed"] = 0
    #messages = state["messages"]
    mode = state["mode"]
    #models_selected = state["models_selected"]
    problem_type = state["problem_type"]
    X_train = state["X_train"]
    y_train = state["y_train"]
    project_id = state["project_id"]
    models_completed = state["models_completed"]

#splitting and preprocessing logic:
#----------------------------------
    df= await projectRequests.get_dataset(project_id)
    Xpreprocessing_pipeline=projectRequests.get_X_pipeline(project_id)
    Ypreprocessing_pipeline=projectRequests.get_Y_pipeline(project_id)
    
    numerical_cols = X_train.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = X_train.select_dtypes(include=['object']).columns

    Xpreprocessing_pipeline.transformers = [t for t in Xpreprocessing_pipeline.transformers if t is not None]
    Ypreprocessing_pipeline.transformers = [t for t in Ypreprocessing_pipeline.transformers if t is not None]
    

    final_step=[('categorical_imputer', SimpleImputer(strategy='most_frequent'), categorical_cols),('numerical_imputer', SimpleImputer(strategy='median'), numerical_cols)]
    Xpreprocessing_pipeline.transformers.extend(final_step)

    print(f"=======================================\nthis is the Xpreprocessing_pipeline:{Xpreprocessing_pipeline.transformers}\n====================================")
    print(f"=======================================\nthis is the Ypreprocessing_pipeline:{Ypreprocessing_pipeline.transformers}\n====================================")

    X_train=Xpreprocessing_pipeline.fit_transform(X_train)
    y_train=Ypreprocessing_pipeline.fit_transform(y_train)

    feature_names = Xpreprocessing_pipeline.get_feature_names_out()
    X_processed = pd.DataFrame(X_processed, columns=feature_names)
    y_processed = pd.DataFrame(y_processed, columns=['y','row_id'])

    merged=X_processed.merge(y_processed, on='row_id',how='inner')
    X_train = merged.drop(columns=['row_id', 'y'])
    y_train = merged['y']
    
    globals_dict={'project_id':state['project_id'],
                    'df':df,
                    'X_train':X_train,
                    'y_train':y_train,
                    }

# modelling logic:
#-----------------
    import_block = ""
    if mode == "HERMES" and models_completed < 1:
        if problem_type == "classification":
            if model in classification_import_block:
                import_block = classification_import_block[model]
                
        elif problem_type == "regression":
            if model in regression_import_block:
                import_block = regression_import_block[model]
        model = train_code

    elif mode == "ATHENA" and models_completed < 3:
        if problem_type == "classification":
            if model in classification_import_block:
                import_block = classification_import_block[model]
        elif problem_type == "regression":
            if model in regression_import_block:
                import_block = regression_import_block[model]
        model = train_code
    
    elif mode == "HEPHAESTUS" and models_completed < 5:
        if problem_type == "classification":
            if model in classification_import_block:
                import_block = classification_import_block[model]
        elif problem_type == "regression":
            if model in regression_import_block:
                import_block = regression_import_block[model]
        model = train_code
                    
    exec(import_block, globals_dict)
    exec(model, globals_dict)

    model=globals_dict['model']
    projectRequests.save_X_pipeline(Xpreprocessing_pipeline,project_id)
    projectRequests.save_Y_pipeline(Ypreprocessing_pipeline,project_id)
    projectRequests.save_model(project_id, model,state['model'][models_completed]['model'])
    print("---MODEL SAVED SUCCESSFULLY---")

    return {
        "iterations": 0,
        "error": "no",
        'models_completed':models_completed+1
    }