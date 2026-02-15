#!/usr/bin/env python3
"""Quick fitter for l3_scale (smaller samples + quick verify).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _flatten_e8z3(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    linfty_mod = _load_module(
        ROOT / "tools" / "build_linfty_firewall_extension.py", "linfty_mod"
    )

    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = linfty_mod._load_bad9()

    L = linfty_mod.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0)

    rng = np.random.default_rng(2026)

    num = 0.0
    den = 0.0
    target_samples = 120
    attempts = 0
    while attempts < 600 and num == 0 and den == 0:
        attempts += 1
        for _ in range(200):
            x = toe._random_element(rng, e6_basis, scale0=1, scale1=2, scale2=2)
            y = toe._random_element(rng, e6_basis, scale0=1, scale1=2, scale2=2)
            z = toe._random_element(rng, e6_basis, scale0=1, scale1=2, scale2=2)
            J = toe._jacobi(L.br_l2, x, y, z)
            S = L.l3(x, y, z).scale(
                -1.0
            )  # recover pre-scaled fiber-sum S (l3 = -s * S)
            Sflat = _flatten_e8z3(S)
            Jflat = _flatten_e8z3(J)
            s_den = float(np.vdot(Sflat, Sflat).real)
            if s_den < 1e-20:
                continue
            s_num = float(np.vdot(Sflat, Jflat).real)
            num += s_num
            den += s_den
            target_samples -= 1
            if target_samples <= 0:
                break
        if target_samples <= 0:
            break

    if den == 0.0:
        print("Could not gather valid samples for fitting")
        return

    s_opt = num / den
    print(f"Quick-fitted l3_scale = {s_opt:.6f}")

    # quick verification (30 trials)
    rng2 = np.random.default_rng(321)
    Ltest = linfty_mod.LInftyE8Extension(
        toe, proj, all_triads, bad9, l3_scale=float(s_opt)
    )
    verify = linfty_mod.verify_homotopy_jacobi(Ltest, toe, e6_basis, rng2, trials=30)
    print("Verification (30 trials):")
    for k, v in verify.items():
        print(
            f"  {k}: l2_anom={v['l2_jacobi_anomaly_max']:.3e} homotopy_res={v['homotopy_residual_max']:.3e}"
        )


if __name__ == "__main__":
    main()
