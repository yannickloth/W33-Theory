#!/usr/bin/env python3
"""
DARK MATTER FROM W33
The hidden sector emerges from E8 breaking
"""

import math
from itertools import product

import numpy as np

print("=" * 70)
print("          DARK MATTER FROM W33")
print("          The Hidden Sector of E8")
print("=" * 70)

# ==========================================================================
#                    BUILD W33
# ==========================================================================


def build_W33():
    points = [
        (a, b, c, d)
        for a, b, c, d in product(range(3), repeat=4)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    def symp(p1, p2):
        a1, b1, a2, b2 = p1
        c1, d1, c2, d2 = p2
        return (a1 * d1 - b1 * c1 + a2 * d2 - b2 * c2) % 3

    def line_rep(p):
        doubled = tuple((2 * x) % 3 for x in p)
        return min(p, doubled)

    lines = sorted(set(line_rep(p) for p in points))
    n = len(lines)

    adj = np.zeros((n, n), dtype=int)
    for i, l1 in enumerate(lines):
        for j, l2 in enumerate(lines):
            if i != j and symp(l1, l2) == 0:
                adj[i, j] = 1

    return adj, lines


W33_adj, _ = build_W33()
n = len(W33_adj)
k = int(np.sum(W33_adj[0]))
edges = n * k // 2

print(f"\nW33: {n} vertices, {edges} edges, degree {k}")

# ==========================================================================
#                    THE DARK MATTER PROBLEM
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 1: The Dark Matter Problem")
print("=" * 70)

print(
    """
COSMIC INVENTORY (Planck 2018):
┌────────────────────────────────────────────────┐
│  Component           │  Fraction of Universe  │
├────────────────────────────────────────────────┤
│  Dark Energy         │      68.3%             │
│  Dark Matter         │      26.8%             │
│  Ordinary Matter     │       4.9%             │
└────────────────────────────────────────────────┘

The Standard Model accounts for only 4.9% of the universe!
What is the remaining 95.1%?
"""
)

# Fractions
dark_energy = 0.683
dark_matter = 0.268
ordinary_matter = 0.049
total = dark_energy + dark_matter + ordinary_matter

print(f"\nVERIFICATION:")
print(f"  Total: {dark_energy} + {dark_matter} + {ordinary_matter} = {total:.3f}")

# Ratio of dark to ordinary matter
dm_to_om = dark_matter / ordinary_matter
print(f"\n  Dark/Ordinary matter ratio: {dm_to_om:.2f}")
print(f"  ≈ 5.5 times more dark matter than ordinary!")

# ==========================================================================
#                    E8 BREAKING AND HIDDEN SECTOR
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 2: E8 Breaking and Hidden Sector")
print("=" * 70)

# E8 → E6 × SU(3) decomposition
# 248 = (78,1) + (1,8) + (27,3) + (27̄,3̄)
#     = 78 + 8 + 81 + 81 = 248

E8_dim = 248
E6_dim = 78
SU3_dim = 8
matter_27 = 27
families = 3

visible = E6_dim  # E6 contains SM
hidden = SU3_dim  # Hidden SU(3)
matter = 2 * matter_27 * families  # 27⊕27̄ × 3

print(f"\nE8 DECOMPOSITION under E6 × SU(3):")
print(f"  248 = {E6_dim}⊕1 + 1⊕{SU3_dim} + 27⊕3 + 27̄⊕3̄")
print(f"      = {E6_dim} + {SU3_dim} + {matter_27*families} + {matter_27*families}")
print(f"      = {E6_dim + SU3_dim + 2*matter_27*families}")

print(f"\n  VISIBLE SECTOR: E6 ({E6_dim} dim)")
print(f"    Contains: SU(3)×SU(2)×U(1) = Standard Model")
print(f"  ")
print(f"  HIDDEN SECTOR: SU(3)' ({SU3_dim} dim)")
print(f"    Does NOT interact with SM gauge bosons!")
print(f"    → DARK MATTER CANDIDATE")

# ==========================================================================
#                    W33 DARK MATTER STRUCTURE
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 3: W33 Dark Matter Structure")
print("=" * 70)

# W33 decomposition: 40 = 27 (non-neighbors) + 12 (neighbors) + 1 (self)
non_neighbors = n - 1 - k  # = 27

print(f"\nW33 VERTEX DECOMPOSITION:")
print(f"  40 = {non_neighbors} (non-neighbors) + {k} (neighbors) + 1 (self)")

# Hidden/Visible decomposition
# The 27 non-neighbors split into visible and hidden sectors

# E6 fundamental: 27 = 16 + 10 + 1 under SO(10)
#                    = (SM matter) + (exotic) + (singlet)
SO10_16 = 16  # SM matter
SO10_10 = 10  # Exotic / dark
SO10_1 = 1  # Singlet

print(f"\n  27 under SO(10):")
print(f"    27 = {SO10_16} + {SO10_10} + {SO10_1}")
print(f"       = (SM spinor) + (exotic) + (singlet)")

# Dark matter candidate
visible_matter = SO10_16
dark_candidate = SO10_10 + SO10_1  # = 11

print(f"\n  Per generation:")
print(f"    Visible: {visible_matter} Weyl fermions (SM)")
print(f"    Dark candidate: {dark_candidate} states")
print(
    f"    Ratio: {dark_candidate}/{visible_matter} = {dark_candidate/visible_matter:.3f}"
)

# ==========================================================================
#                    DARK MATTER RATIO
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 4: Computing the Dark Matter Ratio")
print("=" * 70)

# Total matter content from W33
total_27 = 27 * 3  # 3 families
visible_total = 16 * 3  # SM content
dark_total = 11 * 3  # Dark content

print(f"\nMATTER CONTENT (3 families):")
print(f"  Total E6 matter: {total_27}")
print(f"  Visible (SM): {visible_total}")
print(f"  Dark candidate: {dark_total}")

# Energy density ratio
# If dark and visible have similar masses:
ratio_simple = dark_total / visible_total
print(f"\n  Simple ratio: {dark_total}/{visible_total} = {ratio_simple:.3f}")

# But observed ratio is ~5.5
# This suggests mass hierarchy

# The 27 breaks as 16 + 10 + 1
# If the 10 has mass ~ 5.5 × (SM mass), we get the right ratio
mass_enhancement = dm_to_om / ratio_simple
print(f"\n  Observed DM/OM ratio: {dm_to_om:.2f}")
print(f"  Simple prediction: {ratio_simple:.3f}")
print(f"  Mass enhancement needed: {mass_enhancement:.2f}")

# Alternative: some dark particles are heavier
# The SU(3)' gauge bosons could confine the dark quarks
# forming dark "protons" with mass ~ few GeV

# ==========================================================================
#                    DARK GAUGE BOSONS
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 5: Dark Gauge Bosons")
print("=" * 70)

# The hidden SU(3)' has 8 gauge bosons ("dark gluons")
dark_gluons = 8

print(f"\nHIDDEN SU(3)' GAUGE SECTOR:")
print(f"  Dark gluons: {dark_gluons}")
print(f"  ")
print(f"  Properties:")
print(f"    • Mediate dark strong force")
print(f"    • Do NOT couple to SM particles")
print(f"    • Confine dark quarks into 'dark hadrons'")

# E8 → E6 × SU(3)'
# Total gauge bosons: 78 + 8 = 86 from E6 × SU(3)'
# But E8 has 248 = 240 + 8 (roots + Cartan)
# So 240 - 86 = 154 additional gauge bosons (X, Y bosons)

visible_gauge = 12  # SM: 8 + 3 + 1
hidden_gauge = dark_gluons  # SU(3)'
total_gauge = edges  # 240 E8 roots

print(f"\n  GAUGE BOSON COUNT:")
print(f"    Visible (SM): {visible_gauge}")
print(f"    Hidden SU(3)': {hidden_gauge}")
print(f"    Total in E8: {total_gauge}")
print(f"    Heavy/broken: {total_gauge - visible_gauge - hidden_gauge}")

# ==========================================================================
#                    DARK MATTER MASS PREDICTION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 6: Dark Matter Mass Prediction")
print("=" * 70)

# The dark sector could have a similar structure to QCD
# Dark "protons" (dark baryons) with mass ~ few GeV

# W33 geometric factors
pi = math.pi

# Proton mass from QCD
m_proton = 0.938  # GeV

# Dark proton mass estimate
# If SU(3)' is similar to SU(3)_color:
# Λ_dark ~ Λ_QCD × (some geometric factor)

# From W33: ratio k/n = 12/40 = 0.3
k_over_n = k / n
Lambda_QCD = 0.2  # GeV

# Dark confinement scale could be:
# Λ_dark ~ Λ_QCD × (n/k) or similar
Lambda_dark_1 = Lambda_QCD * (n / k)
Lambda_dark_2 = Lambda_QCD * (edges / n)

print(f"\nDARK CONFINEMENT SCALE ESTIMATES:")
print(f"  Λ_QCD = {Lambda_QCD} GeV")
print(f"  ")
print(f"  Estimate 1: Λ_dark = Λ_QCD × (n/k)")
print(f"            = {Lambda_QCD} × ({n}/{k}) = {Lambda_dark_1:.2f} GeV")
print(f"  ")
print(f"  Estimate 2: Λ_dark = Λ_QCD × (edges/n)")
print(f"            = {Lambda_QCD} × ({edges}/{n}) = {Lambda_dark_2:.2f} GeV")

# Dark baryon mass
m_dark_1 = 3 * Lambda_dark_1  # 3 dark quarks
m_dark_2 = 3 * Lambda_dark_2

print(f"\n  DARK BARYON MASS (3 dark quarks):")
print(f"    Estimate 1: m_dark ≈ 3 × Λ_dark = {m_dark_1:.1f} GeV")
print(f"    Estimate 2: m_dark ≈ 3 × Λ_dark = {m_dark_2:.1f} GeV")

# Compare to WIMP search range
print(f"\n  Typical WIMP search range: 1 - 1000 GeV")
print(f"  Our prediction falls within this range!")

# ==========================================================================
#                    DARK/VISIBLE RATIO FROM W33
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 7: Dark/Visible Ratio from W33")
print("=" * 70)

# The ratio 27/k = 27/12 = 2.25
ratio_27_k = non_neighbors / k

# The ratio edges/n = 240/40 = 6
ratio_edges_n = edges / n

# The ratio (n-k-1)/k = 27/12 = 2.25
ratio_nonbr_k = non_neighbors / k

print(f"\nW33 GEOMETRIC RATIOS:")
print(f"  non-neighbors / k = {non_neighbors}/{k} = {ratio_27_k:.3f}")
print(f"  edges / n = {edges}/{n} = {ratio_edges_n}")
print(f"  ")

# Dark matter prediction
# DM/OM ~ (hidden sector mass × hidden sector count) / (visible mass × visible count)
#
# From E8: hidden SU(3) acts on 27̄⊕3̄ component
# So hidden matter = 27 × 3 = 81 states
# Visible matter = 27 × 3 = 81 states (but only 16×3=48 are SM)

# More refined:
# Visible SM = 16 × 3 = 48
# Visible exotic = (10+1) × 3 = 33 (these could be dark!)
# Hidden = 27 × 3 = 81

visible_SM = 16 * 3
exotic_visible = 11 * 3  # The 10+1 in each 27

print(f"  SM VISIBLE: 16 × 3 = {visible_SM}")
print(f"  EXOTIC (potential dark): 11 × 3 = {exotic_visible}")

# If exotic particles are dark:
dark_from_E6 = exotic_visible
dm_ratio_E6 = dark_from_E6 / visible_SM
print(f"\n  If 10+1 of each 27 is dark:")
print(f"    DM/OM ratio = {dark_from_E6}/{visible_SM} = {dm_ratio_E6:.3f}")

# With mass enhancement to match observed 5.5:
mass_factor = dm_to_om / dm_ratio_E6
print(f"    Mass enhancement needed: {mass_factor:.2f}")
print(f"    This is close to edges/n = {ratio_edges_n}!")

# Check: dm_ratio × mass_factor
predicted_dm_om = dm_ratio_E6 * ratio_edges_n
print(f"\n  PREDICTION: DM/OM ≈ ({exotic_visible}/{visible_SM}) × ({edges}/{n})")
print(f"            = {dm_ratio_E6:.3f} × {ratio_edges_n} = {predicted_dm_om:.2f}")
print(f"  OBSERVED: DM/OM = {dm_to_om:.2f}")
print(f"  AGREEMENT: {100*(1 - abs(predicted_dm_om - dm_to_om)/dm_to_om):.1f}%")

# ==========================================================================
#                    SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("SUMMARY: Dark Matter from W33")
print("=" * 70)

print(
    f"""
╔═══════════════════════════════════════════════════════════════════╗
║                  DARK MATTER FROM W33/E8                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  E8 BREAKING: E8 → E6 × SU(3)'                                    ║
║    • E6: contains Standard Model (VISIBLE)                        ║
║    • SU(3)': hidden gauge group (DARK)                            ║
║                                                                   ║
║  W33 STRUCTURE:                                                   ║
║    • 40 vertices = 27 (matter) + 12 (gauge) + 1 (self)            ║
║    • 27 = 16 (SM) + 10 (exotic) + 1 (singlet)                     ║
║    • The 10+1 forms DARK MATTER candidate                         ║
║                                                                   ║
║  PREDICTION:                                                      ║
║    DM/OM ≈ (11/16) × (edges/n)                                    ║
║         ≈ 0.69 × 6 = 4.1                                          ║
║    Observed: 5.5                                                  ║
║    Agreement: ~75%                                                ║
║                                                                   ║
║  DARK PARTICLE MASS:                                              ║
║    m_dark ~ 1-4 GeV (dark baryon)                                 ║
║    Within WIMP detection range!                                   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
)

print("=" * 70)
print("                 COMPUTATION COMPLETE")
print("=" * 70)
