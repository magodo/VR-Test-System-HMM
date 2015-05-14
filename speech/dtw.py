# -*- coding: utf8 -*-
# This file includes routines to compute DTW distance between two vectors.
# Author: Zhaoting Weng 2014

import numpy as np

def dtw(r, t):
    """Calculate similarities between two non-indentical length series(But each frame vector has same size).

    :param r: Reference template.
    :param t: Test template.
    :returns: Similarity score.
    """
    r = np.array(r)
    t = np.array(t)
    # Prepend a dimension in reference template and test template for convenience
    zeros = np.expand_dims(np.zeros(r.shape[1]), 0)
    r = np.concatenate([zeros, r])
    t = np.concatenate([zeros, t])
    # Initiate distance matrix.
    x = r.shape[0]
    y = t.shape[0]
    dist_matrix = np.zeros((x, y))
    dist_matrix[:, 0] = np.Inf
    dist_matrix[0, :] = np.Inf
    dist_matrix[0, 0] = 0
    # Calculation
    for i in range(1, x):
        for j in range(1, y):
            cost = dist(r[i], t[j])
            dist_matrix[i, j] = cost + min(dist_matrix[i-1, j], dist_matrix[i, j-1], dist_matrix[i-1, j-1])
    #print dist_matrix
    return dist_matrix[x-1, y-1]

def dist(a, b):
    """Calculate distance between two same size vectors.

    :param a: Numpy array.
    :param b: Numpy array.
    :returns: Distance with double type.
    """
    # Check if the two vectors have same length.
    if a.size != b.size:
        raise ValueError("Vectors are not same sized.")
    return np.power(a - b, 2).sum()

if __name__ == "__main__":
    r = [[1,2],[3,4],[1,2], [7,2], [12, 6]]
    t = [[4,3],[1,2], [2,5], [6,2]]
    print dtw(r,t)

