#!/usr/bin/env python3
from collections import Counter

import numpy as np

A = np.loadtxt("checks/W33_adjacency_matrix.txt", dtype=int)
neighbors = [tuple(sorted(list(np.nonzero(A[i])[0]))) for i in range(A.shape[0])]
cnt = Counter(neighbors)
print("Distinct neighbor-signatures:", len(cnt))
for k, v in cnt.most_common():
    print("count", v, "len_nb", len(k), "first6", k[:6])

# Also show how many vertices share each signature length
lens = Counter(len(k) for k in cnt.keys())
print(
    "neighbor-set lengths distribution (signature groups):", dict(sorted(lens.items()))
)
