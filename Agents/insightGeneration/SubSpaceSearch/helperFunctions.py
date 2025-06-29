import copy
import pandas as pd
import numpy as np

from models import InsightCard
from .agent import run_advanced_insight_agent

def validate_dfs(full_view: pd.DataFrame, filtered_view: pd.DataFrame,card:InsightCard):
    full_view_values = set(full_view[card.breakdown])

    # Create missing rows in filtered_view for ports that exist in full_view but not in filtered_view
    missing_values = []
    for value in full_view_values:
        if value not in filtered_view[card.breakdown].values:
            missing_values.append({card.breakdown: value, f'{card.aggregation.lower()}_{card.measure}': 0})


    # Add missing ports to filtered_view if any exist
    if missing_values:
        filtered_view = pd.concat([filtered_view, pd.DataFrame(missing_values)], ignore_index=True)

    # Sort both views by Embarked to ensure they align
    full_view = full_view.sort_values(card.breakdown).reset_index(drop=True)
    filtered_view = filtered_view.sort_values(card.breakdown).reset_index(drop=True)
    
    return full_view,filtered_view

def EXPAND(Subspace, df:pd.DataFrame,card:InsightCard,desc:str):
    """
    Expands a given subspace by adding a new filter based on insights generated from the data.
    This function uses an advanced insight agent to suggest new insights, then probabilistically
    selects a new dimension and value to add as a filter to the subspace. The selection 
    probability is based on the log-frequency distribution of values in the chosen dimension.
    Parameters
    ----------
    Subspace : dict
        Current subspace definition containing 'filters' and 'used_cols' lists
    df : pandas.DataFrame
        The input dataset to analyze
    card : InsightCard
        Current insight card object containing analysis details
    desc : str
        Description string for generating insights
    Returns
    -------
    tuple
        A tuple containing:
        - dict: Updated subspace with new filter added (or original if expansion fails)
        - InsightCard: The sampled insight card used for expansion
    Notes
    -----
    The function uses log-frequency based probability distribution to select values,
    making it more likely to select less frequent values compared to raw frequencies.
    If the probability calculation fails (e.g., due to single-value columns),
    the function returns the original subspace without modification.
    """

    suggested_cards = run_advanced_insight_agent(card=card, df=df, desc=desc, subspace=Subspace)
    try:
        sampled_card = np.random.choice(suggested_cards.insight_cards)
        X=sampled_card.subSpace
        value_counts = df[X].value_counts()
        log_freq = np.log(1 + value_counts)
        prob_y = log_freq / log_freq.sum()
        y = np.random.choice(value_counts.index, p=prob_y)
        if isinstance(y, (np.int64, np.int32, np.int16, np.int8)):
            y= int(y)
        elif isinstance(y, (np.float64, np.float32, np.float16)):
            y= float(y)
            
        new_filter = (X,y)
        _subspace = copy.deepcopy(Subspace)
        _subspace["filters"].append(new_filter)
        _subspace["used_cols"].append(X)
    except ValueError as e:
        print(f"Problem with probabilities in EXPAND. Check if your columns have more than one value. Error: {e}")
        return Subspace,card #return the old _subspace
    return _subspace,sampled_card

def apply_filters(df:pd.DataFrame, filters):
    """Applies filters to a pandas DataFrame based on provided column-value pairs.
    This function takes a DataFrame and a list of filters (column-value pairs) and applies them
    to create filtered views of the data. It supports both numeric and non-numeric filtering.
    Args:
        df (pd.DataFrame): The input DataFrame to be filtered.
        filters (list of tuples): List of (column, value) tuples specifying the filter conditions.
            Each tuple contains:
                - column (str): Name of the column to filter on
                - value: Value to filter by
    Returns:
        tuple: Contains:
            - list[pd.DataFrame]: List of filtered DataFrames. Contains either:
                * Single DataFrame if no numeric splits occurred
                * Two DataFrames if numeric splits occurred (greater than and less than views)
            - bool: Flag indicating if multiple views were created (True if numeric splits occurred)
    Example:
        >>> df = pd.DataFrame({'A': [1,2,3], 'B': ['x','y','z']})
        >>> filters = [('A', 2), ('B', 'y')]
        >>> filtered_dfs, multiple_views = apply_filters(df, filters)
    """

    mask = pd.Series(True, index=df.index)
    multiple_Views = False
    filtered_dfs = []
    greater_mask = copy.deepcopy(mask)
    less_mask = copy.deepcopy(mask)
    # Here we considered that there will always be a mask where all filters with numeric values are greater than the value 
    # and one where all filters with numeric values are less than the value for simplicity
    # TODO: Manage the case of combinations of filters with numeric values and non-numeric values
    for col, val in filters:
        # if df[col].dtype.kind in "iufcmM" and df[col].unique().shape[0]> 10:
        #     # For numeric columns, apply a range filter supposing that a continous column needs at least 11 unique values
        #     # Create two masks for numeric columns
        #     greater_mask &= (df[col] >= val)
        #     less_mask &= (df[col] <= val)
        #     # Store original mask before splitting
        #     multiple_Views = True
            
        # else:
            # For non-numeric columns, apply regular equality filter
            mask &= (df[col] == val)
            greater_mask &= (df[col] == val)
            less_mask &= (df[col] == val)

    # If no numeric splits occurred, return single filtered dataframe
    if not multiple_Views:
        filtered_df = df[mask]
        # Append the filtered DataFrame to the list
        filtered_dfs.append(filtered_df)
        return filtered_dfs, multiple_Views
    else:
        # Create two filtered DataFrames based on the greater and less masks
        filtered_df_greater = df[greater_mask]
        filtered_df_less = df[less_mask]
        # Append both DataFrames to the list
        filtered_dfs.append(filtered_df_greater)
        filtered_dfs.append(filtered_df_less)
        # Return the list of DataFrames and the multiple_Views flag
        return filtered_dfs, multiple_Views
def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, tuple):  # Add tuple support
        return tuple(make_serializable(i) for i in obj)
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.datetime64, pd.Timestamp)):
        print("FOUND DATETIME")
        print(obj)
        return str(obj)
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj