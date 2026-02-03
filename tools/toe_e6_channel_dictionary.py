#!/usr/bin/env python3
"""
TOE "E6 channel dictionary" (v3): operator-supported channels on the 27-state sector.

Goal: tie the *certified* E6 Chevalley generators (e_i,f_i,h_i) to protocol-level
signatures on the Schläfli 27:
  - whether dominant matrix support lies on Schläfli edges vs firewall-bad edges
  - whether a W33 holonomy-derived Z6 clock label k6 exists for those pairs
  - the induced Z12/Z24 bins for clock taxonomy

Inputs:
  - artifacts/e6_basis_export_chevalley_27rep_canonical.json
  - artifacts/e6_basis_export_chevalley_27rep_canonical_generators.npy
  - W33_holonomy_s3_gauge_bundle.zip (for deterministic clock phases on Q)
  - tools/toe_dynamics.py (for Schläfli adjacency + firewall bad edges + clock mapping)

Outputs:
  - artifacts/toe_e6_channel_dictionary_v3.json
  - artifacts/toe_e6_channel_dictionary_v3.md
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


def _top_offdiag_entries(
    mat: np.ndarray, k: int
) -> List[Tuple[int, int, complex, float]]:
    if mat.shape != (27, 27):
        raise ValueError("Expected 27x27 matrix")
    abs_m = np.abs(mat)
    # Zero diagonal so we only rank off-diagonal transitions.
    abs_m = abs_m.copy()
    abs_m[np.eye(27, dtype=bool)] = 0.0
    flat = abs_m.ravel()
    if k <= 0:
        return []
    k = min(int(k), flat.size)
    # argpartition for top-k, then sort.
    idxs = np.argpartition(flat, -k)[-k:]
    idxs = idxs[np.argsort(flat[idxs])[::-1]]
    out: List[Tuple[int, int, complex, float]] = []
    for idx in idxs.tolist():
        p = int(idx // 27)
        q = int(idx % 27)
        v = complex(mat[p, q])
        out.append((p, q, v, float(abs(v))))
    return out


def _mass_breakdown(
    mat: np.ndarray, skew: np.ndarray, bad_edges: set[tuple[int, int]]
) -> Dict[str, float]:
    if mat.shape != (27, 27):
        raise ValueError("Expected 27x27 matrix")
    m = mat.copy()
    m[np.eye(27, dtype=bool)] = 0.0
    abs2 = np.abs(m) ** 2

    good_mask = skew.astype(bool)
    bad_mask = np.zeros((27, 27), dtype=bool)
    for u, v in bad_edges:
        bad_mask[u, v] = True
        bad_mask[v, u] = True

    good_mass = float(np.sum(abs2[good_mask]))
    bad_mass = float(np.sum(abs2[bad_mask]))
    total_mass = float(np.sum(abs2))
    other_mass = float(total_mass - good_mass - bad_mass)
    return {
        "total_offdiag_mass": total_mass,
        "schlafli_edge_mass": good_mass,
        "firewall_bad_edge_mass": bad_mass,
        "other_mass": other_mass,
    }


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--top-k", type=int, default=12)
    p.add_argument(
        "--clock-source",
        choices=["w33_clock", "none"],
        default="w33_clock",
        help="Whether to annotate edges with deterministic W33-derived k6 clock labels.",
    )
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_e6_channel_dictionary_v3.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_e6_channel_dictionary_v3.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    cert = _load_json(
        ROOT / "artifacts" / "e6_basis_export_chevalley_27rep_canonical.json"
    )
    gens = np.load(
        ROOT / "artifacts" / "e6_basis_export_chevalley_27rep_canonical_generators.npy",
        allow_pickle=True,
    ).item()
    e = np.array(gens["e"], dtype=np.complex128)
    f = np.array(gens["f"], dtype=np.complex128)
    h = np.array(gens["h"], dtype=np.complex128)
    if e.shape != (6, 27, 27) or f.shape != (6, 27, 27) or h.shape != (6, 27, 27):
        raise RuntimeError("Unexpected generators shape in canonical_generators.npy")

    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    bad_edges = set(fw.bad_edges)

    def edge_clock(i: int, j: int) -> Dict[str, int] | None:
        if args.clock_source != "w33_clock":
            return None
        k6 = toe_dynamics.schlafli_edge_clock_k6(i, j)
        if k6 is None:
            return None
        k6i = int(k6) % 6
        return {
            "k6": k6i,
            "z12": int((2 * k6i) % 12),
            "z24": int((4 * k6i) % 24),
        }

    entries: List[Dict[str, object]] = []
    for i in range(6):
        row: Dict[str, object] = {"i": i + 1, "name": f"alpha_{i+1}"}
        row["mass_e"] = _mass_breakdown(e[i], skew, bad_edges)
        row["mass_f"] = _mass_breakdown(f[i], skew, bad_edges)

        top_e = []
        for p_idx, q_idx, val, mag in _top_offdiag_entries(e[i], int(args.top_k)):
            u, v = (p_idx, q_idx) if p_idx < q_idx else (q_idx, p_idx)
            top_e.append(
                {
                    "p": p_idx,
                    "q": q_idx,
                    "abs": float(mag),
                    "val": [float(np.real(val)), float(np.imag(val))],
                    "schlafli_edge": bool(skew[p_idx, q_idx]),
                    "meet_edge": bool(meet[p_idx, q_idx]),
                    "firewall_bad_edge": bool((u, v) in bad_edges),
                    "clock": edge_clock(p_idx, q_idx),
                }
            )
        top_f = []
        for p_idx, q_idx, val, mag in _top_offdiag_entries(f[i], int(args.top_k)):
            u, v = (p_idx, q_idx) if p_idx < q_idx else (q_idx, p_idx)
            top_f.append(
                {
                    "p": p_idx,
                    "q": q_idx,
                    "abs": float(mag),
                    "val": [float(np.real(val)), float(np.imag(val))],
                    "schlafli_edge": bool(skew[p_idx, q_idx]),
                    "meet_edge": bool(meet[p_idx, q_idx]),
                    "firewall_bad_edge": bool((u, v) in bad_edges),
                    "clock": edge_clock(p_idx, q_idx),
                }
            )

        row["top_e"] = top_e
        row["top_f"] = top_f
        entries.append(row)

    out: Dict[str, object] = {
        "status": "ok",
        "certificate": {
            "dynkin_type": cert["cartan"]["dynkin_type"],
            "serre_ok": bool(cert["serre"]["ok"]),
            "serre_tol": float(cert["serre"]["tol"]),
            "root_residual_max": float(
                cert["root_decomposition"]["root_eigvec_residual_max"]
            ),
        },
        "graph": {
            "schlafli_edges": int(skew.sum() // 2),
            "firewall_bad_edges": int(len(bad_edges)),
            "firewall_bad_triangles": int(len(fw.triangles)),
        },
        "clock_source": str(args.clock_source),
        "entries": entries,
    }
    _write_json(args.out_json, out)

    lines: List[str] = []
    lines.append("# TOE E6 channel dictionary (v3)")
    lines.append("")
    lines.append("## Certificate")
    lines.append(f"- Dynkin type: `{out['certificate']['dynkin_type']}`")
    lines.append(
        f"- Serre: `{out['certificate']['serre_ok']}` (tol `{out['certificate']['serre_tol']}`)"
    )
    lines.append(f"- Root residual max: `{out['certificate']['root_residual_max']}`")
    lines.append("")
    lines.append("## Graph")
    lines.append(f"- Schläfli edges: `{out['graph']['schlafli_edges']}`")
    lines.append(
        f"- Firewall bad edges: `{out['graph']['firewall_bad_edges']}` (triangles `{out['graph']['firewall_bad_triangles']}`)"
    )
    lines.append(f"- Clock source: `{out['clock_source']}`")
    lines.append("")
    lines.append("## Per simple root (dominant operator support)")
    for r in entries:
        i = int(r["i"])
        lines.append(f"### α{i}")
        me = r["mass_e"]
        mf = r["mass_f"]
        lines.append(
            f"- e: mass schlafli `{me['schlafli_edge_mass']:.3g}`, bad `{me['firewall_bad_edge_mass']:.3g}`, other `{me['other_mass']:.3g}`"
        )
        lines.append(
            f"- f: mass schlafli `{mf['schlafli_edge_mass']:.3g}`, bad `{mf['firewall_bad_edge_mass']:.3g}`, other `{mf['other_mass']:.3g}`"
        )
        if r["top_e"]:
            t0 = r["top_e"][0]
            c = t0["clock"]
            if isinstance(c, dict):
                c_str = f"k6={c['k6']} z12={c['z12']} z24={c['z24']}"
            else:
                c_str = "none"
            lines.append(
                f"- top e entry: ({t0['p']},{t0['q']}) |.|={t0['abs']:.3g} "
                f"schlafli={t0['schlafli_edge']} bad={t0['firewall_bad_edge']} clock={c_str}"
            )
        if r["top_f"]:
            t0 = r["top_f"][0]
            c = t0["clock"]
            if isinstance(c, dict):
                c_str = f"k6={c['k6']} z12={c['z12']} z24={c['z24']}"
            else:
                c_str = "none"
            lines.append(
                f"- top f entry: ({t0['p']},{t0['q']}) |.|={t0['abs']:.3g} "
                f"schlafli={t0['schlafli_edge']} bad={t0['firewall_bad_edge']} clock={c_str}"
            )
        lines.append("")

    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
