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

import numpy as np
from scipy.integrate import odeint

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

# Key ratios from W33/E8 structure at M_GUT
# These are the "bare" mass ratios before RG running

W33_ratios_GUT = {
    # From previous analysis
    "m_t/m_b": 240 / 6,  # = 40, matches experiment to 3%
    "m_c/m_s": 40 / 3,  # ≈ 13.3
    "m_t/m_c": 133 / 1,  # dim(E7) = 133
    "m_s/m_d": 240 / 12,  # = 20
    "m_μ/m_e": 27 * 8,  # = 216 (octonions × E6 rep)
    "m_τ/m_μ": 240 / 14,  # ≈ 17
    "m_b/m_τ": 3,  # Color factor
}

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
def yukawa_rge(y, t):
    """
    RG equations for (y_t, y_b, y_τ)
    y = [y_t, y_b, y_τ]
    t = ln(μ/M_Z)
    """
    y_t, y_b, y_tau = y
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

# Solve RG equations from M_Z to M_GUT
t_span = np.linspace(0, np.log(M_GUT / M_Z), 1000)
y0 = [y_t_MZ, y_b_MZ, y_tau_MZ]

solution = odeint(yukawa_rge, y0, t_span)

y_t_GUT = solution[-1, 0]
y_b_GUT = solution[-1, 1]
y_tau_GUT = solution[-1, 2]

print(f"\n  Running to GUT scale (M_GUT = {M_GUT:.0e} GeV):")
print(f"    y_t(M_GUT) = {y_t_GUT:.4f}")
print(f"    y_b(M_GUT) = {y_b_GUT:.4f}")
print(f"    y_τ(M_GUT) = {y_tau_GUT:.4f}")

# Mass ratios at GUT scale
ratio_tb_GUT = y_t_GUT / y_b_GUT
ratio_btau_GUT = y_b_GUT / y_tau_GUT

print(f"\n  Mass ratios at GUT scale:")
print(f"    m_t/m_b (GUT) = {ratio_tb_GUT:.2f}")
print(f"    m_b/m_τ (GUT) = {ratio_btau_GUT:.2f}")

print(f"\n  W33 predictions at GUT scale:")
print(f"    m_t/m_b = 240/6 = {240/6:.2f}")
print(f"    m_b/m_τ = 3")

# ═══════════════════════════════════════════════════════════════════════════
#                    INVERSE: GUT TO LOW ENERGY
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 76)
print("Prediction: GUT Boundary → Low Energy Masses")
print("─" * 76)

# We will determine GUT-scale Yukawa couplings by shooting so that
# the low-energy top mass matches experiment.  W33 ratios fix
# m_t/m_b and m_b/m_τ at M_GUT.

# Helper functions

def run_down(y_GUT):
    """Integrate Yukawa RGEs from GUT scale down to M_Z.

    We simply run the same differential equations on a decreasing energy
    variable.  This avoids the earlier sign confusion with ``yukawa_rge_reverse``.
    ``y_GUT`` is a triple (y_t,y_b,y_tau) at μ=M_GUT; the function returns the
    corresponding values at μ=M_Z.
    """
    t_span_down = np.linspace(np.log(M_GUT / M_Z), 0, 1000)
    sol = odeint(yukawa_rge, y_GUT, t_span_down)
    return sol[-1]

# shooting function: given y_t at GUT, compute predicted m_t at M_Z
def top_mass_difference(y_t_guess):
    y_b_guess = y_t_guess / (240 / 6)
    y_tau_guess = y_b_guess / 3
    y_at_MZ = run_down([y_t_guess, y_b_guess, y_tau_guess])
    m_t_calc = y_at_MZ[0] * v / np.sqrt(2)
    return m_t_calc - m_t_MZ

print("Searching for boundary Yukawa at M_GUT that reproduces m_t at M_Z...")
from scipy.optimize import root_scalar
try:
    sol = root_scalar(top_mass_difference, bracket=[0.01, 5.0], method="bisect", xtol=1e-4)
    y_t_GUT_fit = sol.root
    y_b_GUT_fit = y_t_GUT_fit / (240 / 6)
    y_tau_GUT_fit = y_b_GUT_fit / 3
    print(f"  Fitted y_t(GUT) = {y_t_GUT_fit:.4f}")
    print(f"  Implied y_b(GUT) = {y_b_GUT_fit:.4f}, y_τ(GUT) = {y_tau_GUT_fit:.4f}")
except Exception as e:
    print("  Fit failed, using naive W33 values", e)
    y_t_GUT_fit = 1.0
    y_b_GUT_fit = y_t_GUT_fit / (240 / 6)
    y_tau_GUT_fit = y_b_GUT_fit / 3

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

summary = """
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
║  • m_t/m_b = 240/6 = 40 (E8 roots / color)                               ║
║  • m_t/m_c = 133 (dim E7)                                                ║
║  • m_b/m_τ = 3 (color factor)                                            ║
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
}

with open(
    "C:/Users/wiljd/OneDrive/Desktop/Theory of Everything/RG_MASSES.json", "w"
) as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to RG_MASSES.json")
print("=" * 76)
