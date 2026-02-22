#!/usr/bin/env python3
"""Compute the number of triangles that satisfy the cocycle condition for a bijection."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from e8_embedding_group_theoretic import build_w33
from optimize_bijection_cocycle import build_triangles, triangle_exact
from w33_e8_bijection import generate_e8_roots


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bij", required=True)
    args = parser.parse_args()

    j = json.loads(Path(args.bij).read_text(encoding="utf-8"))
    bij = {int(k): int(v) for k, v in j["bijection"].items()}

    n, vertices, adj, edges = build_w33()
    roots = generate_e8_roots()
    tri_list = build_triangles(n, adj)

    exact = sum(1 for t in tri_list if triangle_exact(roots, bij, edges, t))
    print("exact triangles:", exact)


if __name__ == "__main__":
    main()
