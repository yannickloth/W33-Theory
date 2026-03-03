#!/usr/bin/env python3
"""Hybrid active-subspace search for joint CKM + mass-ratio closure.

This script pushes beyond earlier random scans by:
1. Restricting both Higgs VEVs to the proven active subspace of the Yukawa tensor.
2. Running a wide random exploration in that reduced space.
3. Refining the best candidates with gradient-based local optimization.

The objective is:
    CKM Frobenius error + w * mass-ratio log-error
where the mass targets can be either:
    - legacy repository ratios (historical baseline), or
    - PDG-anchored ratios (u,d,s,c,b,t central values).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

# Script lives under tools/, while reusable modules live under scripts/.
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from w33_ckm_from_vev import compute_ckm_and_jarlskog
from yukawa_mass_ratio_analysis import (
    build_yukawa_tensor,
    mass_ratio_error,
    singular_value_ratios,
    yukawa_from_vev,
)


V_CKM_EXP = np.array(
    [
        [0.97373, 0.2243, 0.00382],
        [0.2210, 0.9870, 0.0410],
        [0.0080, 0.0388, 1.0130],
    ],
    dtype=float,
)

# 2024 PDG central values (units: GeV).
PDG_MASS = {
    "u": 0.00216,  # m_u(2 GeV)
    "d": 0.00470,  # m_d(2 GeV)
    "s": 0.0935,  # m_s(2 GeV)
    "c": 1.2730,  # m_c(m_c)
    "b": 4.1830,  # m_b(m_b)
    "t": 172.57,  # top pole
}


def get_mass_targets(name: str) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return (up_targets, down_targets)."""
    if name == "legacy":
        # Existing baseline used in repository scripts.
        return (1 / 500, 500 / 85000), (1 / 20, 1 / 40)
    if name == "pdg":
        up = (PDG_MASS["c"] / PDG_MASS["t"], PDG_MASS["u"] / PDG_MASS["c"])
        down = (PDG_MASS["s"] / PDG_MASS["b"], PDG_MASS["d"] / PDG_MASS["s"])
        return up, down
    raise ValueError(f"unknown target set: {name}")


def koide_q(masses: list[float] | np.ndarray) -> float:
    """Koide Q = (m1+m2+m3)/(sqrt(m1)+sqrt(m2)+sqrt(m3))^2."""
    m = np.clip(np.asarray(masses, dtype=float), 1e-18, None)
    num = float(np.sum(m))
    den = float(np.sum(np.sqrt(m)) ** 2)
    return num / den if den > 0 else 0.0


def build_active_basis(T: np.ndarray) -> tuple[int, np.ndarray]:
    """Compute active basis V_active (27 x rank) from flattened tensor SVD."""
    T_mat = T.reshape(9, 27)
    _, s, vh = np.linalg.svd(T_mat, full_matrices=False)
    rank = int(np.sum(s > 1e-10))
    v_active = vh[:rank, :].conj().T
    return rank, v_active


def to_vevs(x: np.ndarray, v_active: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    """Map 4*rank real parameters to two normalized complex 27-vectors."""
    a_up = x[:rank] + 1j * x[rank : 2 * rank]
    a_dn = x[2 * rank : 3 * rank] + 1j * x[3 * rank : 4 * rank]
    v_up = v_active @ a_up
    v_dn = v_active @ a_dn
    n_up = np.linalg.norm(v_up)
    n_dn = np.linalg.norm(v_dn)
    if n_up < 1e-14 or n_dn < 1e-14:
        raise ValueError("near-zero VEV norm")
    return v_up / n_up, v_dn / n_dn


def split_errors(
    x: np.ndarray,
    T: np.ndarray,
    v_active: np.ndarray,
    rank: int,
    up_target: tuple[float, float],
    dn_target: tuple[float, float],
    koide_target: float = 2.0 / 3.0,
    koide_sector: str = "down",
) -> dict[str, object]:
    """Evaluate CKM and mass errors plus ratio diagnostics."""
    try:
        v_up, v_dn = to_vevs(x, v_active, rank)
    except ValueError:
        return {
            "ok": False,
            "ckm_err": 1e9,
            "mass_err": 1e9,
            "koide_err": 1e9,
            "up_ratios": (0.0, 0.0),
            "dn_ratios": (0.0, 0.0),
        }

    y_up = yukawa_from_vev(T, v_up)
    y_dn = yukawa_from_vev(T, v_dn)
    sv_up, ratios_up = singular_value_ratios(y_up)
    sv_dn, ratios_dn = singular_value_ratios(y_dn)

    try:
        v_ckm, jcp = compute_ckm_and_jarlskog(y_up, y_dn)
        ckm_err = float(np.linalg.norm(np.abs(v_ckm) - V_CKM_EXP, "fro"))
    except Exception:
        ckm_err = 1e9
        v_ckm = np.zeros((3, 3), dtype=float)
        jcp = 0.0

    mass_err = float(mass_ratio_error(ratios_up, up_target) + mass_ratio_error(ratios_dn, dn_target))
    q_up = koide_q(sv_up)
    q_dn = koide_q(sv_dn)
    if koide_sector == "none":
        koide_err = 0.0
    elif koide_sector == "up":
        koide_err = float((q_up - koide_target) ** 2)
    elif koide_sector == "both":
        koide_err = float((q_up - koide_target) ** 2 + (q_dn - koide_target) ** 2)
    else:
        koide_err = float((q_dn - koide_target) ** 2)
    return {
        "ok": True,
        "ckm_err": ckm_err,
        "mass_err": mass_err,
        "koide_err": koide_err,
        "up_ratios": (float(ratios_up[0]), float(ratios_up[1])),
        "dn_ratios": (float(ratios_dn[0]), float(ratios_dn[1])),
        "up_sv": [float(x) for x in sv_up.tolist()],
        "dn_sv": [float(x) for x in sv_dn.tolist()],
        "koide_up": float(q_up),
        "koide_down": float(q_dn),
        "jarlskog": float(np.real(jcp)),
        "v_ckm_abs": np.abs(v_ckm).tolist(),
    }


def objective(
    x: np.ndarray,
    T: np.ndarray,
    v_active: np.ndarray,
    rank: int,
    up_target: tuple[float, float],
    dn_target: tuple[float, float],
    mass_weight: float,
    koide_weight: float,
    koide_target: float,
    koide_sector: str,
) -> float:
    d = split_errors(
        x,
        T,
        v_active,
        rank,
        up_target,
        dn_target,
        koide_target=koide_target,
        koide_sector=koide_sector,
    )
    return float(d["ckm_err"] + mass_weight * d["mass_err"] + koide_weight * d["koide_err"])


def random_seed_vectors(rng: np.random.Generator, rank: int, n: int) -> list[np.ndarray]:
    """Generate random real parameter seeds in active coordinates."""
    seeds: list[np.ndarray] = []
    for _ in range(n):
        x = rng.normal(size=4 * rank)
        seeds.append(x)
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=6000, help="random active-space samples")
    parser.add_argument("--refine", type=int, default=24, help="number of top seeds to refine")
    parser.add_argument("--mass-weight", type=float, default=1.0, help="mass penalty weight")
    parser.add_argument(
        "--koide-weight",
        type=float,
        default=0.0,
        help="additional Koide-penalty weight",
    )
    parser.add_argument(
        "--koide-target",
        type=float,
        default=2.0 / 3.0,
        help="target Koide Q value (default 2/3)",
    )
    parser.add_argument(
        "--koide-sector",
        choices=["none", "down", "up", "both"],
        default="down",
        help="which sector(s) get Koide penalty",
    )
    parser.add_argument(
        "--targets",
        choices=["legacy", "pdg"],
        default="pdg",
        help="mass-ratio target set",
    )
    parser.add_argument("--seed", type=int, default=20260303, help="RNG seed")
    args = parser.parse_args()

    t0 = time.time()
    print("=" * 74)
    print("W33 BREAKTHROUGH SEARCH: ACTIVE SUBSPACE CKM+MASS OPTIMIZATION")
    print("=" * 74)
    print(
        f"targets={args.targets}, samples={args.samples}, refine={args.refine}, "
        f"mass_weight={args.mass_weight}, koide_weight={args.koide_weight}, "
        f"koide_sector={args.koide_sector}, koide_target={args.koide_target}"
    )

    up_target, dn_target = get_mass_targets(args.targets)
    print(f"up target ratios (m2/m3, m1/m2): {up_target}")
    print(f"dn target ratios (m2/m3, m1/m2): {dn_target}")

    print("\nBuilding Yukawa tensor and active basis...")
    T = build_yukawa_tensor()
    rank, v_active = build_active_basis(T)
    print(f"active rank = {rank}")

    rng = np.random.default_rng(args.seed)
    seeds = random_seed_vectors(rng, rank, args.samples)

    # Random phase
    scored = []
    for x in seeds:
        score = objective(
            x,
            T,
            v_active,
            rank,
            up_target,
            dn_target,
            args.mass_weight,
            args.koide_weight,
            args.koide_target,
            args.koide_sector,
        )
        scored.append((score, x))
    scored.sort(key=lambda t: t[0])
    best_random_score = float(scored[0][0])
    print(f"best random objective: {best_random_score:.6f}")

    # Local refinement
    n_ref = min(len(scored), max(1, args.refine))
    best_score = float("inf")
    best_x: np.ndarray | None = None
    for k in range(n_ref):
        x0 = scored[k][1]
        res = minimize(
            objective,
            x0,
            args=(
                T,
                v_active,
                rank,
                up_target,
                dn_target,
                args.mass_weight,
                args.koide_weight,
                args.koide_target,
                args.koide_sector,
            ),
            method="L-BFGS-B",
            options={"maxiter": 2500, "ftol": 1e-12},
        )
        if res.fun < best_score:
            best_score = float(res.fun)
            best_x = res.x.copy()

    assert best_x is not None
    diag = split_errors(
        best_x,
        T,
        v_active,
        rank,
        up_target,
        dn_target,
        koide_target=args.koide_target,
        koide_sector=args.koide_sector,
    )

    print("\nBest refined candidate:")
    print(f"  objective = {best_score:.6f}")
    print(f"  CKM error = {diag['ckm_err']:.6f}")
    print(f"  mass error = {diag['mass_err']:.6f}")
    print(f"  koide error = {diag['koide_err']:.6f}")
    print(f"  up ratios  = {diag['up_ratios']}")
    print(f"  dn ratios  = {diag['dn_ratios']}")
    print(f"  Koide(up/down) = ({diag['koide_up']:.6f}, {diag['koide_down']:.6f})")

    ts_ms = int(time.time() * 1000)
    out = {
        "timestamp_ms": ts_ms,
        "targets": args.targets,
        "target_ratios": {"up": [float(up_target[0]), float(up_target[1])], "down": [float(dn_target[0]), float(dn_target[1])]},
        "settings": {
            "samples": int(args.samples),
            "refine": int(args.refine),
            "mass_weight": float(args.mass_weight),
            "koide_weight": float(args.koide_weight),
            "koide_target": float(args.koide_target),
            "koide_sector": args.koide_sector,
            "seed": int(args.seed),
            "active_rank": int(rank),
        },
        "best_random_objective": best_random_score,
        "best_refined_objective": float(best_score),
        "diagnostics": diag,
        "best_active_params": [float(v) for v in best_x.tolist()],
        "elapsed_s": float(time.time() - t0),
    }

    weight_tag = f"{args.mass_weight:.3f}".replace(".", "p")
    kweight_tag = f"{args.koide_weight:.3f}".replace(".", "p")
    out_path = (
        ROOT
        / "artifacts"
        / f"w33_breakthrough_search_{args.targets}_w{weight_tag}_kw{kweight_tag}_{ts_ms}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
