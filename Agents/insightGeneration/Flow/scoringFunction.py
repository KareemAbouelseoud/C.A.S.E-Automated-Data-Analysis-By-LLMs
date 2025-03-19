import numpy as np
from scipy.stats import entropy
import numpy as np
import pymannkendall as mk


def score_trend(values):
    """ Calculates the trend score using the Mann-Kendall Trend Test. """
    if len(values) < 2:
        return 0 
    p_value = mk.original_test(values).p
    return 1 - p_value if p_value < 0.05 else 0

def score_outstanding_value(values):
    """ Calculates the outstanding value score as vmax1 / vmax2. """
    abs_values = np.abs(values)
    sorted_values = np.sort(abs_values)[::-1]
    if len(sorted_values) < 2 or sorted_values[1] == 0:
        return 0  
    return sorted_values[0] / sorted_values[1] if sorted_values[0] / sorted_values[1] >= 1.4 else 0


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
