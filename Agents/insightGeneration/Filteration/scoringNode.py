from io import StringIO
import numpy as np
from scipy.stats import entropy
import pandas as pd
import pymannkendall as mk
from models import InsightCard

def score_trend(view: pd.DataFrame):
    """ Calculates the trend score using the Mann-Kendall Trend Test. """
    values = view.iloc[:,1].values
    if len(values) < 2:
        return 0 
    try:
        p_value = mk.original_test(values).p
        return 1 - p_value if p_value < 0.05 else 0
    except Exception as e:
        print(f"Error calculating trend score: {e}")
        return 0

def score_outstanding_value(Card :InsightCard):
    """ Calculates the outstanding value score as vmax1 / vmax2. """
    if type(Card.resulted_df) == str:
        Outstanding_df = pd.read_json(StringIO(Card.resulted_df))
    else:
        Outstanding_df = Card.resulted_df
    
    try:
        aggregated_Col = Outstanding_df.columns.to_list()[1]
        Outstanding_df.sort_values(by=aggregated_Col, ascending= True if Card.aggregation=="MIN" else False)
        Best_2_Values=Outstanding_df.iloc[0:2,1].values
    except Exception as e:
        print(f"Error in getting Best 2 values: {e}")
        return 0
    if len(Best_2_Values) < 2:
        return 0
    try:
        Best_2_Values = np.abs(Best_2_Values.astype(np.float64))
    except Exception as e:
        print(f"Error converting to float: {e}")
        return 0
    return Best_2_Values[0] / Best_2_Values[1] if Best_2_Values[1] != 0 else 0.0

def score_attribution(view: pd.DataFrame):
    """ Calculates the attribution score as max() / total. """
    #NOTE: ASK THE TEAM IF WE SHOULD CONSIDER ABSOLUTE VALUES OR NOT
    try:
        df = view.copy()
        column_name = df.columns[1]
        df[column_name] = df[column_name] / df[column_name].sum()
    except Exception as e:
        print(f"Error in calculating attribution score: {e}")
        return 0
    try:
        return df.iloc[:,1].max() if float(df.iloc[:,1].max())!=1.0 else 0.0 #Cause if the .max equals 1, it means that the filters are so  much that it foucess on one value only, so it is not a good insight.
    except Exception as e:
        print(f"Error in calculating attribution score: {e}")
        return 0

# quantify how much a distribution has changed over time or between groups

def score_distribution_difference(vI:pd.DataFrame, vF:pd.DataFrame):  # initial and final views
    try:
        vI = np.asarray(vI, dtype=np.float64)
        vF = np.asarray(vF, dtype=np.float64)
    except Exception as e:
        print(f"Error converting to float: {e}")
        return 0

    epsilon = 1e-10
    vI += epsilon
    vF += epsilon

    # asmt to normalize
    try:
        vI /= vI.sum()
        vF /= vF.sum()
    except Exception as e:
        print(f"Error normalizing: {e}")
        return 0

    # avg

    M = 0.5 * (vI + vF)

    # Compute KL divergences (Kullback-Leibler )
    #  P and Q are identical fa = 0
    try:
        kl_p = entropy(vI, M)
        kl_q = entropy(vF, M)
    except Exception as e:
        print(f"Error calculating KL divergence: {e}")
        return 0

    return 0.5 * (kl_p + kl_q)

scoring_functions = {
            'attribution': score_attribution,
            'distribution_difference': score_distribution_difference,
            'trend': score_trend,
            'outstanding_value': score_outstanding_value
        }

def Score_card(card:InsightCard):
    """
    Calculates and assigns a score to an InsightCard object based on its insight type\n
    This function evaluates the significance of an insight by applying different scoring
    functions depending on the insight type (attribution, trend, or outstanding_value).
    The score is then stored in the InsightCard object.

    Parameters
    ----------
    card : InsightCard
        An InsightCard object containing the insight data and metadata
    Returns
    -------
    InsightCard
        The input card object with updated score and considered status
    Notes
    -----
    - For attribution insights, card is marked as 'Considered' if score >= 0.5
    - For outstanding_value insights, card is marked as 'Considered' if score >= 1.4
    - Scoring is only performed if the resulted_df in the card is not empty
    - For trend and outstanding_value types, assumes resulted_df has at least one column
    """
    
    score = 0.0
    insight_type = card.insight_type

    # Access resulted_df from the InsightCard object
    if type(card.resulted_df) == str:
        card_resulted_df = pd.read_json(StringIO(card.resulted_df))
    else:
        card_resulted_df = card.resulted_df
    if not card_resulted_df.empty:
        if insight_type == 'Attribution':
            score = scoring_functions['attribution'](card_resulted_df)
            if score >= 0.5:
                card.Considered = True
    
        elif insight_type == 'Trend':
            # Assuming resulted_df has values in a single column or series
            if len(card_resulted_df.columns) > 0:
                score = scoring_functions['trend'](card_resulted_df)
                if score >= 0.5:
                    card.Considered = True

        elif insight_type == 'Outstanding Value':
            # Assuming resulted_df has values in a single column or series
            if len(card_resulted_df.columns) > 1:
                score = scoring_functions['outstanding_value'](card)
                if score >= 1.4:
                    card.Considered = True

    # Create new dict with score added
    if score == np.nan or score == None or score == np.inf or score == -np.inf:
        score = 0.0

    card.Score = float(score)
    return card