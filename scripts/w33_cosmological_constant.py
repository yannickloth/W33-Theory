#!/usr/bin/env python3
"""
Cosmological Constant and Gravitational Sector from W(3,3)
============================================================

THEOREM (Cosmological Constant from Spectral Ratios):
  The spectral action on W(3,3) determines the cosmological constant
  through the ratio of Seeley-DeWitt coefficients a_0/a_2, which is
  a pure number determined by the graph combinatorics.

KEY RESULTS:
  1. a_0 = 440 (total DOFs), a_2 = 2080/6 = 1040/3
  2. a_0/a_2 = 440/(1040/3) = 1320/1040 = 33/26
  3. The "gravitational" vertex Laplacian L0 has Tr = 480 = 40*12
  4. The trace ratio Tr(L1)/Tr(L0) = 960/480 = 2 (edges/vertices balance)
  5. The spectral action naturally produces a HIERARCHY between the
     cosmological constant (Lambda^4 term) and the Planck scale
     (Lambda^2 term) via the ratio 33/26.

COMPUTATION:
  Part 1: Seeley-DeWitt coefficient ratios
  Part 2: Trace identities and sum rules
  Part 3: Heat kernel asymptotics
  Part 4: Effective cosmological constant
  Part 5: Gravitational sector structure
  Part 6: Synthesis

Usage:
  python scripts/w33_cosmological_constant.py
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from w33_homology import boundary_matrix, build_clique_complex, build_w33

from w33_h1_decomposition import build_incidence_matrix


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def main():
    t0 = time.time()
    print("=" * 72)
    print("  COSMOLOGICAL CONSTANT FROM W(3,3) SPECTRAL DATA")
    print("=" * 72)

    # Build W33
    n, vertices, adj, edges = build_w33()
    simplices = build_clique_complex(n, adj)
    m = len(edges)
    triangles = simplices[2]
    tetrahedra = simplices.get(3, [])

    # All Laplacians
    d2 = boundary_matrix(simplices[2], simplices[1]).astype(float)
    D = build_incidence_matrix(n, edges)
    L0 = D @ D.T
    L1 = D.T @ D + d2 @ d2.T
    if len(tetrahedra) > 0:
        d3 = boundary_matrix(simplices[3], simplices[2]).astype(float)
        L2 = d2.T @ d2 + d3 @ d3.T
    else:
        L2 = d2.T @ d2

    w0 = np.linalg.eigvalsh(L0)
    w1 = np.linalg.eigvalsh(L1)
    w2 = np.linalg.eigvalsh(L2)

    print(
        f"\n  Simplicial complex: {n} vertices, {m} edges, "
        f"{len(triangles)} triangles, {len(tetrahedra)} tetrahedra"
    )

    # =====================================================================
    # PART 1: SEELEY-DEWITT COEFFICIENT RATIOS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 1: SEELEY-DEWITT COEFFICIENTS")
    print("=" * 72)

    # Compute all traces
    tr_L0 = float(np.sum(w0))
    tr_L1 = float(np.sum(w1))
    tr_L2 = float(np.sum(w2))
    tr_total = tr_L0 + tr_L1 + tr_L2

    tr_L0_sq = float(np.sum(w0**2))
    tr_L1_sq = float(np.sum(w1**2))
    tr_L2_sq = float(np.sum(w2**2))
    tr_total_sq = tr_L0_sq + tr_L1_sq + tr_L2_sq

    a_0 = n + m + len(triangles)  # total DOFs
    a_2 = tr_total / 6
    a_4 = tr_total_sq / 360  # simplified

    print(f"  a_0 = {a_0}")
    print(f"  a_2 = Tr(D^2)/6 = {tr_total:.0f}/6 = {a_2:.6f}")
    print(f"  a_4 = Tr(D^4)/360 = {tr_total_sq:.0f}/360 = {a_4:.6f}")

    # Exact rational forms
    a_0_frac = Fraction(a_0)
    tr_total_frac = Fraction(int(round(tr_total)))
    a_2_frac = tr_total_frac / 6
    print(f"\n  Exact fractions:")
    print(f"    a_0 = {a_0_frac}")
    print(f"    a_2 = {tr_total_frac}/6 = {a_2_frac}")
    print(f"    a_0/a_2 = {a_0_frac}/{a_2_frac} = {a_0_frac / a_2_frac}")

    ratio_a0_a2 = a_0_frac / a_2_frac
    print(f"    a_0/a_2 = {ratio_a0_a2} = {float(ratio_a0_a2):.10f}")

    # =====================================================================
    # PART 2: TRACE IDENTITIES
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 2: TRACE IDENTITIES AND SUM RULES")
    print("=" * 72)

    print(f"  Individual traces:")
    print(f"    Tr(L0) = {tr_L0:.0f}  (= n*k = 40*12 = 480)")
    print(f"    Tr(L1) = {tr_L1:.0f}")
    print(f"    Tr(L2) = {tr_L2:.0f}  (= 4*n_tri = 4*160 = 640)")
    print(f"    Total  = {tr_total:.0f}")

    # L1 trace decomposition: 0*81 + 4*120 + 10*24 + 16*15 = 480+240+240 = 960
    print(f"\n  L1 trace decomposition:")
    print(f"    0*81 + 4*120 + 10*24 + 16*15 = {0*81 + 4*120 + 10*24 + 16*15}")

    # Trace ratios
    print(f"\n  Trace ratios:")
    print(f"    Tr(L1)/Tr(L0) = {tr_L1/tr_L0:.6f} = {Fraction(int(tr_L1), int(tr_L0))}")
    print(f"    Tr(L2)/Tr(L0) = {tr_L2/tr_L0:.6f} = {Fraction(int(tr_L2), int(tr_L0))}")
    print(f"    Tr(L2)/Tr(L1) = {tr_L2/tr_L1:.6f} = {Fraction(int(tr_L2), int(tr_L1))}")

    # Sum rule: Tr(L0) + Tr(L2) = 480 + 640 = 1120
    # Tr(L1) = 960
    # Total = 2080
    print(f"\n  Sum rules:")
    print(f"    Tr(L0) + Tr(L2) = {tr_L0 + tr_L2:.0f}")
    print(f"    Tr(L1) = {tr_L1:.0f}")
    print(f"    Tr(L0) + Tr(L2) - Tr(L1) = {tr_L0 + tr_L2 - tr_L1:.0f}")

    # The "McKean-Singer" formula: sum (-1)^k Tr(L_k) = 0
    # (not quite — this is for the supertrace of e^{-tL}, at t=0)
    alternating = tr_L0 - tr_L1 + tr_L2
    print(f"    Tr(L0) - Tr(L1) + Tr(L2) = {alternating:.0f}")

    # =====================================================================
    # PART 3: HEAT KERNEL ASYMPTOTICS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 3: HEAT KERNEL STRUCTURE")
    print("=" * 72)

    # The heat kernel K(t) = sum_n exp(-t*lambda_n) encodes all spectral data.
    # For the full Hodge-Dirac:
    all_eigs = np.concatenate([w0, w1, w2])

    # Exact heat kernel (finite sum)
    # K(t) = 82 + 280*exp(-4t) + 48*exp(-10t) + 30*exp(-16t)
    # where:
    #   82 = 1(b0) + 81(b1) + 0(b2) zero modes
    #   280 = 120(L1 coex) + 160(L2 all)
    #   48 = 24(L0) + 24(L1 exact-10)
    #   30 = 15(L0) + 15(L1 exact-16)

    n_zero = np.sum(np.abs(all_eigs) < 0.5)
    n_at_4 = np.sum(np.abs(all_eigs - 4.0) < 0.5)
    n_at_10 = np.sum(np.abs(all_eigs - 10.0) < 0.5)
    n_at_16 = np.sum(np.abs(all_eigs - 16.0) < 0.5)

    print(f"  Exact heat kernel:")
    print(
        f"    K(t) = {n_zero} + {n_at_4}*exp(-4t) + {n_at_10}*exp(-10t) + {n_at_16}*exp(-16t)"
    )
    print(
        f"    = {n_zero} + {n_at_4}*e^{{-4t}} + {n_at_10}*e^{{-10t}} + {n_at_16}*e^{{-16t}}"
    )

    # Verify: total = 82 + 280 + 48 + 30 = 440
    total_check = n_zero + n_at_4 + n_at_10 + n_at_16
    print(
        f"    Total: {n_zero}+{n_at_4}+{n_at_10}+{n_at_16} = {total_check} (should be 440)"
    )

    # Heat kernel at special values
    print(f"\n  Heat kernel at special values:")
    for t in [0.0, 0.1, 0.5, 1.0, 2.0]:
        if t == 0:
            K_t = float(total_check)
        else:
            K_t = (
                n_zero
                + n_at_4 * np.exp(-4 * t)
                + n_at_10 * np.exp(-10 * t)
                + n_at_16 * np.exp(-16 * t)
            )
        print(f"    K({t:.1f}) = {K_t:.6f}")

    # Small-t expansion: K(t) ~ a_0 - a_2*t + a_4*t^2/2 - ...
    # (since K(t) = sum exp(-t*lambda), K(0) = a_0, K'(0) = -sum(lambda) = -6*a_2)
    K_deriv_0 = -tr_total  # K'(0) = -sum(lambda)
    K_deriv2_0 = tr_total_sq  # K''(0) = sum(lambda^2)
    print(f"\n  Small-t expansion coefficients:")
    print(f"    K(0) = a_0 = {a_0}")
    print(f"    K'(0) = -{tr_total:.0f} = -6*a_2 = -6*{a_2:.2f}")
    print(f"    K''(0) = {tr_total_sq:.0f}")

    # =====================================================================
    # PART 4: EFFECTIVE COSMOLOGICAL CONSTANT
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 4: COSMOLOGICAL CONSTANT STRUCTURE")
    print("=" * 72)

    # In the Connes spectral action:
    #   S = f_4 Lambda^4 a_0 + f_2 Lambda^2 a_2 + f_0 a_4 + ...
    #
    # The cosmological constant Lambda_cc is proportional to:
    #   Lambda_cc ~ (f_4 / f_2) * (a_0 / a_2) * Lambda^2
    #
    # The RATIO a_0/a_2 is the geometric quantity we can compute.

    print(f"  Key ratio: a_0/a_2 = {ratio_a0_a2} = {float(ratio_a0_a2):.10f}")

    # The inverse ratio a_2/a_0 relates to the average eigenvalue
    avg_eigenvalue = tr_total / a_0
    print(
        f"\n  Average eigenvalue: Tr(D^2)/dim = {tr_total:.0f}/{a_0} = {avg_eigenvalue:.6f}"
    )
    print(f"    = {Fraction(int(tr_total), a_0)}")

    # The "spectral gap ratio": smallest nonzero eigenvalue / average
    # This measures how far the cosmological constant is from the Planck scale
    min_nonzero = 4.0  # smallest nonzero eigenvalue
    gap_ratio = min_nonzero / avg_eigenvalue
    print(
        f"  Gap ratio (min_nonzero / avg): {min_nonzero} / {avg_eigenvalue:.4f} = {gap_ratio:.6f}"
    )

    # The fraction of the spectrum in each sector (spectral entropy-like)
    fractions = {
        "zero_modes": n_zero / a_0,
        "gauge (4)": n_at_4 / a_0,
        "moduli (10)": n_at_10 / a_0,
        "moduli (16)": n_at_16 / a_0,
    }
    print(f"\n  Spectral fractions:")
    for name, frac in fractions.items():
        print(f"    {name}: {frac:.6f} ({frac*100:.2f}%)")

    # =====================================================================
    # PART 5: GRAVITATIONAL SECTOR
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 5: GRAVITATIONAL SECTOR (L0 STRUCTURE)")
    print("=" * 72)

    # L0 spectrum: 0^1 + 10^24 + 16^15
    w0_spectrum = {}
    for e in w0:
        key = round(float(e), 1)
        w0_spectrum[key] = w0_spectrum.get(key, 0) + 1

    print(f"  L0 spectrum: {dict(sorted(w0_spectrum.items()))}")
    print(f"  L0 = diag(0, 10*I_24, 16*I_15)")

    # Einstein-Hilbert action from L0:
    # S_EH ~ Tr(L0) = n*k = 480
    # The "scalar curvature" of the graph: R_v = degree(v) for each vertex
    # For SRG(40,12,2,4): all degrees are 12, so R = 12 uniformly.
    print(f"\n  Scalar curvature: R_v = k = 12 (uniform)")
    print(f"  Total scalar curvature: Tr(L0) = n*R = 40*12 = {int(tr_L0)}")

    # The ratio of gravitational to gauge action:
    # S_EH / S_YM = Tr(L0) / (coex contribution to Tr(L1))
    tr_gauge = 4 * 120  # gauge part of Tr(L1)
    tr_matter = 0 * 81  # matter part (zero)
    tr_exact = 10 * 24 + 16 * 15  # exact part
    print(f"\n  Action decomposition:")
    print(f"    S_EH (gravitational) ~ Tr(L0) = {int(tr_L0)}")
    print(f"    S_YM (gauge) ~ 4*120 = {tr_gauge}")
    print(f"    S_exact (moduli) ~ 10*24 + 16*15 = {tr_exact}")
    print(f"    S_matter ~ 0*81 = {tr_matter}")
    print(
        f"    Ratio S_EH/S_YM = {tr_L0/tr_gauge:.6f} = {Fraction(int(tr_L0), tr_gauge)}"
    )

    # =====================================================================
    # PART 6: SYNTHESIS
    # =====================================================================
    print("\n" + "=" * 72)
    print("  PART 6: SYNTHESIS")
    print("=" * 72)

    print(
        f"""
  COSMOLOGICAL CONSTANT FROM W(3,3):

  1. SEELEY-DEWITT COEFFICIENTS:
     a_0 = {a_0} (cosmological, proportional to Lambda^4)
     a_2 = {a_2_frac} (Einstein-Hilbert, proportional to Lambda^2)
     a_0/a_2 = {ratio_a0_a2} = {float(ratio_a0_a2):.10f}

  2. HEAT KERNEL (EXACT):
     K(t) = {n_zero} + {n_at_4}*exp(-4t) + {n_at_10}*exp(-10t) + {n_at_16}*exp(-16t)
     Only 4 distinct eigenvalues: 0, 4, 10, 16
     Spectral simplicity: 4 terms suffice for all physics

  3. TRACE IDENTITIES:
     Tr(L0) = {int(tr_L0)} = 40*12 (gravitational)
     Tr(L1) = {int(tr_L1)} = 0+480+240+240 (gauge+moduli)
     Tr(L2) = {int(tr_L2)} = 4*160 (self-dual)
     Tr(L1)/Tr(L0) = {Fraction(int(tr_L1), int(tr_L0))} (gauge/gravity ratio)

  4. GRAVITATIONAL SECTOR:
     L0 = 0 + 10*P_24 + 16*P_15
     Uniform curvature: R = 12 at every vertex
     S_EH/S_YM = {Fraction(int(tr_L0), tr_gauge)} (gravity/gauge hierarchy)

  5. KEY INSIGHT:
     The ratio a_0/a_2 = {ratio_a0_a2} is a PURE NUMBER determined
     entirely by the W33 graph combinatorics. In the spectral action:
       Lambda_cc / M_Planck^2 ~ (f_4/f_2) * {ratio_a0_a2}
     The hierarchy between the cosmological constant and the Planck
     scale is controlled by the cutoff function moments f_4/f_2,
     while the GEOMETRIC factor {ratio_a0_a2} is fixed by W33.

  6. SPECTRAL SIMPLICITY:
     The entire physics of W33 is encoded in just 4 numbers:
       eigenvalues: 0, 4, 10, 16
       multiplicities: 82, 280, 48, 30
     This extreme spectral economy (only 4 distinct eigenvalues
     across all 440 DOFs) is a unique feature of W33 = GQ(3,3).
"""
    )

    results = {
        "a_0": int(a_0),
        "a_2": float(a_2),
        "a_2_rational": str(a_2_frac),
        "a_0_over_a_2": float(ratio_a0_a2),
        "a_0_over_a_2_rational": str(ratio_a0_a2),
        "tr_L0": float(tr_L0),
        "tr_L1": float(tr_L1),
        "tr_L2": float(tr_L2),
        "tr_total": float(tr_total),
        "n_zero": int(n_zero),
        "n_at_4": int(n_at_4),
        "n_at_10": int(n_at_10),
        "n_at_16": int(n_at_16),
        "avg_eigenvalue": float(avg_eigenvalue),
        "elapsed_seconds": time.time() - t0,
    }

    out_dir = Path(__file__).resolve().parent.parent / "checks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"PART_CXI_cosmological_constant_{int(time.time())}.json"
    with open(fname, "w") as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder, default=str)
    print(f"  Wrote: {fname}")
    print(f"  Elapsed: {time.time() - t0:.1f}s")

    return results


if __name__ == "__main__":
    main()
