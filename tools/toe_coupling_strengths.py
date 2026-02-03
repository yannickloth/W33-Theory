#!/usr/bin/env python3
"""
Compute a coupling atlas among the 6 E6 simple-root raising channels (Chevalley e_i).

For each unordered pair (i,j), i<j:
  1) compute commutator C = [e_i, e_j]
  2) match C to the best root operator E_out among the 72 roots by normalized Frobenius overlap
  3) report coupling coefficient (least-squares in the 1D root space) and protocol annotations:
       - dominant support edge (p->q) of E_out
       - Schläfli edge? firewall-bad edge? clock bins (from W33 holonomy clock on Q)

Outputs:
  - artifacts/toe_coupling_strengths_v4.json
  - artifacts/toe_coupling_strengths_v4.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


toe_dynamics = _load_module(ROOT / "tools" / "toe_dynamics.py", "toe_dynamics")


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def _top_offdiag(mat: np.ndarray) -> Tuple[int, int, float]:
    abs_m = np.abs(mat).copy()
    abs_m[np.eye(27, dtype=bool)] = 0.0
    idx = int(np.argmax(abs_m))
    p = int(idx // 27)
    q = int(idx % 27)
    return p, q, float(abs_m[p, q])


def _overlap(a: np.ndarray, b: np.ndarray) -> float:
    va = a.ravel()
    vb = b.ravel()
    na = float(np.linalg.norm(va))
    nb = float(np.linalg.norm(vb))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(abs(np.vdot(vb, va)) / (na * nb))


def _ensure_root_dict() -> Path:
    out = ROOT / "artifacts" / "toe_root_operator_dictionary.npy"
    if out.exists():
        return out
    tool = _load_module(
        ROOT / "tools" / "toe_root_operator_dictionary.py",
        "toe_root_operator_dictionary",
    )
    tool.main([])
    if not out.exists():
        raise RuntimeError(
            "Expected toe_root_operator_dictionary.npy to be written but file missing"
        )
    return out


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_coupling_strengths_v4.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_coupling_strengths_v4.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    gens = np.load(
        ROOT / "artifacts" / "e6_basis_export_chevalley_27rep_canonical_generators.npy",
        allow_pickle=True,
    ).item()
    e = np.array(gens["e"], dtype=np.complex128)
    if e.shape != (6, 27, 27):
        raise RuntimeError("Unexpected e shape in canonical generators")

    root_path = _ensure_root_dict()
    root = np.load(root_path, allow_pickle=True).item()
    keys = np.array(root["keys"], dtype=np.int64)
    weights = np.array(root["weights"], dtype=np.complex128)
    mats = np.array(root["mats"], dtype=np.complex128)
    is_pos = np.array(
        root.get("is_positive", np.zeros((72,), dtype=np.int64)), dtype=np.int64
    )

    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    bad_edges = set(fw.bad_edges)

    couplings: List[Dict[str, object]] = []
    for i in range(6):
        for j in range(i + 1, 6):
            c = _comm(e[i], e[j])
            cn = float(np.linalg.norm(c))
            if cn < 1e-12:
                couplings.append(
                    {
                        "pair": [i + 1, j + 1],
                        "comm_norm": cn,
                        "overlap": 0.0,
                        "output_root_index": None,
                        "output_root_key": None,
                    }
                )
                continue

            overlaps = [float(_overlap(c, mats[k])) for k in range(mats.shape[0])]
            k_best = int(np.argmax(overlaps))
            out_m = mats[k_best]
            ov = float(overlaps[k_best])
            # best-fit coefficient in 1D span of out_m
            denom = complex(np.vdot(out_m.ravel(), out_m.ravel()))
            coeff = (
                complex(np.vdot(out_m.ravel(), c.ravel()) / denom)
                if denom != 0
                else 0.0 + 0.0j
            )

            p0, q0, mag0 = _top_offdiag(out_m)
            u, v = (p0, q0) if p0 < q0 else (q0, p0)
            clock = toe_dynamics.schlafli_edge_clock_k6(p0, q0)
            if clock is None:
                z12 = None
                z24 = None
            else:
                k6 = int(clock) % 6
                z12 = int((2 * k6) % 12)
                z24 = int((4 * k6) % 24)

            couplings.append(
                {
                    "pair": [i + 1, j + 1],
                    "comm_norm": cn,
                    "overlap": ov,
                    "coeff": [float(np.real(coeff)), float(np.imag(coeff))],
                    "coeff_abs": float(abs(coeff)),
                    "output_root_index": k_best,
                    "output_root_key": [int(x) for x in keys[k_best].tolist()],
                    "output_root_weight_re": [
                        float(x) for x in np.real(weights[k_best]).tolist()
                    ],
                    "output_root_weight_im": [
                        float(x) for x in np.imag(weights[k_best]).tolist()
                    ],
                    "output_root_is_positive": bool(int(is_pos[k_best]) == 1),
                    "dominant_support": {
                        "p": p0,
                        "q": q0,
                        "abs": mag0,
                        "schlafli_edge": bool(skew[p0, q0]),
                        "meet_edge": bool(meet[p0, q0]),
                        "firewall_bad_edge": bool((u, v) in bad_edges),
                        "clock_k6": int(clock) if clock is not None else None,
                        "phase_z12": z12,
                        "phase_z24": z24,
                    },
                }
            )

    couplings_sorted = sorted(
        couplings, key=lambda r: float(r.get("overlap") or 0.0), reverse=True
    )
    out: Dict[str, object] = {
        "status": "ok",
        "note": "Coupling atlas among Chevalley simple generators e_i, matched to root operators by Frobenius overlap.",
        "counts": {"pairs": len(couplings)},
        "couplings": couplings_sorted,
    }
    _write_json(args.out_json, out)

    lines: List[str] = []
    lines.append("# TOE Coupling Strengths v4 (exact root-operator match)")
    lines.append("")
    lines.append("Top couplings (by overlap):")
    for row in couplings_sorted[:15]:
        pair = row["pair"]
        ov = float(row.get("overlap") or 0.0)
        dom = row.get("dominant_support") or {}
        if not isinstance(dom, dict):
            dom = {}
        lines.append(
            f"- pair {pair} overlap={ov:.3f} comm_norm={float(row.get('comm_norm') or 0.0):.3e} "
            f"support=({dom.get('p')},{dom.get('q')}) schlafli={dom.get('schlafli_edge')} bad={dom.get('firewall_bad_edge')} "
            f"Z12/Z24={dom.get('phase_z12')}/{dom.get('phase_z24')}"
        )
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
