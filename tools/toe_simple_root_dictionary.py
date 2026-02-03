#!/usr/bin/env python3
"""
Build a "physics dictionary" keyed by the 6 canonical E6 simple roots.

This glues together:
  - Chevalley certificate (Cartan, Serre OK): artifacts/e6_basis_export_chevalley_27rep_canonical.json
  - Weyl simple-generator (s1..s6) signed action on the canonical 27:
      artifacts/we6_signed_action_on_27.json
  - Cubic-triad selection parity and firewall-bad triads:
      artifacts/selection_rules_report.json
      artifacts/physics_selection_table.json
      artifacts/firewall_bad_triads_mapping.json
  - Dynamics observables on the same 27-sector (Schläfli kernel + firewall edges):
      tools/toe_dynamics.py

Writes:
  artifacts/toe_simple_root_dictionary.json
  artifacts/toe_simple_root_dictionary.md
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


def _tri_key(t: Sequence[int]) -> Tuple[int, int, int]:
    a, b, c = (int(t[0]), int(t[1]), int(t[2]))
    return tuple(sorted((a, b, c)))  # type: ignore[return-value]


def _comm_norm_diag_u(h_diag: np.ndarray, u: np.ndarray) -> float:
    diff = h_diag[:, None] - h_diag[None, :]
    return float(np.linalg.norm(diff * u))


def _drift_diag_u(
    h_diag: np.ndarray, u: np.ndarray, *, seed: int, steps: int
) -> Tuple[float, float]:
    rng = np.random.default_rng(seed)
    psi = rng.normal(size=27) + 1j * rng.normal(size=27)
    psi = psi / np.linalg.norm(psi)
    exps = []
    for _ in range(int(steps) + 1):
        exps.append(float(np.vdot(psi, h_diag * psi).real))
        psi = u @ psi
    deltas = np.abs(np.diff(np.array(exps, dtype=float)))
    return (
        float(np.mean(deltas)) if deltas.size else 0.0,
        float(np.max(deltas)) if deltas.size else 0.0,
    )


def _hol_hist_bins(
    theta: np.ndarray, tris: List[Tuple[int, int, int]], *, bins: int
) -> Dict[int, int]:
    two_pi = float(2.0 * np.pi)
    hist = {i: 0 for i in range(int(bins))}
    for a, b, c in tris:
        ang = float(theta[a, b] + theta[b, c] + theta[c, a])
        x = (ang / two_pi) * bins
        bb = int(np.floor(x + 0.5)) % int(bins)
        hist[bb] += 1
    return hist


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dt", type=float, default=0.35)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--phase-noise", type=float, default=0.0)
    p.add_argument(
        "--phase-source",
        choices=["random", "w33_clock"],
        default="random",
        help="Edge phase source: seeded random Z6 or deterministic W33 holonomy-derived clock.",
    )
    p.add_argument("--steps", type=int, default=30)
    p.add_argument(
        "--out-json",
        type=Path,
        default=ROOT / "artifacts" / "toe_simple_root_dictionary.json",
    )
    p.add_argument(
        "--out-md",
        type=Path,
        default=ROOT / "artifacts" / "toe_simple_root_dictionary.md",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    cert = _load_json(
        ROOT / "artifacts" / "e6_basis_export_chevalley_27rep_canonical.json"
    )
    act = _load_json(ROOT / "artifacts" / "we6_signed_action_on_27.json")
    sel = _load_json(ROOT / "artifacts" / "selection_rules_report.json")
    phys = _load_json(ROOT / "artifacts" / "physics_selection_table.json")
    fwmap = _load_json(ROOT / "artifacts" / "firewall_bad_triads_mapping.json")

    bad_triads = [_tri_key(t) for t in phys["firewall_bad_triads"]]
    bad_set = set(bad_triads)

    # Graph + phases (same basis as selection rules: E6-id).
    skew, meet = toe_dynamics.load_schlafli_graph()
    fw = toe_dynamics.load_firewall_bad_edges()
    good_edges = toe_dynamics.edge_list_from_adj(skew)
    all_edges = good_edges + sorted(fw.bad_edges)
    theta = toe_dynamics.build_edge_phases(
        all_edges,
        seed=int(args.seed),
        noise_sigma=float(args.phase_noise),
        phase_mod=6,
        source=str(args.phase_source),
    )

    # Triangle sets: Schläfli skew triangles + firewall-bad meet triangles.
    tris_schlafli = toe_dynamics.triangles_in_graph(skew)
    tris_bad = [tuple(sorted(t)) for t in fw.triangles]

    # Build U at two endpoints: firewall on/off (1.0 blocks bad edges; 0.0 includes them).
    cartan = toe_dynamics.load_e6_cartan().astype(np.complex128)
    h_diag = np.array(
        [np.real(np.diag(cartan[i])).astype(float) for i in range(6)], dtype=float
    )

    dyn: Dict[str, object] = {
        "dt": float(args.dt),
        "seed": int(args.seed),
        "phase_noise": float(args.phase_noise),
        "steps": int(args.steps),
    }
    dyn_cases: Dict[str, object] = {}
    for fw_strength in (1.0, 0.0):
        m = toe_dynamics.build_hamiltonian(
            good_adj=skew,
            bad_edges=fw.bad_edges,
            theta=theta,
            firewall_strength=float(fw_strength),
        )
        u = toe_dynamics.unitary_from_hermitian(m, dt=float(args.dt))

        per_hi = []
        for i in range(6):
            diag = h_diag[i]
            dims = {
                "plus": int(np.sum(diag > 1e-9)),
                "minus": int(np.sum(diag < -1e-9)),
                "zero": int(np.sum(np.abs(diag) <= 1e-9)),
            }
            comm_n = _comm_norm_diag_u(diag, u)
            mean_d, max_d = _drift_diag_u(
                diag, u, seed=int(args.seed) + 999, steps=int(args.steps)
            )
            per_hi.append(
                {
                    "i": i + 1,
                    "comm_norm": float(comm_n),
                    "mean_drift": float(mean_d),
                    "max_drift": float(max_d),
                    "dims": dims,
                }
            )

        # Holonomy buckets for Schläfli triangles and the 9 firewall triangles.
        hist_s24 = _hol_hist_bins(theta, tris_schlafli, bins=24)
        hist_b24 = _hol_hist_bins(theta, tris_bad, bins=24)
        hist_s12 = {k % 12: hist_s24[k] + hist_s24.get(k + 12, 0) for k in range(12)}
        hist_b12 = {k % 12: hist_b24[k] + hist_b24.get(k + 12, 0) for k in range(12)}

        best = toe_dynamics.best_conserved_charge(
            u=u,
            cartan=cartan,
            n_samples=250,
            seed=int(args.seed) + (0 if fw_strength == 1.0 else 10_000),
            steps=int(args.steps),
        )

        dyn_cases[str(fw_strength)] = {
            "firewall_strength": float(fw_strength),
            "per_simple_cartan": per_hi,
            "best_charge": {
                "score": best.score,
                "mean_drift": best.mean_drift,
                "comm_norm": best.comm_norm,
                "coeffs": best.coeffs,
                "dims": best.dims,
            },
            "holonomy": {
                "schlafli_triangles": {
                    "n": len(tris_schlafli),
                    "hist_z12": {str(k): int(v) for k, v in sorted(hist_s12.items())},
                    "hist_z24": {str(k): int(v) for k, v in sorted(hist_s24.items())},
                },
                "firewall_bad_triangles": {
                    "n": len(tris_bad),
                    "hist_z12": {str(k): int(v) for k, v in sorted(hist_b12.items())},
                    "hist_z24": {str(k): int(v) for k, v in sorted(hist_b24.items())},
                },
            },
        }

    # Selection-rule / firewall summary per generator (s_i corresponds to simple root i).
    sel_by_name = {g["name"]: g for g in sel["generators"]}
    phys_by_name = {g["name"]: g for g in phys["generators"]}
    parity_bad = fwmap["selection_parity_on_bad_triads"]

    root_rows = []
    for i in range(6):
        name = f"s{i+1}"
        g_act = next(g for g in act["generators"] if g["name"] == name)
        p_perm = [int(x) for x in g_act["permutation"]]

        moved = [
            tuple(sorted((p_perm[a], p_perm[b], p_perm[c]))) for (a, b, c) in bad_triads
        ]
        overlap = len(set(moved) & bad_set)

        g_sel = sel_by_name[name]
        g_phys = phys_by_name[name]
        root_rows.append(
            {
                "i": i + 1,
                "name": name,
                "selection": {
                    "global_scale": int(g_sel["global_scale"]),
                    "triad_parity_hist": g_sel["triad_parity_hist"],
                },
                "firewall": {
                    "bad_triads_parity_hist": parity_bad[name][
                        "bad_triads_parity_hist"
                    ],
                    "preserved_bad": int(g_phys["counts"]["preserved_bad"]),
                    "flipped_bad": int(g_phys["counts"]["flipped_bad"]),
                    "image_overlap_bad_triads": int(overlap),
                },
                "channels": {
                    "n_transpositions": int(
                        g_sel["channels"].get("n_transpositions", 0)
                    ),
                    "triads_fixed_setwise": int(
                        g_sel["channels"].get("triads_fixed_setwise", 0)
                    ),
                },
            }
        )

    out = {
        "status": "ok",
        "certificate": {
            "dynkin_type": cert["cartan"]["dynkin_type"],
            "cartan_matrix": cert["cartan"]["cartan_matrix"],
            "serre_ok": bool(cert["serre"]["ok"]),
            "serre_tol": float(cert["serre"]["tol"]),
            "root_residual_max": float(
                cert["root_decomposition"]["root_eigvec_residual_max"]
            ),
            "cartan_comm_max_frob": float(
                cert["cartan_recovery"]["cartan_comm_max_frob"]
            ),
        },
        "counts": {
            "triads_total": int(phys["counts"]["triads_total"]),
            "firewall_bad_triads": int(phys["counts"]["firewall_bad_triads"]),
            "schlafli_good_edges": int(skew.sum() // 2),
            "firewall_bad_edges": int(len(fw.bad_edges)),
        },
        "dynamics": {"params": dyn, "cases": dyn_cases},
        "simple_roots": root_rows,
    }

    _write_json(args.out_json, out)

    # Markdown summary for humans.
    lines: List[str] = []
    lines.append("# TOE simple-root dictionary (E6)")
    lines.append("")
    lines.append("## Certificate")
    lines.append(f"- Dynkin type: `{out['certificate']['dynkin_type']}`")
    lines.append(
        f"- Serre: `{out['certificate']['serre_ok']}` (tol `{out['certificate']['serre_tol']}`)"
    )
    lines.append(
        f"- Cartan comm max (Frobenius): `{out['certificate']['cartan_comm_max_frob']}`"
    )
    lines.append(
        f"- Root eigvec residual max: `{out['certificate']['root_residual_max']}`"
    )
    lines.append("")
    lines.append("## Per-simple-root summary")
    for r in root_rows:
        fw_info = r["firewall"]
        lines.append(
            f"- {r['name']}: bad flipped `{fw_info['flipped_bad']}` / preserved `{fw_info['preserved_bad']}`; "
            f"bad-parity `{fw_info['bad_triads_parity_hist']}`; overlap(image(bad),bad) `{fw_info['image_overlap_bad_triads']}`"
        )
    lines.append("")
    lines.append("## Dynamics snapshots")
    for k in ("1.0", "0.0"):
        c = dyn_cases[k]
        best = c["best_charge"]
        lines.append(
            f"- fw `{k}`: best score `{best['score']}`, drift `{best['mean_drift']}`, comm `{best['comm_norm']}`, dims `{best['dims']}`"
        )
    lines.append("")
    lines.append(f"- JSON: `{args.out_json}`")
    _write_md(args.out_md, lines)

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
