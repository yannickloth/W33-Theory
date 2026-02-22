#!/usr/bin/env python3
"""
Self-duality check: the orthogonality graph on W33 *lines* is W33 again.

Using artifacts/w33_line_pair_ip_model.json, define a graph on the 40 W33 lines where
an edge means the two A2 subsystems are orthogonal (cross inner products all 0).

This script verifies that this line-orthogonality graph is SRG(40,12,2,4),
matching the original W33 point graph parameters.

Output:
  - artifacts/w33_line_orthogonality_graph.json
  - artifacts/w33_line_orthogonality_graph.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

IN_IP_MODEL = ROOT / "artifacts" / "w33_line_pair_ip_model.json"

OUT_JSON = ROOT / "artifacts" / "w33_line_orthogonality_graph.json"
OUT_MD = ROOT / "artifacts" / "w33_line_orthogonality_graph.md"


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    obj = json.loads(IN_IP_MODEL.read_text(encoding="utf-8"))
    model = obj.get("model")
    if not isinstance(model, dict) or len(model) != 780:
        raise RuntimeError("Invalid w33_line_pair_ip_model.json: model")

    n = 40
    adj = np.zeros((n, n), dtype=int)
    for entry in model.values():
        i = int(entry["i"])
        j = int(entry["j"])
        if entry["type"] == "orthogonal":
            adj[i, j] = adj[j, i] = 1

    degs = adj.sum(axis=1).tolist()
    deg_set = sorted(set(int(x) for x in degs))
    if len(deg_set) != 1:
        raise RuntimeError(f"Not regular: degree set {deg_set}")
    k = int(deg_set[0])

    # SRG parameters: lambda = common neighbors for adjacent pairs, mu = for non-adjacent pairs.
    lam: Counter[int] = Counter()
    mu: Counter[int] = Counter()
    for i in range(n):
        for j in range(i + 1, n):
            cn = int(np.dot(adj[i], adj[j]))
            if adj[i, j] == 1:
                lam[cn] += 1
            else:
                mu[cn] += 1

    out = {
        "counts": {"vertices": n, "edges": int(adj.sum() // 2)},
        "degrees": {"unique": deg_set},
        "srg": {
            "k": k,
            "lambda_common_neighbors_hist": dict(
                sorted((int(a), int(b)) for a, b in lam.items())
            ),
            "mu_common_neighbors_hist": dict(
                sorted((int(a), int(b)) for a, b in mu.items())
            ),
            "is_srg_40_12_2_4": (
                k == 12 and set(lam.keys()) == {2} and set(mu.keys()) == {4}
            ),
        },
    }
    _write_json(OUT_JSON, out)

    md = []
    md.append("# W33 Line-Orthogonality Graph")
    md.append("")
    md.append(f"- Vertices (lines): **{n}**")
    md.append(f"- Edges (orthogonal line-pairs): **{out['counts']['edges']}**")
    md.append(f"- Degree k: **{k}**")
    md.append(
        f"- λ (adjacent common neighbors): `{out['srg']['lambda_common_neighbors_hist']}`"
    )
    md.append(
        f"- μ (non-adjacent common neighbors): `{out['srg']['mu_common_neighbors_hist']}`"
    )
    md.append("")
    md.append(f"SRG(40,12,2,4): **{out['srg']['is_srg_40_12_2_4']}**")
    md.append("")
    md.append(f"_Wrote: `{OUT_JSON}`_")
    md.append(f"_Wrote: `{OUT_MD}`_")
    _write_md(OUT_MD, md)

    print(f"wrote={OUT_JSON}")
    print(f"wrote={OUT_MD}")
    print(f"SRG(40,12,2,4)={out['srg']['is_srg_40_12_2_4']}")


if __name__ == "__main__":
    main()
