import numpy as np
from scipy.stats import entropy
import pandas as pd
import pymannkendall as mk

from Agents.insightGeneration.QUGEN.prompts import InsightCard

def score_trend(values):
    """ Calculates the trend score using the Mann-Kendall Trend Test. """
    if len(values) < 2:
        return 0 
    p_value = mk.original_test(values).p
    return 1 - p_value if p_value < 0.05 else 0

def score_outstanding_value(Card :InsightCard):
    """ Calculates the outstanding value score as vmax1 / vmax2. """
    Outstanding_df = Card.resulted_df
    aggregated_Col = Outstanding_df.columns.to_list()[1]
    Outstanding_df.sort_values(by=aggregated_Col, ascending= True if Card.aggregation=="MIN" else False)
    Best_2_Values=Outstanding_df.iloc[0:2,1].values
    Best_2_Values = np.abs(Best_2_Values.astype(np.float64))
    return Best_2_Values[0] / Best_2_Values[1] if Best_2_Values[1] != 0 else 0.0

def score_attribution(view: pd.DataFrame):
    """ Calculates the attribution score as max() / total. """
    #NOTE: ASK THE TEAM IF WE SHOULD CONSIDER ABSOLUTE VALUES OR NOT
    df = view.copy()
    column_name = df.columns[1]
    df[column_name] = df[column_name] / df[column_name].sum()
    return df.iloc[:,1].max()


# quantify how much a distribution has changed over time or between groups
def score_distribution_difference(vI, vF):  # initial and final views
    vI = np.asarray(vI, dtype=np.float64)
    vF = np.asarray(vF, dtype=np.float64)

    epsilon = 1e-10
    vI += epsilon
    vF += epsilon

    # asmt to normalize
    vI /= vI.sum()
    vF /= vF.sum()

    # avg

    M = 0.5 * (vI + vF)

    # Compute KL divergences (Kullback-Leibler )
    #  P and Q are identical fa = 0
    kl_p = entropy(vI, M)
    kl_q = entropy(vF, M)

    return 0.5 * (kl_p + kl_q)
