import networkx as nx
import numpy as np
import math

from scipy import stats

def compute_mean_confidence_interval(seir, alpha=0.05):
    mean = np.average(seir, axis=0)

    ci = np.zeros(mean.shape)

    for i in range(seir.shape[1]):
        for j in range(seir.shape[2]):
            for k in range(seir.shape[3]):
                theta = seir[:,i,j,k]
                n = len(theta)
                se = stats.sem(theta) / math.sqrt(n)
                if seir.shape[0] < 30:
                    ci[i,j,k] = se * stats.t.ppf((1 + (1-alpha)) / 2., n-1)
                else:
                    ci[i,j,k] = se * stats.norm.ppf(1-(alpha/2))

    return mean, ci
