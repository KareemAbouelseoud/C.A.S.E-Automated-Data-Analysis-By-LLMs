import os
import pandas as pd
import numpy as np
import google.generativeai as genai  # New
import google.ai.generativelanguage as glm

from scipy.stats import kendalltau, kruskal
#pip install scipy
# Install with: pip install -U google-generativeai
# Set up your Gemini API Key (replace with your actual key)
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"  # Or load from a config file

MODEL_NAME = "gemini-1.5-flash-001"  # Choose your model
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
    """Expands a subspace S by adding a filter."""
    avlbl_cols = [col for col in D.columns if col not in S["used_cols"]]

    # Sample attribute and value:
    try:
        X = np.random.choice(avlbl_cols)  # <--- Pick a random attribute
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
