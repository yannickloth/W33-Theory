#!/usr/bin/env python3
"""Visualize the tomotope doubled-K4 incidence kernel (8 modes) and image (4 modes).

Generates PNGs into `docs/images/`.
"""
from __future__ import annotations

import itertools
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def build_doubled_k4_incidence():
    edges = list(itertools.combinations(range(4), 2))
    rows = []
    for i, j in edges:
        row = [0, 0, 0, 0]
        row[i] = 1
        row[j] = 1
        rows.append(row)
        rows.append(row[:])
    return np.array(rows, dtype=float)


def main():
    out_dir = Path("docs") / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    M = build_doubled_k4_incidence()
    U, s, Vt = np.linalg.svd(M, full_matrices=True)

    rank = np.linalg.matrix_rank(M)
    left_null = U[:, rank:]
    image_modes = Vt.T[:, :rank]

    # Save kernel mode heatmap (8 x 12)
    for i in range(left_null.shape[1]):
        vec = left_null[:, i]
        plt.figure(figsize=(6, 1))
        plt.bar(range(len(vec)), vec)
        plt.title(f"Tomotope kernel mode {i+1}")
        plt.tight_layout()
        plt.savefig(out_dir / f"tomotope_kernel_mode_{i+1}.png")
        plt.close()

    # Save image modes (4)
    for i in range(image_modes.shape[1]):
        vec = image_modes[:, i]
        plt.figure(figsize=(6, 1))
        plt.bar(range(len(vec)), vec)
        plt.title(f"Tomotope image mode {i+1}")
        plt.tight_layout()
        plt.savefig(out_dir / f"tomotope_image_mode_{i+1}.png")
        plt.close()

    print(f"Wrote tomotope mode plots to {out_dir}")


if __name__ == "__main__":
    main()
