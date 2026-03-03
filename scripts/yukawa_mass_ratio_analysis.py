"""Utility for analyzing fermion mass ratios from the W33 Yukawa tensor.

This script is intended to support Pillar 68: determine whether the
Higgs VEV direction that gives good CKM/PMNS mixing can also reproduce the
observed fermion mass hierarchies.  It can also perform a random search for
VEV directions that yield hierarchical singular values.

Usage:
    python scripts/yukawa_mass_ratio_analysis.py [--search N]

Options:
    --search N   perform N random samples and report best errors.

The script loads the tensor from the same routines used by
`THEORY_PART_CLXXIV_YUKAWA_OPTIMIZATION.py` and reads the optimized
parameters from `data/w33_yukawa_optimization.json` if available.
"""

from __future__ import annotations
import argparse, json, os
from pathlib import Path
import numpy as np

from w33_complex_yukawa import build_z3_complex_profiles, build_dominant_profiles
from w33_ckm_from_vev import cubic_form_on_h27


ROOT = Path(__file__).resolve().parents[1]

# CKM target used across optimization scripts in this repository.
V_CKM_exp = np.array(
    [
        [0.97373, 0.2243, 0.00382],
        [0.2210, 0.9870, 0.0410],
        [0.0080, 0.0388, 1.0130],
    ]
)


def build_yukawa_tensor():
    """Reconstruct the 3x3x27 Yukawa tensor T[a,b,k]."""
    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    n27 = len(H27)
    T = np.zeros((3, 3, n27), dtype=complex)
    for k in range(n27):
        e_k = np.zeros(n27, dtype=complex)
        e_k[k] = 1.0
        for a in range(3):
            for b in range(a, 3):
                val = cubic_form_on_h27(None, local_tris, psi_dom[a], psi_dom[b], e_k)
                T[a, b, k] = val
                T[b, a, k] = val
    return T


def yukawa_from_vev(T, v_H):
    """Matrix Y = T · v_H."""
    return np.einsum("abk,k->ab", T, v_H)


def singular_value_ratios(Y):
    """Return singular values and successive ratios sv[1]/sv[0], sv[2]/sv[1]."""
    sv = np.linalg.svd(Y, compute_uv=False)
    sv_sorted = np.sort(sv)[::-1]
    ratios = (sv_sorted[1] / sv_sorted[0], sv_sorted[2] / sv_sorted[1])
    return sv_sorted, ratios


def load_optimized_vevs():
    """Load best CKM VEVs from the JSON data file, returning (v_up, v_dn).

    Returns None if file not found or malformed.
    """
    path = os.path.join("data", "w33_yukawa_optimization.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    if "ckm" not in data:
        return None
    ck = data["ckm"]
    try:
        v_up = np.array(ck["v1_re"]) + 1j * np.array(ck["v1_im"])
        v_dn = np.array(ck["v2_re"]) + 1j * np.array(ck["v2_im"])
        # normalise
        v_up = v_up / np.linalg.norm(v_up)
        v_dn = v_dn / np.linalg.norm(v_dn)
        return v_up, v_dn
    except Exception:
        return None


def mass_ratio_error(ratio_vals, target):
    """Compute squared log-difference error between 2-tuple ratio_vals and target."""
    return sum((np.log(ratio_vals[i]) - np.log(target[i])) ** 2 for i in range(2))


def random_search(T, n_samples=10000, seed=0):
    """Perform random sampling of Higgs VEV directions to find good mass ratios.

    Returns a dict with best up/down errors and corresponding VEVs.
    """
    # target ratios from PDG approximations (from conversation summary)
    r_up = [1/500, 500/85000]
    r_dn = [1/20, 1/40]
    rng = np.random.default_rng(seed)
    best = {
        "up_err": float("inf"),
        "dn_err": float("inf"),
        "up_vev": None,
        "dn_vev": None,
    }
    for _ in range(n_samples):
        v = rng.normal(size=27) + 1j * rng.normal(size=27)
        v /= np.linalg.norm(v)
        Y = yukawa_from_vev(T, v)
        sv, ratios = singular_value_ratios(Y)
        err = mass_ratio_error(ratios, r_up)
        if err < best["up_err"]:
            best["up_err"] = err
            best["up_vev"] = v.copy()
        # also test down-type by generating a second independent random vev
        w = rng.normal(size=27) + 1j * rng.normal(size=27)
        w /= np.linalg.norm(w)
        Yd = yukawa_from_vev(T, w)
        svd, ratiosd = singular_value_ratios(Yd)
        errd = mass_ratio_error(ratiosd, r_dn)
        if errd < best["dn_err"]:
            best["dn_err"] = errd
            best["dn_vev"] = w.copy()
    return best


def mass_ratio_objective(params, T, target):
    """Objective for a single Higgs VEV giving target ratios.

    ``params`` is a 54-real vector encoding a complex 27-vector.  The
    returned value is the squared log-difference error defined by
    ``mass_ratio_error``.
    """
    # unpack
    v = params[:27] + 1j * params[27:]
    norm = np.linalg.norm(v)
    if norm < 1e-15:
        return 1e6
    v = v / norm
    Y = yukawa_from_vev(T, v)
    _, ratios = singular_value_ratios(Y)
    return mass_ratio_error(ratios, target)


def ckm_and_mass_objective(params, T, ckm_target, r_up, r_dn, weight_mass=1.0):
    """Combined objective for CKM error plus mass‑ratio error.

    ``params`` is a 108-real vector encoding two complex 27‑vectors
    ``v_up`` and ``v_dn``.  The CKM error is the Frobenius norm of
    |V_CKM(v_up,v_dn)|-``ckm_target``.  The mass error is the sum of
    squared log‑differences for the up and down sectors.  ``weight_mass``
    scales the mass component relative to CKM.
    """
    # split into two vevs
    v_up = params[:27] + 1j * params[27:54]
    v_dn = params[54:81] + 1j * params[81:108]
    nu = np.linalg.norm(v_up); nd = np.linalg.norm(v_dn)
    if nu < 1e-15 or nd < 1e-15:
        return 1e6
    v_up /= nu; v_dn /= nd
    # CKM part
    Y_u = yukawa_from_vev(T, v_up)
    Y_d = yukawa_from_vev(T, v_dn)
    try:
        from w33_ckm_from_vev import compute_ckm_and_jarlskog
        V, _ = compute_ckm_and_jarlskog(Y_u, Y_d)
        ckm_err = float(np.linalg.norm(np.abs(V) - ckm_target, "fro"))
    except Exception:
        ckm_err = 1e6
    # mass part
    sv_u, ratios_u = singular_value_ratios(Y_u)
    sv_d, ratios_d = singular_value_ratios(Y_d)
    mass_err = mass_ratio_error(ratios_u, r_up) + mass_ratio_error(ratios_d, r_dn)
    return ckm_err + weight_mass * mass_err


def optimize_mass_ratio(T, target, n_restarts=5, maxiter=1000):
    """Run gradient-based optimization for mass ratios.

    Returns a tuple ``(best_err, best_vev)``.
    """
    from scipy.optimize import minimize
    # initial guess: random unit vector
    rng = np.random.default_rng(123)
    best_err = float("inf")
    best_vec = None
    for i in range(n_restarts):
        guess = rng.normal(size=27) + 1j * rng.normal(size=27)
        guess /= np.linalg.norm(guess)
        params0 = np.concatenate([np.real(guess), np.imag(guess)])
        res = minimize(
            mass_ratio_objective, params0, args=(T, target),
            method="L-BFGS-B", options={"maxiter": maxiter, "ftol": 1e-12},
        )
        if res.fun < best_err:
            best_err = float(res.fun)
            v = res.x[:27] + 1j * res.x[27:]
            best_vec = v / np.linalg.norm(v)
    return best_err, best_vec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", type=int, default=0,
                        help="number of random samples to evaluate")
    parser.add_argument("--optimize", action="store_true",
                        help="run gradient-based mass ratio optimization")
    parser.add_argument("--combined", action="store_true",
                        help="optimize CKM mixing and mass ratios together")
    parser.add_argument(
        "--combined-restarts",
        type=int,
        default=8,
        help="number of multi-start attempts for --combined",
    )
    parser.add_argument(
        "--mass-weight",
        type=float,
        default=1.0,
        help="mass penalty weight in combined objective",
    )
    args = parser.parse_args()

    print("Building Yukawa tensor...")
    T = build_yukawa_tensor()
    print("Done.")

    vevs = load_optimized_vevs()
    if vevs is not None:
        v_up, v_dn = vevs
        print("Loaded optimized CKM VEVs.")
        for label, v in [("up", v_up), ("down", v_dn)]:
            Y = yukawa_from_vev(T, v)
            sv, ratios = singular_value_ratios(Y)
            print(f"{label} singular values: {sv}")
            print(f"{label} ratios: {ratios}")
    else:
        print("No optimized VEV found (run Pillar CLXXIV first)")

    if args.search > 0:
        print(f"Performing {args.search} random samples...")
        best = random_search(T, n_samples=args.search)
        print("Best up-sector error", best["up_err"])
        print("Best down-sector error", best["dn_err"])
        sv_up, r_up = singular_value_ratios(yukawa_from_vev(T, best["up_vev"]))
        sv_dn, r_dn = singular_value_ratios(yukawa_from_vev(T, best["dn_vev"]))
        print("  up best ratios", r_up, "singular", sv_up)
        print("  dn best ratios", r_dn, "singular", sv_dn)

    if args.optimize or args.combined:
        # run gradient-based optimization for both sectors
        r_up = [1/500, 500/85000]
        r_dn = [1/20, 1/40]
        if args.optimize:
            print("Running mass ratio optimization...")
            err_u, v_u = optimize_mass_ratio(T, r_up, n_restarts=5)
            err_d, v_d = optimize_mass_ratio(T, r_dn, n_restarts=5)
            print(f"Optimized up-sector error {err_u}")
            print(f"Optimized down-sector error {err_d}")
            if v_u is not None:
                sv_u, ratios_u = singular_value_ratios(yukawa_from_vev(T, v_u))
                print("  up optimized ratios", ratios_u, "singular", sv_u)
            if v_d is not None:
                sv_d, ratios_d = singular_value_ratios(yukawa_from_vev(T, v_d))
                print("  down optimized ratios", ratios_d, "singular", sv_d)
        if args.combined:
            print("Running combined CKM+mass optimization...")
            # start from previous CKM-optimal parameters if available
            initial = None
            if args.optimize is False:
                # try loading from data file
                vevs = load_optimized_vevs()
                if vevs is not None:
                    v_up0, v_dn0 = vevs
                    params0 = np.concatenate([np.real(v_up0), np.imag(v_up0),
                                              np.real(v_dn0), np.imag(v_dn0)])
                    initial = params0
            from scipy.optimize import minimize
            def run_combined(init=None, weight=1.0):
                if init is None:
                    rng = np.random.default_rng(9)
                    guess = rng.normal(size=108)
                else:
                    guess = init.copy()
                res = minimize(
                    ckm_and_mass_objective, guess,
                    args=(T, V_CKM_exp, r_up, r_dn, weight),
                    method="L-BFGS-B", options={"maxiter":2000, "ftol":1e-12},
                )
                return res.fun, res.x

            best_comb_err = float("inf")
            best_comb_params = None
            rng_starts = np.random.default_rng(20260303)
            for k in range(max(1, args.combined_restarts)):
                if k == 0 and initial is not None:
                    start = initial
                else:
                    start = rng_starts.normal(size=108)
                cur_err, cur_params = run_combined(start, weight=args.mass_weight)
                if cur_err < best_comb_err:
                    best_comb_err = cur_err
                    best_comb_params = cur_params

            print(
                f"Combined objective (best of {max(1, args.combined_restarts)} starts) = {best_comb_err}"
            )
            # display CKM and mass errors separately
            c_err = ckm_and_mass_objective(
                best_comb_params, T, V_CKM_exp, r_up, r_dn, weight_mass=0.0
            )
            total_w = ckm_and_mass_objective(
                best_comb_params,
                T,
                V_CKM_exp,
                r_up,
                r_dn,
                weight_mass=args.mass_weight,
            )
            if args.mass_weight > 0:
                m_err = (total_w - c_err) / args.mass_weight
            else:
                m_err = 0.0
            print(f"  CKM error component {c_err:.6f}")
            print(f"  mass error component {m_err:.6e}")
            # breakdown actual ratios
            v_up_c = best_comb_params[:27] + 1j * best_comb_params[27:54]
            v_dn_c = best_comb_params[54:81] + 1j * best_comb_params[81:108]
            v_up_c /= np.linalg.norm(v_up_c)
            v_dn_c /= np.linalg.norm(v_dn_c)
            sv_u, ratios_u = singular_value_ratios(yukawa_from_vev(T, v_up_c))
            sv_d, ratios_d = singular_value_ratios(yukawa_from_vev(T, v_dn_c))
            print("  up ratios", ratios_u, "down ratios", ratios_d)

            # write optimization artifact for downstream analysis
            out = {
                "combined_objective": float(best_comb_err),
                "ckm_error": float(c_err),
                "mass_error": float(m_err),
                "mass_weight": float(args.mass_weight),
                "combined_restarts": int(max(1, args.combined_restarts)),
                "target_ratios": {
                    "up": [float(r_up[0]), float(r_up[1])],
                    "down": [float(r_dn[0]), float(r_dn[1])],
                },
                "achieved_ratios": {
                    "up": [float(ratios_u[0]), float(ratios_u[1])],
                    "down": [float(ratios_d[0]), float(ratios_d[1])],
                },
                "singular_values": {
                    "up": [float(x) for x in sv_u.tolist()],
                    "down": [float(x) for x in sv_d.tolist()],
                },
                "params": [float(x) for x in best_comb_params.tolist()],
            }
            out_path = ROOT / "artifacts" / "w33_combined_ckm_mass_optimization.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
            print(f"  wrote {out_path}")

if __name__ == "__main__":
    main()
