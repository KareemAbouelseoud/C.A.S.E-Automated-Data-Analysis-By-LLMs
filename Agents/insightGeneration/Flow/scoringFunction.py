import numpy as np
from scipy.stats import entropy


def score_attribution(values):
    if len(values) == 0:
        return 0.0
    total = sum(values)
    return max(values) / total if total != 0 else 0.0


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
