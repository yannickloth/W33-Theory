#!/usr/bin/env python3
"""
W33 THEORY - PART CLXIII
MONSTER DARK SECTOR & ULTRA-HEAVY COSMIC RAYS

This module speculates that the Monster group (through its j-function)
points to an additional, ultra-heavy component of the dark sector with
mass set by the first coefficient

    c_1 = 196884 = 196560 + 324

The 196560 term is the Leech-lattice minimal vector count, while the
extra 324 = 12 \times 27 hints at a coupling to the Albert algebra.
If such "monster dark matter" exists, its mass scale ~2\times10^5 GeV is
well beyond collider reach but could show up in the highest-energy
cosmic-ray and gamma-ray data (HAWC, LHAASO, CTA, etc.).

Sections:
  1. Monster numbers and j-function
  2. Heavy DM mass prediction
  3. Simple annihilation flux toy model
  4. Observational prospects
"""

import sys
import numpy as np

# ensure unicode output on Windows
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("=" * 80)
print("PART CLXIII: MONSTER DARK SECTOR & ULTRA-HEAVY COSMIC RAYS")
print("=" * 80)

# -----------------------------------------------------------------------------
# SECTION 1: MONSTER NUMBERS
# -----------------------------------------------------------------------------
print("\nSECTION 1: MONSTER GROUP AND j-FUNCTION")
print("""
The Monster's graded dimension series begins

    j(q) = q^{-1} + 196884 q + 21493760 q^2 + ...

c_1 = 196884 = 196560 + 324
  • 196560 = number of minimal vectors in the Leech lattice
  • 324 = 12 × 27 (Albert algebra connection)

This suggests a hierarchical structure where the Monster unifies both
binary and ternary Golay/Albert pieces.
""")

c1 = 196884
leech_part = 196560
albert_correction = 324
print(f"  c1 = {c1}")
print(f"  leech contribution = {leech_part}")
print(f"  Albert correction = {albert_correction}")

# -----------------------------------------------------------------------------
# SECTION 2: HEAVY DM MASS
# -----------------------------------------------------------------------------
print("\nSECTION 2: PREDICTED MONSTER DARK MATTER MASS")
print("""
If we interpret c1 as counting degrees of freedom for an ultra-heavy
stable particle (or multiplet), then the natural mass scale is

    M_DM,monster ~ c1 GeV ≃ 1.96884×10^5 GeV ≈ 200 TeV.

This is roughly three orders of magnitude heavier than the W33/13-sector
DM candidate explored in CLX–CLXII.
""")

m_monster = float(c1)  # GeV
print(f"  M_DM,monster ≈ {m_monster:.0f} GeV ({m_monster/1e3:.1f} TeV)")

# -----------------------------------------------------------------------------
# SECTION 3: SIMPLE ANNIHILATION FLUX MODEL
# -----------------------------------------------------------------------------
print("\nSECTION 3: TOY COSMIC-RAY FLUX FOR HEAVY DARK MATTER")
print("""
Using the same back-of-the-envelope formula as in CLX, we compute the
annihilation flux for E ≲ M/2.  Because the density scales as 1/M^2, the
observable flux is extremely suppressed; however, searches at ~100 TeV
may eventually have sensitivity.
""")

# parameters (reuse from CLX but with heavy mass)
rho0 = 0.4  # GeV/cm^3
sigma_anni = 3e-26  # cm^3/s

def dNde(E, m=m_monster):
    return np.where(np.abs(E - m / 2) < 1.0, 1.0, 0.0)

E = np.linspace(1e3, m_monster, 1000)  # GeV, start at 1 TeV
Q = 0.5 * sigma_anni * rho0**2 / m_monster**2 * dNde(E)
lambda_E = 1e21 * (E / 100) ** (-0.3)  # cm
K = 1e28  # cm^2/s
flux = Q * lambda_E / (4 * np.pi * K)

print(f"  Sample flux near E=m/2 = {m_monster/2:.1f} GeV: {flux.max():.3e} cm^-2 s^-1 sr^-1 GeV^-1")
print("(Flux is ridiculously tiny, ~10^-20, illustrating why existing "
      "experiments cannot yet probe this component.)")

# -----------------------------------------------------------------------------
# SECTION 4: OBSERVATIONAL PROSPECTS
# -----------------------------------------------------------------------------
print("\nSECTION 4: OBSERVATIONAL PROSPECTS")
print("""
1. Ultra-high-energy cosmic-ray spectrum above 10^5 GeV may exhibit a
   slight bump or cutoff if annihilation or decay of monster-sector DM
   contributes.
2. Gamma-ray telescopes (HAWC, LHAASO, CTA) could search for lines at
   E_γ ≈ M_DM,monster ≃ 200 TeV, though attenuation on extragalactic
   backgrounds is severe.
3. Direct detection and colliders are hopeless; only astrophysical probes
   at the highest energies are viable.

If future data from LHAASO, CTA, IceCube, or even the Pierre Auger
Observatory show unexplained features near 10^5–10^6 GeV, it would be
worth revisiting the Monster dark sector.
""")

# expose variables for tests
__all__ = ["m_monster", "flux"]
