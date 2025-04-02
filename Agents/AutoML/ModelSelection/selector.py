from typing import List
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

system_prompt = hub.pull("automl-model-selection-planner").messages[0].prompt.template
CONFIGURATIONS={
    'temperature':0.7,
    'model':"gemini-2.0-flash",
}

classification_docs = {
    "Logistic Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html",
    "Stochastic Gradient Descent (SGD) Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html",
    "Gaussian Naive Bayes": "https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html",
    "Multinomial Naive Bayes": "https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html",
    "Bernoulli Naive Bayes": "https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.BernoulliNB.html",
    "K-Nearest Neighbors (KNN) Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html",
    "Decision Tree Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html",
    "Random Forest Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html",
    "Gradient Boosting Classifier (GBM)": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html",
    "Extreme Gradient Boosting (XGBoost) Classifier": "https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBClassifier",
    "Categorical Boosting (CatBoost) Classifier": "https://catboost.ai/en/docs/concepts/python-reference_catboostclassifier",
    "Support Vector Machine (SVM) Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html",
    "Multi-layer Perceptron (MLP) Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html",
    "AdaBoost Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html",
    "Extra Trees Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html",
    "Linear Discriminant Analysis (LDA)": "https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html",
    "Quadratic Discriminant Analysis (QDA)": "https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis.html",
    "Gaussian Process Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessClassifier.html",
    "Histogram-based Gradient Boosting Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingClassifier.html",
    "Bagging Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.BaggingClassifier.html",
    "Ridge Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RidgeClassifier.html",
    "Passive-Aggressive Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PassiveAggressiveClassifier.html",
    "Quadratic Support Vector Classifier (QSVC)": "https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html",
    "Nearest Centroid Classifier": "https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestCentroid.html",
    "Dummy Classifier (Stratified)": "https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html"
}


regression_docs = {
    "Ordinary Least Squares (OLS) Linear Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html",
    "Ridge Regression (L2 Regularization)": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html",
    "Lasso Regression (L1 Regularization)": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html",
    "ElasticNet Regression (L1+L2)": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html",
    "Stochastic Gradient Descent (SGD) Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDRegressor.html",
    "Decision Tree Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html",
    "Random Forest Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html",
    "Gradient Boosting Regressor (GBR)": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html",
    "Extreme Gradient Boosting (XGBoost) Regressor": "https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor",
    "Categorical Boosting (CatBoost) Regressor": "https://catboost.ai/en/docs/concepts/python-reference_catboostregressor",
    "Support Vector Regression (SVR)": "https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html",
    "Multi-layer Perceptron (MLP) Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html",
    "AdaBoost Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostRegressor.html",
    "Extra Trees Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesRegressor.html",
    "Bayesian Ridge Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.BayesianRidge.html",
    "Huber Regressor (Robust Regression)": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.HuberRegressor.html",
    "Theil-Sen Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.TheilSenRegressor.html",
    "Quantile Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.QuantileRegressor.html",
    "Kernel Ridge Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.kernel_ridge.KernelRidge.html",
    "Partial Least Squares Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.cross_decomposition.PLSRegression.html",
    "Passive-Aggressive Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PassiveAggressiveRegressor.html",
    "Gaussian Process Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.GaussianProcessRegressor.html",
    "Histogram-based Gradient Boosting Regressor": "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html",
    "Isotonic Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.isotonic.IsotonicRegression.html"
}


class ModelRecommendation(BaseModel):
    """Individual model recommendation structure"""
    model: str = Field(description="Full name of the recommended ML model as given to you")
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

    data_report = state['data_report']
    problem_type = state['problem_type']
    X_columns = state['X_columns']
    y_column = state['y_column']
    mode = state['mode']
    
    model_list = list(classification_docs.keys()) if problem_type == 'classification' else list(regression_docs.keys()
)
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
                f"This is the preprocessing steps that are going to be applied for the X_columns: {state['X_preprocessing_logic']}\n"
                f"This is the preprocessing steps that are going to be applied for the y_column: {state['Y_preprocessing_logic']}\n"
                "Please provide recommendations strictly following the format requirements."
        }
    ]
    response = await llm.with_structured_output(Selector).ainvoke(messages)
    

    return {
        "models": [
            {"model": rec.model, "reasoning": rec.reasoning, 'reference_url': classification_docs[rec.model] if problem_type == 'classification' else regression_docs[rec.model]}
            for rec in response.models
        ]
    }


async def brancher(state) -> Literal["model_trainer_node", "model_tuner_node"]:
    """Determine workflow continuation based on state validation"""
    if state['mode']=='HERMES':
        return "model_trainer_node"
    else:
        return "model_tuner_node"