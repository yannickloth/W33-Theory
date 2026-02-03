#!/usr/bin/env python3
"""
Exact E6 simple-root coupling atlas in the **weight basis** export.

This is the "clean" version of the coupling atlas that does *not* depend on
numerical root clustering:
  - It uses `artifacts/e6_27rep_basis_export/E6_basis_78.npy` which is already
    (Cartan + 72 root operators) in a weight basis where the Cartan is diagonal.
  - It identifies each root operator by the unique weight difference it induces.
  - It computes commutators among the 6 simple root generators (basis indices 0..5),
    then matches outputs back to one of the 72 root operators by Frobenius overlap.

It also classifies output roots by the standard E6 -> D5×U(1) subalgebra:
  - Choose a D5 by deleting the appropriate degree-1 node from the E6 Dynkin graph.
  - A root lies in D5 iff its simple-root coefficient on the deleted node is 0.

Outputs:
  - artifacts/toe_coupling_strengths_v5_weightbasis.json
  - artifacts/toe_coupling_strengths_v5_weightbasis.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _fro_inner(a: np.ndarray, b: np.ndarray) -> complex:
    return np.vdot(a.reshape(-1), b.reshape(-1))


def _fro_norm(a: np.ndarray) -> float:
    return float(np.linalg.norm(a.reshape(-1)))


def _offdiag_root_vector(
    mat: np.ndarray, weights_27x6: np.ndarray, tol: float = 1e-9
) -> Tuple[int, ...] | None:
    """Return α(h) in Z^6 from off-diagonal support, or None if no off-diagonal support."""
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


def _dominant_support_edge(mat: np.ndarray) -> Tuple[int, int] | None:
    m = mat.copy()
    m[np.eye(27, dtype=bool)] = 0.0
    a = np.abs(m)
    if float(np.max(a)) == 0.0:
        return None
    i, j = np.unravel_index(int(np.argmax(a)), a.shape)
    return int(i), int(j)


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
    """Pick a degree-1 node whose deletion yields D5 (degrees [1,1,1,2,3])."""
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
    raise RuntimeError(
        "Could not find a D5 deletion node (got only A5-like deletions?)"
    )


def _simple_coeffs(
    cartan: np.ndarray, root_alpha_h: Tuple[int, ...]
) -> Tuple[int, ...]:
    """Solve Cartan * c = alpha(h) for integer c (simple-root coefficients)."""
    a = np.array(root_alpha_h, dtype=float)
    c = np.linalg.solve(cartan.astype(float), a)
    c_int = np.rint(c).astype(int)
    resid = cartan.astype(int) @ c_int - np.array(root_alpha_h, dtype=int)
    if int(np.max(np.abs(resid))) != 0:
        raise RuntimeError(
            f"Non-integer root coefficients? resid={resid.tolist()} for alpha(h)={list(root_alpha_h)}"
        )
    return tuple(int(x) for x in c_int.tolist())


@dataclass(frozen=True)
class CouplingRow:
    pair: Tuple[int, int]  # 1-based simple-root labels (i<j)
    comm_norm: float
    overlap: float
    out_basis_index: (
        int | None
    )  # index into E6_basis_78.npy, or None if zero commutator
    out_root_alpha_h: Tuple[int, ...] | None  # alpha(h) in Z^6
    out_simple_coeffs: Tuple[int, ...] | None  # coefficients in simple roots
    d5_class: str | None  # "d5" or "coset" (only if out_root exists)
    support: Tuple[int, int] | None  # dominant (p,q) entry indices in 0..26
    schlafli_edge: bool | None
    firewall_bad: bool | None
    k6: int | None
    z12: int | None
    z24: int | None


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--export-dir",
        type=Path,
        default=ROOT / "artifacts" / "e6_27rep_basis_export",
        help="Directory containing E6_basis_78.npy and Cartan_mats.npy (default: artifacts/e6_27rep_basis_export).",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_coupling_strengths_v5_weightbasis.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_coupling_strengths_v5_weightbasis.md",
    )
    p.add_argument(
        "--tol-zero",
        type=float,
        default=1e-8,
        help="Frobenius norm threshold for treating commutators as zero.",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    export_dir = args.export_dir.expanduser().resolve()
    basis_path = export_dir / "E6_basis_78.npy"
    cartan_path = export_dir / "Cartan_mats.npy"
    if not basis_path.exists() or not cartan_path.exists():
        raise RuntimeError(f"Missing expected files under export_dir={export_dir}")

    E = np.load(basis_path).astype(np.complex128)  # (78,27,27)
    cartan_mats = np.load(cartan_path).astype(np.complex128)  # (6,27,27)
    weights_27x6 = np.stack(
        [np.real_if_close(np.diag(cartan_mats[i]), tol=1e-9) for i in range(6)], axis=1
    ).astype(int)

    # Identify Cartan indices (no off-diagonal support).
    cartan_idx: List[int] = []
    root_idx: List[int] = []
    root_alpha_h_by_basis: Dict[int, Tuple[int, ...]] = {}
    for k in range(E.shape[0]):
        rv = _offdiag_root_vector(E[k], weights_27x6, tol=1e-9)
        if rv is None:
            cartan_idx.append(int(k))
        else:
            root_idx.append(int(k))
            root_alpha_h_by_basis[int(k)] = rv
    if len(cartan_idx) != 6 or len(root_idx) != 72:
        raise RuntimeError(
            f"Unexpected split: cartan={len(cartan_idx)} roots={len(root_idx)}"
        )

    # Simple roots are basis indices 0..5 in this export (by construction).
    simple_basis = [0, 1, 2, 3, 4, 5]
    simple_cols = [root_alpha_h_by_basis[k] for k in simple_basis]
    cartan = _cartan_from_simple_root_columns(simple_cols)

    d5_deleted = _choose_d5_deleted_node(cartan)

    # Protocol annotation helpers (Schläfli + firewall + clock).
    sys.path.insert(0, str(ROOT / "tools"))
    import toe_dynamics  # type: ignore  # noqa: E402

    skew, _meet = toe_dynamics.load_schlafli_graph()
    bad_edges = set(toe_dynamics.load_firewall_bad_edges().bad_edges)

    def annotate_support(
        edge: Tuple[int, int] | None
    ) -> Tuple[bool | None, bool | None, int | None, int | None, int | None]:
        if edge is None:
            return None, None, None, None, None
        p0, q0 = edge
        schlafli = bool(skew[p0, q0])
        a, b = (p0, q0) if p0 < q0 else (q0, p0)
        bad = bool((a, b) in bad_edges)
        k6 = toe_dynamics.schlafli_edge_clock_k6(p0, q0) if schlafli else None
        if k6 is None:
            return schlafli, bad, None, None, None
        z12 = int((2 * int(k6)) % 12)
        z24 = int((4 * int(k6)) % 24)
        return schlafli, bad, int(k6), z12, z24

    rows: List[CouplingRow] = []
    # Pairwise commutators of simple roots, labeled 1..6.
    for a_i in range(6):
        for a_j in range(a_i + 1, 6):
            i = simple_basis[a_i]
            j = simple_basis[a_j]
            comm = E[i] @ E[j] - E[j] @ E[i]
            cn = _fro_norm(comm)
            if cn < float(args.tol_zero):
                rows.append(
                    CouplingRow(
                        pair=(a_i + 1, a_j + 1),
                        comm_norm=cn,
                        overlap=0.0,
                        out_basis_index=None,
                        out_root_alpha_h=None,
                        out_simple_coeffs=None,
                        d5_class=None,
                        support=None,
                        schlafli_edge=None,
                        firewall_bad=None,
                        k6=None,
                        z12=None,
                        z24=None,
                    )
                )
                continue

            # Match to best root operator in the 72 basis elements by overlap.
            best_k = None
            best_ov = -1.0
            for k in root_idx:
                nk = _fro_norm(E[k])
                if nk == 0.0:
                    continue
                ov = abs(_fro_inner(E[k], comm)) / (nk * cn)
                if float(ov) > best_ov:
                    best_ov = float(ov)
                    best_k = int(k)

            if best_k is None:
                raise RuntimeError(
                    "Failed to match a nonzero commutator to any root basis element"
                )

            alpha_h = root_alpha_h_by_basis[best_k]
            coeffs = _simple_coeffs(cartan, alpha_h)
            d5_class = "d5" if int(coeffs[d5_deleted]) == 0 else "coset"
            support = _dominant_support_edge(E[best_k])
            schlafli, bad, k6, z12, z24 = annotate_support(support)

            rows.append(
                CouplingRow(
                    pair=(a_i + 1, a_j + 1),
                    comm_norm=cn,
                    overlap=float(best_ov),
                    out_basis_index=best_k,
                    out_root_alpha_h=alpha_h,
                    out_simple_coeffs=coeffs,
                    d5_class=d5_class,
                    support=support,
                    schlafli_edge=schlafli,
                    firewall_bad=bad,
                    k6=k6,
                    z12=z12,
                    z24=z24,
                )
            )

    out: Dict[str, object] = {
        "status": "ok",
        "source": {
            "export_dir": str(export_dir),
            "basis_file": str(basis_path),
            "cartan_file": str(cartan_path),
        },
        "cartan": {
            "matrix": cartan.tolist(),
            "simple_basis_indices": simple_basis,
            "d5_deleted_node": int(d5_deleted),
        },
        "couplings": [
            {
                "pair": [int(r.pair[0]), int(r.pair[1])],
                "comm_norm": float(r.comm_norm),
                "overlap": float(r.overlap),
                "out_basis_index": r.out_basis_index,
                "out_root_alpha_h": (
                    list(r.out_root_alpha_h) if r.out_root_alpha_h is not None else None
                ),
                "out_simple_coeffs": (
                    list(r.out_simple_coeffs)
                    if r.out_simple_coeffs is not None
                    else None
                ),
                "d5_class": r.d5_class,
                "support": list(r.support) if r.support is not None else None,
                "schlafli_edge": r.schlafli_edge,
                "firewall_bad": r.firewall_bad,
                "k6": r.k6,
                "z12": r.z12,
                "z24": r.z24,
            }
            for r in rows
        ],
    }
    _write_json(args.out_json, out)

    lines: List[str] = []
    lines.append("# TOE Coupling Strengths v5 (weight-basis exact)")
    lines.append("")
    lines.append(f"- Export dir: `{export_dir}`")
    lines.append(f"- D5 deletion node (0-based): `{d5_deleted}`")
    lines.append("")
    lines.append("Nonzero couplings:")
    nonzero = [r for r in rows if r.out_basis_index is not None]
    nonzero.sort(key=lambda r: float(r.overlap), reverse=True)
    for r in nonzero:
        lines.append(
            f"- pair {list(r.pair)} -> basis[{r.out_basis_index}] "
            f"alpha(h)={list(r.out_root_alpha_h or ())} coeffs={list(r.out_simple_coeffs or ())} "
            f"class={r.d5_class} overlap={r.overlap:.3f} "
            f"support={list(r.support or ())} schlafli={r.schlafli_edge} bad={r.firewall_bad} "
            f"Z12/Z24={r.z12}/{r.z24}"
        )
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
