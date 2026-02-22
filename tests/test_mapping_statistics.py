import json
import numpy as np
from collections import defaultdict

def build_W33():
    from itertools import product
    def omega(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3
    def normalize(v):
        for i, x in enumerate(v):
            if x != 0:
                inv = pow(x, -1, 3)
                return tuple((inv * c) % 3 for c in v)
        return v
    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]
    vertices = list({normalize(p) for p in points})
    edges = []
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
    return vertices, edges


vertices, edges = build_W33()
with open("data/w33_e8_mapping.json") as f:
    mapping = json.load(f)

map_arr = [mapping[str(i)] for i in range(len(edges))]

# build E8 roots
roots = []
for i in range(8):
    for j in range(i + 1, 8):
        for si in [1, -1]:
            for sj in [1, -1]:
                r = [0] * 8
                r[i] = si
                r[j] = sj
                roots.append(tuple(r))
from itertools import product as _prod
for signs in _prod([0.5, -0.5], repeat=8):
    if sum(1 for s in signs if s < 0) % 2 == 0:
        roots.append(tuple(signs))

int_type = {i for i, r in enumerate(roots) if all(float(c).is_integer() for c in r)}
half_type = set(range(len(roots))) - int_type


def lift(v):
    return tuple(c if c <= 1 else c - 3 for c in v)

diff_norms = [sum((lift(vertices[e[0]])[k] - lift(vertices[e[1]])[k]) ** 2 for k in range(4)) for e in edges]


def test_mapping_length():
    assert len(map_arr) == len(edges) == 240


def test_integer_half_distribution():
    counts_int = sum(1 for r in map_arr if r in int_type)
    counts_half = len(map_arr) - counts_int
    # should roughly be half-half
    assert abs(counts_int - counts_half) < 50


def test_diff_norm_stats():
    int_norms = [d for d, r in zip(diff_norms, map_arr) if r in int_type]
    half_norms = [d for d, r in zip(diff_norms, map_arr) if r in half_type]
    # average int_norm should be less than average half_norm
    assert np.mean(int_norms) < np.mean(half_norms)
