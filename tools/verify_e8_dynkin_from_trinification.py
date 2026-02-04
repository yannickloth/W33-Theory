#!/usr/bin/env python3
"""
Recover an E8 Dynkin diagram from the trinification-derived E8 root set.

Pipeline:
  1) Rebuild the 240 roots in Z^8 as in verify_e8_root_system_from_trinification.py
  2) Construct the induced inner product <α,β> via B^{-1}, where
       B = Σ_{α∈Φ} α α^T  (adjoint trace form on Cartan)
  3) Choose a generic positivity direction v and define Φ⁺ = {α | α·v > 0}
  4) Extract simple roots as those α∈Φ⁺ not expressible as α=β+γ with β,γ∈Φ⁺
  5) Compute the Cartan matrix and match (up to permutation) to canonical E8

Outputs:
  - artifacts/verify_e8_dynkin_from_trinification.json
  - artifacts/verify_e8_dynkin_from_trinification.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


E8_CANONICAL = np.array(
    [
        [2, -1, 0, 0, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0, 0, 0],
        [0, -1, 2, -1, 0, 0, 0, 0],
        [0, 0, -1, 2, -1, 0, 0, 0],
        [0, 0, 0, -1, 2, -1, 0, -1],
        [0, 0, 0, 0, -1, 2, -1, 0],
        [0, 0, 0, 0, 0, -1, 2, 0],
        [0, 0, 0, 0, -1, 0, 0, 2],
    ],
    dtype=int,
)


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _load_root_tool():
    path = ROOT / "tools" / "verify_e8_root_system_from_trinification.py"
    spec = importlib.util.spec_from_file_location(
        "verify_e8_root_system_from_trinification", path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _inner(Binv: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ Binv @ b)


def main() -> None:
    root_tool = _load_root_tool()

    # Reconstruct the root list exactly as the root-system verifier does.
    e6_roots = root_tool.generate_roots_from_cartan(root_tool.E6_CARTAN)
    w27 = root_tool.load_e6_27_weights_from_chevalley()
    w3 = root_tool.a2_weights_fund3()
    a2_roots = root_tool.a2_roots_from_weights(w3)

    roots8 = set()
    for r in e6_roots:
        roots8.add(tuple(list(r) + [0, 0]))
    for r in a2_roots:
        roots8.add(tuple([0] * 6 + list(r)))
    for mu in w27:
        for nu in w3:
            roots8.add(tuple(list(mu.tolist()) + list(nu.tolist())))
            roots8.add(tuple(list((-mu).tolist()) + list((-nu).tolist())))
    roots8.discard(tuple([0] * 8))

    roots = np.array(sorted(roots8), dtype=float)
    B = roots.T @ roots
    Binv = np.linalg.inv(B)

    # Choose a generic positivity direction.
    rng = np.random.default_rng(0)
    v = rng.normal(size=8)
    dots = roots @ v
    # Avoid degenerate ties.
    if np.min(np.abs(dots)) < 1e-12:
        v = rng.normal(size=8)
        dots = roots @ v
    pos = [tuple(int(x) for x in r) for r, d in zip(roots.astype(int), dots) if d > 0]
    pos_set = set(pos)
    if len(pos) != 120:
        raise RuntimeError(f"Expected 120 positive roots; got {len(pos)}")

    # Simple roots are positive roots that are not a sum of two positive roots.
    simples: List[Tuple[int, ...]] = []
    for a in pos:
        a_vec = np.array(a, dtype=int)
        is_simple = True
        for b in pos:
            if b == a:
                continue
            diff = tuple(int(x) for x in (a_vec - np.array(b, dtype=int)).tolist())
            if diff in pos_set:
                is_simple = False
                break
        if is_simple:
            simples.append(a)
    if len(simples) != 8:
        raise RuntimeError(f"Expected 8 simple roots; got {len(simples)}")

    S = np.array(simples, dtype=float)  # 8×8
    # Cartan matrix: a_{ij} = 2 <α_i, α_j>/<α_j,α_j>
    C = np.zeros((8, 8), dtype=int)
    lens = np.array([_inner(Binv, S[j], S[j]) for j in range(8)], dtype=float)
    for i in range(8):
        for j in range(8):
            val = 2.0 * _inner(Binv, S[i], S[j]) / lens[j]
            C[i, j] = int(round(val))

    # Verify simply-laced properties.
    ok_simple_laced = bool(
        np.all(np.diag(C) == 2)
        and (set(int(x) for x in np.unique(C).tolist()) - {2, 0, -1}) == set()
        and np.all(C == C.T)
    )

    # Match to canonical E8 Cartan matrix up to permutation.
    perm_found: List[int] | None = None
    for perm in permutations(range(8)):
        P = np.array(perm, dtype=int)
        Cp = C[np.ix_(P, P)]
        if np.array_equal(Cp, E8_CANONICAL):
            perm_found = list(perm)
            break

    status = "ok"
    if not ok_simple_laced:
        status = "fail"
    if perm_found is None:
        status = "fail"

    out = {
        "status": status,
        "counts": {
            "roots_total": int(len(roots8)),
            "positive": int(len(pos)),
            "simples": int(len(simples)),
        },
        "cartan_matrix_raw": C.tolist(),
        "cartan_matrix_matches_canonical": bool(perm_found is not None),
        "perm_to_canonical": perm_found,
        "simples": simples,
        "notes": {
            "positivity_vector": v.tolist(),
            "simple_laced_ok": ok_simple_laced,
        },
    }

    out_json = ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.json"
    out_md = ROOT / "artifacts" / "verify_e8_dynkin_from_trinification.md"
    _write_json(out_json, out)

    md: List[str] = []
    md.append("# Verify E8 Dynkin from trinification roots\n")
    md.append(f"- status: `{status}`")
    md.append(f"- roots_total: `{out['counts']['roots_total']}`")
    md.append(f"- positives: `{out['counts']['positive']}`")
    md.append(f"- simples: `{out['counts']['simples']}`")
    md.append(f"- matches canonical: `{out['cartan_matrix_matches_canonical']}`\n")
    md.append("## Cartan matrix (raw order)\n")
    md.append("```")
    for row in C.tolist():
        md.append(" ".join(f"{x:2d}" for x in row))
    md.append("```")
    md.append(f"- JSON: `{out_json}`")
    _write_md(out_md, md)

    print(f"status={status} simples={len(simples)}")
    if status != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
