from typing import List
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Literal
from langchain import hub
from langchain_core.tools import tool,InjectedToolArg
from typing_extensions import Annotated,Optional

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
    "Isotonic Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.isotonic.IsotonicRegression.html",
    "Linear Regression": "https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html"
}


class ModelRecommendation(BaseModel):
    """Individual model recommendation structure"""
    model: str = Field(description="Full name of the recommended ML model as given to you")
    reasoning: str = Field(description="Explanation for selecting this model")


class Selector(BaseModel):
    """Main structured output model"""
    models: List[ModelRecommendation] = Field(description="List of recommended models with explanations")

@tool
async def model_selector_node(state: Annotated[dict, InjectedToolArg] = None,
                            number_of_models: Annotated[int, "Number of models to be selected"] = 3,):
                            # task: Optional[Annotated[str, "This is the task that the supervisor node should assign or give. It is completely optional, You can write what are your preferences or comments"]] = None
    """This agent is responsible for selecting the best model for the given data and problem type. It will use the provided data report and other information to make its recommendations.
    The agent will also provide reasoning for its choices, and it will be able to handle both classification and regression tasks. The agent will return a list of recommended models along with their reasoning and reference URLs."""
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
    X_preprocessing_logic = state.get('X_preprocessing_logic', None)
    Y_preprocessing_logic = state.get('Y_preprocessing_logic', None)
    model_list = list(classification_docs.keys()) if problem_type == 'classification' else list(regression_docs.keys())
    messages = [{"role": "system","content": system_prompt}]+state.get('model_selection_messages', [])
    content=""
    if state.get('evaluation_metrics', None):
        content+=f"Here are the evaluation metrics for your previous steps: {state['evaluation_metrics']}\n\n Attempt to Analyze and Improve, if possible, if not return the same values.\n\n"
    # if task:
    #     content+=f"Here are the instructions for you given by the supervisor: {task}\n\n"
    content+=f"""\n
    Problem Type: {problem_type}
    this is the model list: {model_list}\n 
    this is the data report:{data_report}\n
    this is the X columns: {X_columns}\n And this is the y column: {y_column}\n
    This is the preprocessing steps that were applied for the X_columns: {X_preprocessing_logic if X_preprocessing_logic else 'No preprocessing was applied for the X_columns'}\n"""
    if state.get('Y_preprocessing_logic', None):
        content+=f"This is the preprocessing steps that were applied for the y_column: {Y_preprocessing_logic if Y_preprocessing_logic else 'No preprocessing was applied for the y_column'}\n"
    content+=f"Please provide recommendations strictly following the format requirements. Give me the best {number_of_models} models for the given data and problem type."
    
    messages.append({"role": "user", "content": content})

    response = await llm.with_structured_output(Selector).ainvoke(messages)
    models_response=[]
    old_model_dict=state.get('models',{})
    for model in response.models:
        if model.model in old_model_dict:
            old_model_dict[model.model]['reasoning']=model.reasoning
        else:
            old_model_dict[model.model] = {
                "reasoning": model.reasoning,
                'reference_url': classification_docs[model.model] if problem_type == 'classification' else regression_docs[model.model]
            }

        models_response.append({
            model.model: {
                "reasoning": model.reasoning,
                'reference_url': classification_docs[model.model] if problem_type == 'classification' else regression_docs[model.model]
            }
        })

    completed=state.get('completed',{})
    completed['model_selector']=True
    new_state={
        "models": old_model_dict,
        'model_selection_messages': messages[1:]+[{"role": "assistant", "content": f"Here is the output: {response.model_dump_json()}"}],
        'completed':completed
    }

    return [f'The model selection is done, here are the models selected {[list(model.keys())[0] for model in models_response]}', new_state]