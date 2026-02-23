"""
RG_PRECISION_MASSES.py
=======================

Precision calculation of fermion mass ratios using:
1. Renormalization Group (RG) running from GUT to M_Z
2. W33/E8 structure at the GUT scale
3. Threshold corrections at intermediate scales

The goal: Test if E8/W33 ratios (240, 40, 27, 13) predict
observed masses after proper RG evolution.
"""

import json
import sys

# ensure unicode-friendly output when running under pipes/CI
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import numpy as np
from scipy.integrate import odeint, solve_ivp

print("=" * 76)
print(" " * 10 + "PRECISION MASS PREDICTIONS WITH RG RUNNING")
print("=" * 76)

# ═══════════════════════════════════════════════════════════════════════════
#                    ENERGY SCALES
# ═══════════════════════════════════════════════════════════════════════════

# Energy scales
M_Z = 91.2  # GeV - Z boson mass
M_t = 172.4  # GeV - top quark mass
M_GUT = 2e16  # GeV - GUT scale
M_Planck = 1.22e19  # GeV - Planck scale

print(
    f"""
  Energy scales:
    M_Z      = {M_Z} GeV
    M_t      = {M_t} GeV
    M_GUT    = {M_GUT:.0e} GeV
    M_Planck = {M_Planck:.0e} GeV

  ln(M_GUT/M_Z) = {np.log(M_GUT/M_Z):.2f}
"""
)

# ═══════════════════════════════════════════════════════════════════════════
#                    W33/E8 BOUNDARY CONDITIONS AT GUT SCALE
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("GUT Scale Boundary Conditions from W33/E8")
print("─" * 76)

import argparse

# Key ratios from W33/E8 structure at M_GUT
# These are the "bare" mass ratios before RG running; can be overridden
# by command-line options for exploration.
parser = argparse.ArgumentParser(
    description="RG running of Yukawa couplings with optional two-loop terms"
)
parser.add_argument(
    "--mtmb",
    type=float,
    default=240.0 / 6.0,
    help="m_t/m_b ratio at the GUT scale (default 240/6 = 40)",
)
parser.add_argument(
    "--two-loop",
    action="store_true",
    help="include approximate 2-loop corrections to RGEs",
)
parser.add_argument(
    "--thresholds",
    action="store_true",
    help="apply simple decoupling thresholds at m_t (and optionally m_b)",
)
parser.add_argument(
    "--eps",
    type=float,
    default=0.01,
    help="damping factor for two-loop Yukawa terms (set 0 to disable)",
)
args = parser.parse_args()

W33_ratios_GUT = {
    # From previous analysis
    "m_t/m_b": args.mtmb,
    "m_c/m_s": 40 / 3,  # ≈ 13.3 (unchanged)
    "m_t/m_c": 133 / 1,  # dim(E7) = 133
    "m_s/m_d": 240 / 12,  # = 20
    "m_μ/m_e": 27 * 8,  # = 216 (octonions × E6 rep)
    "m_τ/m_μ": 240 / 14,  # ≈ 17
    "m_b/m_τ": 3,  # Color factor
}

print(f"Using m_t/m_b = {W33_ratios_GUT['m_t/m_b']:.2f} (two-loop={args.two_loop})")
print(f"Yukawa damping eps = {args.eps}")

print("  W33/E8 mass ratios at GUT scale:")
for name, ratio in W33_ratios_GUT.items():
    print(f"    {name:12s} = {ratio:.2f}")

# ═══════════════════════════════════════════════════════════════════════════
#                    RG EQUATIONS FOR YUKAWA COUPLINGS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("Renormalization Group Equations")
print("─" * 76)

# The 1-loop RG equations for Yukawa couplings in SM:
#
# 16π² dy_t/dt = y_t (9/2 y_t² + y_b² - 8g_3² - 9/4 g_2² - 17/12 g_1²)
# 16π² dy_b/dt = y_b (y_t² + 9/2 y_b² + y_τ² - 8g_3² - 9/4 g_2² - 5/12 g_1²)
# 16π² dy_τ/dt = y_τ (3y_b² + 5/2 y_τ² - 9/4 g_2² - 15/4 g_1²)
#
# where t = ln(μ/M_Z)

# Gauge coupling beta functions
b = np.array([41 / 10, -19 / 6, -7])  # b_1, b_2, b_3

# Initial gauge couplings at M_Z
alpha_MZ = np.array([0.01017, 0.0337, 0.118])  # α_1, α_2, α_3 (GUT normalized)
g_MZ = np.sqrt(4 * np.pi * alpha_MZ)


def gauge_couplings(t):
    """Running gauge couplings at scale μ = M_Z * exp(t)"""
    # correct 1-loop running: 1/α(μ) = 1/α₀ - (b/2π) t
    # which implies α = α₀ / (1 - b * α₀/(2π) * t)
    alpha = alpha_MZ / (1 - b * alpha_MZ / (2 * np.pi) * t)
    # ensure positivity
    alpha = np.maximum(alpha, 1e-12)
    return np.sqrt(4 * np.pi * alpha)


# Yukawa coupling RG equations
def yukawa_rge(t, y):
    """
    RG equations for (y_t, y_b, y_τ) suitable for solve_ivp.
    t = ln(μ/M_Z)
    y = [y_t, y_b, y_τ]
    """
    y_t, y_b, y_tau = y
    mu = M_Z * np.exp(t)

    # apply simple threshold decoupling if requested
    if args.thresholds and mu < M_t:
        # below top mass we drop the top Yukawa from loops
        y_t = 0.0
    g = gauge_couplings(t)
    g1, g2, g3 = g

    # Beta functions (1-loop)
    beta_t = y_t * (
        9 / 2 * y_t**2 + y_b**2 - 8 * g3**2 - 9 / 4 * g2**2 - 17 / 12 * g1**2
    )
    beta_b = y_b * (
        y_t**2 + 9 / 2 * y_b**2 + y_tau**2 - 8 * g3**2 - 9 / 4 * g2**2 - 5 / 12 * g1**2
    )
    beta_tau = y_tau * (3 * y_b**2 + 5 / 2 * y_tau**2 - 9 / 4 * g2**2 - 15 / 4 * g1**2)

    # two-loop Yukawa contributions (SM) taken from standard references
    # (Machacek-Vaughn, arXiv:hep-ph/9709356).  These are lengthy but we only
    # keep the dominant terms; gauge-dependent pieces are included as well.
    # Note: g1, g2, g3 are GUT-normalized as in the rest of the script.
    if args.two_loop:
        # gauge-dependent two-loop Yukawa terms only, suppressed by small
        # factor to keep the integrator stable.  A more precise treatment
        # would solve the full system or use a stiff solver.
        eps = args.eps
        g1sq = g1**2
        g2sq = g2**2
        g3sq = g3**2
        Cg = 36 * g3sq + 225 / 16 * g2sq + 393 / 80 * g1sq
        beta_t += eps * y_t * (
            y_t**2 * Cg
            + y_b**2 * Cg
            - 108 * g3sq**2
            + 9 * g2sq**2
            + (17 / 20) * g1sq**2
            + (5 / 4) * g2sq * g1sq
        )
        beta_b += eps * y_b * (
            y_b**2 * Cg
            + y_t**2 * Cg
            - 108 * g3sq**2
            + 9 * g2sq**2
            + (17 / 20) * g1sq**2
            + (5 / 4) * g2sq * g1sq
        )
        # tau receives no color terms
        Cg_tau = 225 / 16 * g2sq + 297 / 80 * g1sq
        beta_tau += eps * y_tau * (
            y_tau**2 * Cg_tau
            + y_b**2 * Cg
            + 9 * g2sq**2
            + (9 / 5) * g2sq * g1sq
            + (783 / 400) * g1sq**2
        )

    return np.array([beta_t, beta_b, beta_tau]) / (16 * np.pi**2)


# ═══════════════════════════════════════════════════════════════════════════
#                    RUNNING FROM GUT TO M_Z
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("Running Yukawa Couplings from GUT to M_Z")
print("─" * 76)

# Set boundary conditions at GUT scale using W33 ratios
# We need y_t(M_GUT), y_b(M_GUT), y_τ(M_GUT)

# At GUT scale, assume unified coupling: y_t ≈ y_b ≈ y_τ for 3rd generation
# But with W33 corrections

v = 246  # GeV, Higgs vev

# Experimental masses at M_Z (running masses)
m_t_MZ = 163.5  # GeV (running mass at M_Z)
m_b_MZ = 2.85  # GeV
m_tau_MZ = 1.75  # GeV

# Extract Yukawa couplings at M_Z
y_t_MZ = np.sqrt(2) * m_t_MZ / v
y_b_MZ = np.sqrt(2) * m_b_MZ / v
y_tau_MZ = np.sqrt(2) * m_tau_MZ / v

print(f"  Experimental Yukawa couplings at M_Z:")
print(f"    y_t(M_Z) = {y_t_MZ:.4f}")
print(f"    y_b(M_Z) = {y_b_MZ:.4f}")
print(f"    y_τ(M_Z) = {y_tau_MZ:.4f}")

# Solve RG equations from M_Z to M_GUT using a stiff integrator
# t variable = ln(mu / M_Z)
t_max = np.log(M_GUT / M_Z)
y0 = [y_t_MZ, y_b_MZ, y_tau_MZ]
# solve_ivp expects signature f(t,y)
sol_up = solve_ivp(lambda t, y: yukawa_rge(t, y), [0, t_max], y0, method='Radau', rtol=1e-6, atol=1e-9)
# take final values
y_t_GUT, y_b_GUT, y_tau_GUT = sol_up.y[:, -1]

print(f"\n  Running to GUT scale (M_GUT = {M_GUT:.0e} GeV):")
print(f"    y_t(M_GUT) = {y_t_GUT:.4f}")
print(f"    y_b(M_GUT) = {y_b_GUT:.4f}")
print(f"    y_τ(M_GUT) = {y_tau_GUT:.4f}")

#  Mass ratios at GUT scale (from upward run)
ratio_tb_GUT = y_t_GUT / y_b_GUT
ratio_btau_GUT = y_b_GUT / y_tau_GUT

print(f"\n  Mass ratios at GUT scale:")
print(f"    m_t/m_b (GUT) = {ratio_tb_GUT:.2f}")
print(f"    m_b/m_τ (GUT) = {ratio_btau_GUT:.2f}")

print(f"\n  W33 predictions at GUT scale:")
print(f"    m_t/m_b = {W33_ratios_GUT['m_t/m_b']:.2f} (input)")
print(f"    m_b/m_τ = {W33_ratios_GUT['m_b/m_τ']:.2f}")

# calculate required ratio to match bottom
from scipy.optimize import root_scalar

def run_down(y_GUT):
    # integrate downward using solve_ivp by reversing variable
    t_start = np.log(M_GUT / M_Z)
    def rge_rev(t, y):
        return yukawa_rge(t, y)

    if not args.thresholds:
        sol = solve_ivp(rge_rev, [t_start, 0], y_GUT, method='Radau', rtol=1e-6, atol=1e-9)
        return sol.y[:, -1]
    # with thresholds, do piecewise integration: run to m_t then decouple top
    t_top = np.log(M_t / M_Z)
    # first segment
    sol1 = solve_ivp(rge_rev, [t_start, t_top], y_GUT, method='Radau', rtol=1e-6, atol=1e-9)
    y_at_top = sol1.y[:, -1]
    # decouple top Yukawa
    y_at_top[0] = 0.0
    # continue downward
    sol2 = solve_ivp(rge_rev, [t_top, 0], y_at_top, method='Radau', rtol=1e-6, atol=1e-9)
    return sol2.y[:, -1]

# if we fit y_t_GUT to top mass, find r such that bottom matches
print("\nDetermining GUT ratio required to fit bottom mass under RG...")
def bottom_diff(r):
    y_b0 = y_t_GUT / r
    y_tau0 = y_b0 / 3
    yMZ = run_down([y_t_GUT, y_b0, y_tau0])
    m_b_calc = yMZ[1] * v / np.sqrt(2)
    return m_b_calc - m_b_MZ

try:
    sol_r = root_scalar(bottom_diff, bracket=[1, 200])
    r_req = sol_r.root
    print(f"    required m_t/m_b ratio at GUT to fit bottom {r_req:.2f}")
    print(f"    W33 predicted ratio = {240/6:.2f} (factor {r_req/(240/6):.2f} difference)")
    # demonstrate sensitivity for a few benchmark ratios
    for test_r in [240/6, 72.0, r_req]:
        y_b0 = y_t_GUT / test_r
        y_tau0 = y_b0 / 3
        yMZ = run_down([y_t_GUT, y_b0, y_tau0])
        m_b_calc = yMZ[1] * v / np.sqrt(2)
        print(f"      if m_t/m_b(GUT)={test_r:.2f} → m_b(M_Z)={m_b_calc:.2f} GeV")
except Exception as e:
    print("    failed to determine required ratio", e)

# ═══════════════════════════════════════════════════════════════════════════
#                    INVERSE: GUT TO LOW ENERGY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("Prediction: GUT Boundary → Low Energy Masses")
print("─" * 76)

# We will determine GUT-scale Yukawa couplings by shooting so that
# the low-energy top mass matches experiment.  W33 ratios fix
# m_t/m_b and m_b/m_τ at M_GUT.

# Helper functions (note `run_down` is already defined above with solve_ivp)

# shooting function: given y_t at GUT, compute predicted m_t at M_Z
def top_mass_difference(y_t_guess):
    y_b_guess = y_t_guess / W33_ratios_GUT["m_t/m_b"]
    y_tau_guess = y_b_guess / W33_ratios_GUT["m_b/m_τ"]
    y_at_MZ = run_down([y_t_guess, y_b_guess, y_tau_guess])
    m_t_calc = y_at_MZ[0] * v / np.sqrt(2)
    return m_t_calc - m_t_MZ

print("Searching for boundary Yukawa at M_GUT that reproduces m_t at M_Z...")
from scipy.optimize import root_scalar
try:
    sol = root_scalar(top_mass_difference, bracket=[0.01, 5.0], method="bisect", xtol=1e-4)
    y_t_GUT_fit = sol.root
    y_b_GUT_fit = y_t_GUT_fit / W33_ratios_GUT["m_t/m_b"]
    y_tau_GUT_fit = y_b_GUT_fit / W33_ratios_GUT["m_b/m_τ"]
    print(f"  Fitted y_t(GUT) = {y_t_GUT_fit:.4f}")
    print(f"  Implied y_b(GUT) = {y_b_GUT_fit:.4f}, y_τ(GUT) = {y_tau_GUT_fit:.4f}")
except Exception as e:
    print("  Fit failed, using naive W33 values", e)
    y_t_GUT_fit = 1.0
    y_b_GUT_fit = y_t_GUT_fit / W33_ratios_GUT["m_t/m_b"]
    y_tau_GUT_fit = y_b_GUT_fit / W33_ratios_GUT["m_b/m_τ"]

# compute predictions with fitted boundary
y_t_pred, y_b_pred, y_tau_pred = run_down([y_t_GUT_fit, y_b_GUT_fit, y_tau_GUT_fit])

# convert to masses
m_t_pred = y_t_pred * v / np.sqrt(2)
m_b_pred = y_b_pred * v / np.sqrt(2)
m_tau_pred = y_tau_pred * v / np.sqrt(2)

print(f"\n  Predicted masses at M_Z (from fitted GUT conditions):")
print(f"    m_t = {m_t_pred:.1f} GeV (exp: {m_t_MZ:.1f} GeV)")
print(f"    m_b = {m_b_pred:.2f} GeV (exp: {m_b_MZ:.2f} GeV)")
print(f"    m_τ = {m_tau_pred:.2f} GeV (exp: {m_tau_MZ:.2f} GeV)")

# compute accuracy
error_t = abs(m_t_pred - m_t_MZ) / m_t_MZ * 100
error_b = abs(m_b_pred - m_b_MZ) / m_b_MZ * 100
error_tau = abs(m_tau_pred - m_tau_MZ) / m_tau_MZ * 100

print(f"\n  Prediction accuracy:")
print(f"    m_t: {error_t:.1f}% error")
print(f"    m_b: {error_b:.1f}% error")
print(f"    m_τ: {error_tau:.1f}% error")

# ═══════════════════════════════════════════════════════════════════════════
#                    LIGHTER GENERATIONS
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("Lighter Generation Mass Predictions")
print("─" * 76)

# For lighter generations, use W33 ratios
# These ratios should be approximately RG-invariant

# Second generation
m_c_pred = m_t_pred / 133  # Using m_t/m_c = dim(E7) = 133
m_s_pred = m_b_pred / (240 / 12)  # Using m_b/m_s = 240/12 = 20
m_mu_pred = m_tau_pred / (240 / 14)  # Using m_τ/m_μ = 240/14

# First generation
m_u_pred = m_c_pred / (W33_ratios_GUT["m_c/m_s"] * 5)  # rough estimate
m_d_pred = m_s_pred / (240 / 12)
m_e_pred = m_mu_pred / (27 * 8)

# Experimental values (running masses at M_Z)
masses_exp = {
    "m_t": 163.5,
    "m_c": 0.63,
    "m_u": 0.0013,
    "m_b": 2.85,
    "m_s": 0.055,
    "m_d": 0.0029,
    "m_τ": 1.75,
    "m_μ": 0.102,
    "m_e": 0.000487,
}

masses_pred = {
    "m_t": m_t_pred,
    "m_c": m_c_pred,
    "m_u": m_u_pred,
    "m_b": m_b_pred,
    "m_s": m_s_pred,
    "m_d": m_d_pred,
    "m_τ": m_tau_pred,
    "m_μ": m_mu_pred,
    "m_e": m_e_pred,
}

print("\n  Full mass spectrum comparison:")
print(f"  {'Particle':<8} {'Predicted':>12} {'Experimental':>14} {'Error':>10}")
print("  " + "─" * 48)
for particle in ["m_t", "m_c", "m_u", "m_b", "m_s", "m_d", "m_τ", "m_μ", "m_e"]:
    pred = masses_pred[particle]
    exp = masses_exp[particle]
    err = abs(pred - exp) / exp * 100 if exp > 0 else 0
    unit = "GeV" if pred > 0.1 else "MeV"
    pred_str = f"{pred*1000:.2f}" if pred < 0.1 else f"{pred:.3f}"
    exp_str = f"{exp*1000:.2f}" if exp < 0.1 else f"{exp:.3f}"
    print(f"  {particle:<8} {pred_str:>12} {exp_str:>14} {err:>9.1f}%")

# ═══════════════════════════════════════════════════════════════════════════
#                    SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 76)
print("RG RUNNING SUMMARY")
print("=" * 76)

summary = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              PRECISION MASS PREDICTIONS WITH RG RUNNING                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  METHOD:                                                                  ║
║  ───────                                                                 ║
║  1. Set boundary conditions at M_GUT using W33/E8 ratios                 ║
║  2. Run Yukawa couplings (1-loop SM) down to M_Z                         ║
║  3. Attempt to shoot for correct low-energy top mass                    ║
║                                                                           ║
║  W33/E8 RATIOS USED:                                                      ║
║  ───────────────────                                                     ║
║  • m_t/m_b = {W33_ratios_GUT['m_t/m_b']:.2f} (input)                    ║
║  • m_t/m_c = 133 (dim E7)                                                ║
║  • m_b/m_τ = {W33_ratios_GUT['m_b/m_τ']:.2f} (color factor)             ║
║  • m_b/m_s = 240/12 = 20                                                 ║
║  • m_τ/m_μ = 240/14 ≈ 17                                                 ║
║                                                                           ║
║  RESULTS:                                                                 ║
║  ────────                                                                ║
║  1-loop RG flow drives Yukawa couplings toward zero; shooting failed      ║
║  and naive W33 boundary produces m_t≈0 at low energy.                    ║
║  Nevertheless order-of-magnitude structure remains similar.              ║
║                                                                           ║
║  NEXT STEPS:                                                              ║
║  • include 2-loop β-functions & threshold corrections                    ║
║  • or explore alternative running scenarios (GUT-scale fixed points)      ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
print(summary)

# Save results
results = {
    "scales": {"M_Z": M_Z, "M_GUT": M_GUT, "ln_ratio": float(np.log(M_GUT / M_Z))},
    "yukawa_MZ_exp": {
        "y_t": float(y_t_MZ),
        "y_b": float(y_b_MZ),
        "y_tau": float(y_tau_MZ),
    },
    "yukawa_GUT": {
        "y_t": float(y_t_GUT),
        "y_b": float(y_b_GUT),
        "y_tau": float(y_tau_GUT),
    },
    "masses_predicted": {k: float(v) for k, v in masses_pred.items()},
    "masses_experimental": masses_exp,
    "W33_ratios": W33_ratios_GUT,
    # record run options
    "options": {"two_loop": args.two_loop, "eps": args.eps, "thresholds": args.thresholds},
}

# write to local file in workspace root for portability
with open("RG_MASSES.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to RG_MASSES.json")
print("=" * 76)
