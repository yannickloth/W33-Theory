"""Simple k-means clustering on normalized neighbor-vectors to see if natural
clusters match the proposed particle-group partition.

Outputs a brief summary to stdout and writes checks/PART_CXI_clustering.json.
"""

import json
import os
import random
from collections import Counter

import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
IN_PATH = os.path.join(ROOT, "checks", "PART_CXI_group_adjacency.json")
OUT_PATH = os.path.join(ROOT, "checks", "PART_CXI_clustering.json")


def kmeans(X, k, n_iter=200, rng=None):
    n, d = X.shape
    if rng is None:
        rng = np.random.default_rng()
    # init centroids as random samples
    idx = rng.choice(n, size=k, replace=False)
    centroids = X[idx].astype(float)
    labels = np.zeros(n, dtype=int)
    for it in range(n_iter):
        # assign
        dists = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        # update
        for j in range(k):
            members = X[labels == j]
            if len(members) > 0:
                centroids[j] = members.mean(axis=0)
            else:
                # reinit empty centroid
                centroids[j] = X[rng.choice(n)]
    inertia = np.sum(
        np.min(
            np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2) ** 2, axis=1
        )
    )
    return labels, centroids, inertia


def purity_score(labels, groups):
    # groups: dict label->list of indices
    n = len(labels)
    k = len(set(labels))
    # build cluster->group counts
    cluster_groups = {}
    for i, cl in enumerate(labels):
        cluster_groups.setdefault(cl, []).append(i)
    total = 0
    for cl, members in cluster_groups.items():
        # count group membership for members
        counts = Counter()
        for m in members:
            for g, idxs in groups.items():
                if m in idxs:
                    counts[g] += 1
                    break
        total += counts.most_common(1)[0][1]
    return total / n


def main():
    data = json.load(open(IN_PATH))
    groups = data["groups"]
    per = data["per_vertex_neighbor_counts"]
    ordered_groups = ["fermions", "exotics", "e6_singlet", "gauge", "dark_matter"]

    X = []
    for v in range(1, 41):
        p = per[f"V{v}"]
        vec = [p[g] / 12.0 for g in ordered_groups]
        X.append(vec)
    X = np.array(X)

    rng = np.random.default_rng(12345)
    results = {}
    for k in range(3, 7):
        best = None
        best_inertia = float("inf")
        best_labels = None
        for _ in range(20):
            labels, centroids, inertia = kmeans(X, k, n_iter=200, rng=rng)
            if inertia < best_inertia:
                best_inertia = inertia
                best_labels = labels.copy()
        purity = purity_score(best_labels, groups)
        # contingency
        conting = {}
        for cl in set(best_labels):
            conting[cl] = Counter()
            for i, lab in enumerate(best_labels):
                if lab == cl:
                    for g, idxs in groups.items():
                        if i in idxs:
                            conting[cl][g] += 1
                            break
        results[k] = {
            "inertia": float(best_inertia),
            "purity": float(purity),
            "contingency": {str(k): dict(v) for k, v in conting.items()},
        }

    from utils.json_safe import dump_json

    dump_json(results, OUT_PATH, indent=2)

    for k, res in results.items():
        print(f"k={k}: inertia={res['inertia']:.3f}, purity={res['purity']:.3f}")
        print(" contingency:")
        for cl, cnt in res["contingency"].items():
            print("  - cluster", cl, cnt)
        print()


if __name__ == "__main__":
    main()
