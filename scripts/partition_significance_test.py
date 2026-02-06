"""Permutation test to assess whether the observed within-group homogeneity
is significantly smaller than expected by chance for groups of the same sizes.

By default tests the "gauge" group homogeneity (but can be changed via code).
"""

import json
import math
import os
import random
from statistics import mean, pstdev

ROOT = os.path.dirname(os.path.dirname(__file__))
ADJ_PATH = os.path.join(ROOT, "checks", "W33_adjacency_matrix.txt")
OUT_PATH = os.path.join(ROOT, "checks", "PART_CXI_group_adjacency.json")


def read_adj(path):
    mat = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            row = [int(x) for x in line.strip().split()]
            if row:
                mat.append(row)
    return mat


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def main(trials=5000, rng_seed=42):
    rnd = random.Random(rng_seed)
    adj = read_adj(ADJ_PATH)
    n = len(adj)
    assert n == 40

    # build normalized vecs per vertex (fractions)
    groups = json.load(open(OUT_PATH))["groups"]
    ordered_groups = ["fermions", "exotics", "e6_singlet", "gauge", "dark_matter"]

    # compute per-vertex normalized vector
    # need per_vertex counts
    per = json.load(open(OUT_PATH))["per_vertex_neighbor_counts"]
    vecs = {}
    for v in range(1, n + 1):
        p = per[f"V{v}"]
        vecs[v - 1] = [p[g] / 12.0 for g in ordered_groups]

    # observed within-group distance for gauge (and others)
    observed = {}
    for g, idxs in groups.items():
        idxs = idxs
        pairs = []
        for i in range(len(idxs)):
            for j in range(i + 1, len(idxs)):
                vi = idxs[i]
                vj = idxs[j]
                pairs.append(dist(vecs[vi], vecs[vj]))
        observed[g] = sum(pairs) / len(pairs) if pairs else 0.0

    vertices = list(range(n))

    results = {}
    for g, idxs in groups.items():
        size = len(idxs)
        if size <= 1:
            results[g] = {
                "observed": observed[g],
                "pval": None,
                "z": None,
                "mean_rand": None,
                "stdev_rand": None,
            }
            continue
        samples = []
        for t in range(trials):
            sample = rnd.sample(vertices, size)
            pairs = []
            for i in range(len(sample)):
                for j in range(i + 1, len(sample)):
                    vi = sample[i]
                    vj = sample[j]
                    pairs.append(dist(vecs[vi], vecs[vj]))
            val = sum(pairs) / len(pairs) if pairs else 0.0
            samples.append(val)
        mean_rand = mean(samples)
        stdev_rand = pstdev(samples)
        pval = sum(1 for x in samples if x <= observed[g]) / trials
        z = (observed[g] - mean_rand) / stdev_rand if stdev_rand > 0 else None
        results[g] = {
            "observed": observed[g],
            "pval": pval,
            "z": z,
            "mean_rand": mean_rand,
            "stdev_rand": stdev_rand,
        }

    # Print
    for g, res in results.items():
        if res["pval"] is None:
            print(f"Group {g}: size=1, observed={res['observed']:.4f}")
        else:
            print(
                f"Group {g}: observed={res['observed']:.4f}, mean_rand={res['mean_rand']:.4f}, stdev={res['stdev_rand']:.4f}, p={res['pval']:.4f}, z={res['z']:.3f}"
            )

    # Also print human-readable summary for gauge specifically
    g = "gauge"
    print("\nGauge summary:")
    print(f"Observed gauge within-group distance: {results[g]['observed']:.4f}")
    print(
        f"Random mean: {results[g]['mean_rand']:.4f}, stdev: {results[g]['stdev_rand']:.4f}"
    )
    print(f"p-value (<= observed): {results[g]['pval']:.4f} over {trials} trials")
    print(f"z-score: {results[g]['z']:.3f}")


if __name__ == "__main__":
    main(trials=5000)
