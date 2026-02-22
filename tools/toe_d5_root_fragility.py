#!/usr/bin/env python3
"""
Classify all 72 E6 root operators by the standard SO(10) chain (D5×U(1)) and
measure firewall fragility by operator support.

This avoids the basis-mismatch issues of older "D6+12" exports by working entirely
inside the repo's canonical **weight-basis** export:
  - artifacts/e6_27rep_basis_export/E6_basis_78.npy
  - artifacts/e6_27rep_basis_export/Cartan_mats.npy

Steps:
  1) Identify each of the 72 root operators by its unique root-vector α(h) ∈ Z^6
     from off-diagonal support in the weight basis.
  2) Recover the Cartan matrix from the 6 simple roots (export indices 0..5).
  3) Choose the D5 deletion node (degree-1 node whose deletion yields D5).
  4) For each root, compute simple-root coefficients c (Cartan*c = α(h)).
     Classify:
       - D5_root if c[del] = 0
       - complement otherwise (signed by c[del])
  5) Compute firewall fragility from full operator support:
       mass_good = Σ_{Schläfli skew edges} |E_ij|^2
       mass_bad  = Σ_{firewall bad edges} |E_ij|^2
       bad_frac  = mass_bad / (mass_good + mass_bad)

Outputs:
  - artifacts/toe_d5_root_fragility.json
  - artifacts/toe_d5_root_fragility.md
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _offdiag_root_vector(
    mat: np.ndarray, weights_27x6: np.ndarray, tol: float = 1e-9
) -> Tuple[int, ...] | None:
    idx = np.argwhere((np.abs(mat) > tol) & (~np.eye(27, dtype=bool)))
    if idx.size == 0:
        return None
    i0, j0 = (int(idx[0, 0]), int(idx[0, 1]))
    rv0 = tuple(int(x) for x in (weights_27x6[i0] - weights_27x6[j0]).tolist())
    for i, j in idx.tolist():
        i = int(i)
        j = int(j)
        rv = tuple(int(x) for x in (weights_27x6[i] - weights_27x6[j]).tolist())
        if rv != rv0:
            raise RuntimeError(
                f"Root-vector mismatch in operator support: {rv0} vs {rv}"
            )
    return rv0


def _cartan_from_simple_root_columns(simple_cols: List[Tuple[int, ...]]) -> np.ndarray:
    if len(simple_cols) != 6:
        raise ValueError("Expected 6 simple-root columns")
    A = np.column_stack(
        [np.array(col, dtype=int) for col in simple_cols]
    )  # A_{i,j} = α_j(h_i)
    if A.shape != (6, 6):
        raise ValueError("Unexpected Cartan matrix shape")
    return A


def _choose_d5_deleted_node(cartan: np.ndarray) -> int:
    deg = [int(np.sum((cartan[i] == -1) & (np.arange(6) != i))) for i in range(6)]
    candidates = [i for i, d in enumerate(deg) if d == 1]
    if not candidates:
        raise RuntimeError("No degree-1 nodes in Dynkin graph; expected E6")

    def sub_deg(keep: List[int]) -> List[int]:
        idx = np.array(keep, dtype=int)
        sub = cartan[np.ix_(idx, idx)]
        d = []
        for a in range(sub.shape[0]):
            d.append(int(np.sum((sub[a] == -1) & (np.arange(sub.shape[0]) != a))))
        return sorted(d)

    for r in sorted(candidates):
        keep = [i for i in range(6) if i != r]
        if sub_deg(keep) == [1, 1, 1, 2, 3]:
            return int(r)
    raise RuntimeError("Could not find a D5 deletion node")


def _simple_coeffs(
    cartan: np.ndarray, root_alpha_h: Tuple[int, ...]
) -> Tuple[int, ...]:
    a = np.array(root_alpha_h, dtype=float)
    c = np.linalg.solve(cartan.astype(float), a)
    c_int = np.rint(c).astype(int)
    resid = cartan.astype(int) @ c_int - np.array(root_alpha_h, dtype=int)
    if int(np.max(np.abs(resid))) != 0:
        raise RuntimeError(
            f"Non-integer root coefficients? resid={resid.tolist()} alpha(h)={list(root_alpha_h)}"
        )
    return tuple(int(x) for x in c_int.tolist())


def _mass_by_edge_classes(
    mat: np.ndarray, skew: np.ndarray, bad_edges: set[tuple[int, int]]
) -> Tuple[float, float, float]:
    m = mat.copy()
    m[np.eye(27, dtype=bool)] = 0.0
    abs2 = np.abs(m) ** 2

    bad_mask = np.zeros((27, 27), dtype=bool)
    for u, v in bad_edges:
        bad_mask[u, v] = True
        bad_mask[v, u] = True

    good_mass = float(np.sum(abs2[skew]))
    bad_mass = float(np.sum(abs2[bad_mask]))
    total_off = float(np.sum(abs2))
    other_mass = float(total_off - good_mass - bad_mass)
    return good_mass, bad_mass, other_mass


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--export-dir",
        type=Path,
        default=ROOT / "artifacts" / "e6_27rep_basis_export",
        help="Directory containing E6_basis_78.npy and Cartan_mats.npy.",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_d5_root_fragility.json",
    )
    p.add_argument(
        "--out-md", type=Path, default=ROOT / "artifacts" / "toe_d5_root_fragility.md"
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    export_dir = args.export_dir.expanduser().resolve()
    E = np.load(export_dir / "E6_basis_78.npy").astype(np.complex128)  # (78,27,27)
    cartan_mats = np.load(export_dir / "Cartan_mats.npy").astype(
        np.complex128
    )  # (6,27,27)
    weights_27x6 = np.stack(
        [np.real_if_close(np.diag(cartan_mats[i]), tol=1e-9) for i in range(6)],
        axis=1,
    ).astype(int)

    # Identify Cartan indices (no off-diagonal support) and root indices.
    cartan_idx: List[int] = []
    root_idx: List[int] = []
    alpha_h_by_basis: Dict[int, Tuple[int, ...]] = {}
    for k in range(E.shape[0]):
        rv = _offdiag_root_vector(E[k], weights_27x6, tol=1e-9)
        if rv is None:
            cartan_idx.append(int(k))
        else:
            root_idx.append(int(k))
            alpha_h_by_basis[int(k)] = rv
    if len(cartan_idx) != 6 or len(root_idx) != 72:
        raise RuntimeError(
            f"Unexpected split: cartan={len(cartan_idx)} roots={len(root_idx)}"
        )

    # Cartan matrix from the 6 simple roots (basis indices 0..5 in this export).
    simple_basis = [0, 1, 2, 3, 4, 5]
    cartan = _cartan_from_simple_root_columns(
        [alpha_h_by_basis[k] for k in simple_basis]
    )
    d5_deleted = _choose_d5_deleted_node(cartan)

    # Protocol edge classes.
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "tools"))
    import toe_dynamics  # type: ignore  # noqa: E402

    skew, _meet = toe_dynamics.load_schlafli_graph()
    bad_edges = set(toe_dynamics.load_firewall_bad_edges().bad_edges)

    rows = []
    class_counts = Counter()
    agg = defaultdict(list)

    for k in root_idx:
        ah = alpha_h_by_basis[k]
        coeffs = _simple_coeffs(cartan, ah)
        u1 = int(coeffs[d5_deleted])
        if u1 == 0:
            klass = "D5_root"
        elif u1 > 0:
            klass = "compl_plus"
        else:
            klass = "compl_minus"

        good_mass, bad_mass, other_mass = _mass_by_edge_classes(E[k], skew, bad_edges)
        denom = good_mass + bad_mass
        bad_frac = float(bad_mass / denom) if denom > 0.0 else 0.0
        other_frac = (
            float(other_mass / (good_mass + bad_mass + other_mass))
            if (good_mass + bad_mass + other_mass) > 0.0
            else 0.0
        )

        class_counts[klass] += 1
        agg[klass].append(bad_frac)

        rows.append(
            {
                "basis_index": int(k),
                "alpha_h": [int(x) for x in ah],
                "simple_coeffs": [int(x) for x in coeffs],
                "u1_deleted_coeff": int(u1),
                "class": klass,
                "mass": {
                    "good": good_mass,
                    "bad": bad_mass,
                    "other": other_mass,
                    "bad_frac": bad_frac,
                    "other_frac": other_frac,
                },
            }
        )

    rows = sorted(
        rows, key=lambda r: (-float(r["mass"]["bad_frac"]), int(r["basis_index"]))
    )

    summary = {}
    for klass, vals in agg.items():
        arr = np.array(vals, dtype=float)
        summary[klass] = {
            "n": int(arr.size),
            "mean_bad_frac": float(np.mean(arr)) if arr.size else 0.0,
            "max_bad_frac": float(np.max(arr)) if arr.size else 0.0,
        }

    out: Dict[str, object] = {
        "status": "ok",
        "export_dir": str(export_dir),
        "cartan_matrix": cartan.astype(int).tolist(),
        "d5_deleted_node": int(d5_deleted),
        "counts": {k: int(v) for k, v in sorted(class_counts.items())},
        "by_class": summary,
        "roots": rows,
    }
    _write_json(args.out_json, out)

    md: List[str] = []
    md.append("# TOE: D5×U(1) Root Fragility (full operator support)")
    md.append("")
    md.append(f"- export_dir: `{export_dir}`")
    md.append(f"- D5 deleted node (0-based): `{d5_deleted}`")
    md.append("")
    md.append("## Counts")
    for k, v in out["counts"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Bad-edge mass fraction by class (mean / max)")
    for k, st in sorted(summary.items()):
        md.append(
            f"- {k}: mean `{st['mean_bad_frac']:.3f}` max `{st['max_bad_frac']:.3f}`"
        )
    md.append("")
    md.append("## Most firewall-sensitive roots (top 15 by bad_frac)")
    for r in rows[:15]:
        md.append(
            f"- idx {r['basis_index']}: class={r['class']} bad_frac={float(r['mass']['bad_frac']):.3f} other_frac={float(r['mass']['other_frac']):.3f} coeff_del={r['u1_deleted_coeff']}"
        )
    md.append("")
    md.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, md)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
