import os
import pandas as pd
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI  # Ensure you have this
import google.generativeai as genai # New
import google.ai.generativelanguage as glm
from sentence_transformers import SentenceTransformer
from scipy.stats import kendalltau, kruskal
from langchain.prompts import PromptTemplate #New

#Install with: pip install -U google-generativeai
# Set up your Gemini API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"  # Or load from a config file
genai.configure(api_key=os.environ["GOOGLE_API_KEY"]) # New

MODEL_NAME = "gemini-1.5-flash-001" # New
# Gemini LLM Setup
llm = ChatGoogleGenerativeAI(model_name=MODEL_NAME, temperature=0.0)
model = genai.GenerativeModel(MODEL_NAME)

# Sentence Transformer for semantic similarity:
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


# --- QUGEN (Question Generation) Functions ---
def generate_questions(data, previous_questions=None, num_questions=3):
    """Generates questions, breakdown, measure, and reason using Gemini."""
    schema = "\n".join([f"{col} ({data[col].dtype})" for col in data.columns])
    if previous_questions is None:
        few_shot_examples = ""
    else:
        few_shot_examples = "\n".join(previous_questions)

    prompt = f"""You are a data analysis expert tasked with asking questions to get insights from a dataset.
The following is the schema of the dataset:
{schema}

Your job is to output questions about the data, breakdown and measure dimensions to analyze the answers, and a reason for asking. Be creative and insightful. Focus on relationships, trends and anomalies.
Format your output as a list of these examples: 
Question: <question>, 
Breakdown: <breakdown dimension>, 
Measure: <aggregation function>(<measure column>),
Reason: <reason for asking>
Here are a few shot examples:
{few_shot_examples}

Give me {num_questions} unique questions about this data, and explain why the measures and breakdowns can give good insights."""

    try:
        # Using Langchain LLMChain for question generation
        template = prompt
        llm_chain = PromptTemplate.from_template(template)
        response = llm.invoke(llm_chain.format())

        return response.split("\n")  # Split into questions
    except Exception as e:
        print(f"Question generation error: {e}")
        return []


def filter_questions(data, questions):
    """Filters questions to remove duplicates and irrelevant questions."""
    filtered_questions = []
    question_embeddings = [semantic_model.encode(q) for q in questions]

    for i, question in enumerate(questions):
        is_duplicate = False
        for j, existing_question in enumerate(filtered_questions):
            existing_embedding = question_embeddings[j]
            similarity = np.dot(question_embeddings[i], existing_embedding) / (
                        np.linalg.norm(question_embeddings[i]) * np.linalg.norm(existing_embedding))  # cosine similarity

            if similarity > 0.8:  # Threshold for duplicate questions
                is_duplicate = True
                break
        if not is_duplicate and is_semantically_relevant(data, question):
            filtered_questions.append(question)
    return filtered_questions


def is_semantically_relevant(data, question):
    """Very basic check, expand as needed. Make sure that columns are not simple descriptive stats (e.g. only one value)"""
    for col in data.columns:
        # Check if the column is in the question, avoid if only has one value:
        if col in question and len(data[col].unique()) <= 1:
            return False
    return True


# --- ISGEN (Insight Generation) Functions ---
def extract_components(question_str):
    """Extracts the components from a question string."""
    try:
        parts = question_str.split(", ")
        question = parts[0].split(": ")[1]
        breakdown = parts[1].split(": ")[1]
        measure_str = parts[2].split(": ")[1]  # e.g., "mean(Sales)"
        reason = parts[3].split(": ")[1]

        # Extract measure aggregation function and column:
        measure_agg = measure_str.split("(")[0]  # e.g., mean
        measure_col = measure_str[len(measure_agg) + 1:-1]  # e.g., Sales

        return question, breakdown, measure_agg, measure_col, reason
    except Exception as e:
        print(f"Problem extracting insight components: {e}")
        return None, None, None, None, None

def EXPAND(S, D, B, M):
    """Expands a subspace S by adding a filter using LLM guidance."""
    avlbl_cols = [col for col in D.columns if col not in S["used_cols"]]

    # Prompt LLM to suggest relevant column
    prompt = f"""Given the dataset with breakdown '{B}' and measure '{M}',
    suggest a column from the following available columns: {avlbl_cols} that can be used as filter"""

    try:
        #Using LangChain LLMChain to get the column suggestion
        template = prompt
        prompt_template = PromptTemplate.from_template(template)
        response = llm.invoke(prompt_template.format())

        suggested_col = response.strip()  # clean up
        if suggested_col not in avlbl_cols: #if suggested col isn't valid choose something else
            X = np.random.choice(avlbl_cols)
        else:
            X = suggested_col #Otherwise choose the suggested column
    except Exception as e:
        print(f"Column suggestion error: {e}")
        X = np.random.choice(avlbl_cols) #Default back to a random selection

    # Sample value of selected column:
    try:
        y = D[X].sample().iloc[0]
        new_filter = (X,y)

        S["filters"].append(new_filter)
        S["used_cols"].append(X)
    except ValueError as e:
        print(f"Problem with probabilities in EXPAND. Check if your columns have more than one value. Error: {e}")
        return S #return the old S

    return S

def apply_filters(D, filters):
    """Applies a list of filters to a DataFrame"""
    Ds = D.copy()
    for col, val in filters:
        Ds = Ds[Ds[col] == val]
    return Ds


def score_trend(subspace_data, B, M):
    """Scores how well a trend pattern exists in the subspace, using the data."""
    try:
        # Handle cases where B is categorical and M is numerical: convert to numeric, encode categories to numbers:
        if not pd.api.types.is_numeric_dtype(subspace_data[B]):
            if len(subspace_data[B].unique()) <= 2:
                subspace_data[B] = subspace_data[B].astype('category').cat.codes  #Binary category
            else:
                return 0  # Not applicable

        # Calculate Kendall's Tau correlation (Non-parametric for trends)
        correlation, p_value = kendalltau(subspace_data[B], subspace_data[M])  # kendalltau already has a p-value.

        if p_value > 0.05:
            return 0  # no significant statistical correlation

        return abs(correlation)  # Take absolute value
    except Exception as e:
        print(f"Trend score calculation error: {e}")
        return 0  # Return a score of 0 if there's an error


def score_outstanding_value(subspace_data, M):
    """Scores for outlier detection, return 0 if not applicable"""
    try:
        if len(subspace_data[M]) == 0:
            return 0  # Avoid divide by zero
        max_val = subspace_data[M].max()
        second_max = subspace_data[M][subspace_data[M] != max_val].max()  # Second max
        if second_max == 0:  # to avoid divide by zero
            return 0
        return max_val / second_max

    except Exception as e:
        print(f"Outlier score calculation error: {e}")
        return 0


def score_attribution(subspace_data, M):
    """Scores attribution as a percentage of the total"""
    try:

        max_val = subspace_data[M].max()  # Maximum value in M column
        total_sum = subspace_data[M].sum()  # Get the sum total
        if total_sum == 0:
            return 0  # Avoid divide by zero

        return max_val / total_sum
    except Exception as e:
        print(f"Attribution score calculation error: {e}")
        return 0


def score_distribution_difference(subspace_data, M, B):
    """Scores the change in distribution, need B, M to work"""
    try:
        if not pd.api.types.is_numeric_dtype(subspace_data[M]):
            return 0  # Not applicable

        contingency_table = pd.crosstab(subspace_data[B],
                                         subspace_data[M])  # crosstab computes a simple cross tabulation of two (or more) factors.

        if contingency_table.size < 2:
            return 0  # Check to see if the contingency table is valid

        stat, p, dof, expected = kruskal(*[contingency_table[col].values for col in contingency_table])
        # Reject the null hypothesis if P < 0.05
        if p < 0.05:
            return stat  # Stat will be returned if it is < 0.05
        else:
            return 0  # Return score of zero if P > 0.05

    except Exception as e:
        print(f"Distribution difference score calculation error: {e}")
        return 0


def generate_insight_description(subspace, score, B, M, pattern, data):
    """Generates a description, and the filters and type"""
    Ds = apply_filters(data, subspace["filters"])  # Apply filters to the data
    if len(Ds) == 0:
        return "No data after filtering."
    description = f"Applying these filters: {subspace['filters']}, to {B} and {M}, on this {pattern} yields a score of {score:.2f}."
    return description

def subspace_search(data, question, breakdown, measure_agg, measure_col, beam_width=3, max_depth=2, exp_factor=2):
    """Beam Search, modified for scoring functions."""

    # Initialize
    So = {"filters": [], "used_cols": []}
    beam = [(So, 0)]  # Starting score is 0

    for depth in range(1, max_depth + 1):
        new_beam = []
        for S, score in beam:
            for i in range(exp_factor):
                Snew = EXPAND(S.copy(), data, breakdown, measure_col)
                Ds = apply_filters(data, Snew["filters"])

                # Select and score: try each scoring function and pick the highest score and pattern:
                trend_score = score_trend(Ds, breakdown, measure_col)
                outlier_score = score_outstanding_value(Ds, measure_col)
                attribution_score = score_attribution(Ds, measure_col)
                distribution_score = score_distribution_difference(Ds, breakdown, measure_col)  # distribution diff

                scores = {
                    "trend": trend_score,
                    "outstanding_value": outlier_score,
                    "attribution": attribution_score,
                    "distribution_difference": distribution_score,
                }

                best_pattern = max(scores, key=scores.get)  # Find the pattern with the highest score
                best_score = scores[best_pattern]  # Get that score

                # Add the new data to the beam, alongside the score and the best fit:
                Snew["pattern"] = best_pattern  # store the type (trend, outlier, attibution, etc)
                new_beam.append((Snew, best_score))  # Save the new beam with the best attributes

        beam = sorted(new_beam, key=lambda x: x[1], reverse=True)[:beam_width]  # Truncate beam

    return beam


# --- Main Execution ---
# Load data (replace with your actual data loading)
try:
    data = pd.read_csv("your_dataset.csv")  # Replace with your file
except FileNotFoundError:
    print("Error: Dataset file not found.")
    exit()

#Basic Preprocessing:
# Drop any rows with missing values for simplicity
data = data.dropna()

# Initial questions
questions = generate_questions(data, num_questions=3)
filtered_questions = filter_questions(data, questions)

# Iterative Refinement of Questions and Insight Generation
all_questions = []
for i in range(2):  #Iterate 2 times
    print(f"\n--- Iteration {i+1} ---")
    top_insights = []
    for question_str in filtered_questions:
        question, breakdown, measure_agg, measure_col, reason = extract_components(question_str)
        if question:  # make sure that the question object has value
            print(f"Analyzing: {question}")
            top_subspaces = subspace_search(data, question, breakdown, measure_agg, measure_col)

            # Process top subspaces:
            for subspace, score in top_subspaces:  # add data points as argument
                pattern = subspace["pattern"]
                Ds = apply_filters(data, subspace["filters"])
                description = generate_insight_description(subspace, score, breakdown, measure_col, pattern, data)
                print(f"  Insight: {description}")

                top_insights.append((description, score, question_str))

    # Generate new questions using previous iterations (few-shot examples)
    new_questions = generate_questions(data, previous_questions=questions, num_questions=3)
    filtered_new_questions = filter_questions(data, new_questions)
    all_questions += questions
    questions = new_questions  # add new questions to existing examples