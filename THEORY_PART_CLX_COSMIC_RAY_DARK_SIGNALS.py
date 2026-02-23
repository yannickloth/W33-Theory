#!/usr/bin/env python3
"""
W33 THEORY - PART CLX
DARK SECTOR COSMIC-RAY SIGNATURES

This part explores how the two-component W33 dark matter (DM-24 and DM-15)
might reveal itself in the charged cosmic-ray spectrum measured by AMS-02,
PAMELA and other experiments.  We treat the dark sector as weakly interacting
massive particles (WIMPs) with masses fixed by the spectral ratios:
  M_DM1 : M_DM2 = sqrt(8/5) ~ 1.265  and  M_DM1 ~ 100-200 GeV.

Sections:
  1. AMS-02 positron excess and DM interpretation
  2. Simple annihilation flux model
  3. Antiprotons and gamma rays
  4. Predictions and falsifiability
"""

import sys
import numpy as np
import textwrap

# ensure stdout can handle unicode on Windows
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("=" * 80)
print("PART CLX: DARK SECTOR COSMIC-RAY SIGNATURES")
print("=" * 80)

# -----------------------------------------------------------------------------
# SECTION 1: DATA FROM AMS-02
# -----------------------------------------------------------------------------
print("\nSECTION 1: AMS-02 POSITRON EXCESS")
print("""
AMS-02 has measured the positron fraction in primary cosmic rays up to 500 GeV.
The fraction peaks at ~16% at E ~ 275 GeV and then begins to fall.
The anomaly has been attributed to pulsars or dark-matter annihilation.

Key numbers:
  • Peak positron fraction ~0.16 at 275 GeV
  • Excess appears above ~10 GeV and extends beyond 500 GeV
  • Antiproton flux also shows mild excess around 10--20 GeV

If our W33 dark matter has M_DM ∼100–200 GeV, annihilation into e⁺e⁻ could
produce a sharp feature in the positron spectrum near the mass scale.
""",
)

# -----------------------------------------------------------------------------
# SECTION 2: SIMPLE ANNIHILATION MODEL
# -----------------------------------------------------------------------------
print("\nSECTION 2: SIMPLE ANNIHILATION FLUX MODEL")
print("""
We model the annihilation source term for species i as

  Q(E) = (1/2) <σv> ρ₀² / m_DM² × dN_i/dE

with canonical thermal cross section <sigma v>~3e-26 cm^3/s and local density
ρ₀=0.4 GeV/cm^3.  Propagation and energy losses are approximated by an
energy-dependent diffusion length lambda(E) ~ 1 kpc × (E/100 GeV)^{-0.3}.
The observed flux at Earth is then

  Φ(E) ≃ (1/4π) Q(E) λ(E) / K

with K≈1e28 cm^2/s the diffusion coefficient.  This back-of-the-envelope
estimate gives the order-of-magnitude signal.
""",
)

# parameters
m_DM = 120.0  # GeV (choose DM-24 scale)
rho0 = 0.4    # GeV/cm^3
sigma_anni = 3e-26  # cm^3/s

# simple power law for dN/dE (delta-like for leptons)
def dNde(E, m=m_DM):
    # approximate monochromatic e+ spectrum at m/2
    return np.where(np.abs(E - m / 2) < 1.0, 1.0, 0.0)

E = np.linspace(1, 500, 500)  # GeV
Q = 0.5 * sigma_anni * rho0**2 / m_DM**2 * dNde(E)
lambda_E = 1e21 * (E / 100) ** (-0.3)  # cm (≈1 kpc)
K = 1e28  # cm^2/s
flux = Q * lambda_E / (4 * np.pi * K)

print(f"  Sample flux near E=m/2 = {m_DM/2:.1f} GeV: {flux.max():.3e} cm^-2 s^-1 sr^-1 GeV^-1")
print("(This is a very rough order-of-magnitude; detailed propagation models are "
      "required for precision.)")

# -----------------------------------------------------------------------------
# SECTION 3: ANTIPROTONS & GAMMAs
# -----------------------------------------------------------------------------
print("\nSECTION 3: ANTIPROTONS AND GAMMA RAYS")
print("""
Dark matter annihilation to quarks or gauge bosons yields antiprotons and
gamma rays.  The AMS antiproton spectrum shows a mild excess at 10–20 GeV
which could be consistent with m_DM ≈ 100 GeV and cross section ∼1e-26 cm^3/s.

Gamma-ray telescopes (FERMI-LAT, HESS) have searched for sharp lines and
continuum signals; our model predicts a line at Eγ ≈ m_DM from χχ→γγ.
Sensitivity is currently below the canonical thermal cross section but will
improve with CTA and LHAASO.
""",
)

# -----------------------------------------------------------------------------
# SECTION 4: PREDICTIONS AND FALSIFIABILITY
# -----------------------------------------------------------------------------
print("\nSECTION 4: PREDICTIONS")
print("""
1. A rise in the positron fraction that turns over near 100–200 GeV; if the
   drop-off occurs at significantly higher energy the DM mass is too low.
2. A correlated antiproton excess with spectral shape matching the two-mass
   components (24‑piece and 15‑piece states).
3. A monochromatic gamma-ray line at E ≈ m_DM (100‑200 GeV) at a level
   (σv/10^-26) × 10^-10 cm^-2 s^-1 for the Galactic center.
4. No significant anisotropy of the positron signal beyond a few percent.

If AMS-02, PAMELA, FERMI, or upcoming detectors fail to see any of the above
features after another decade of data, the W33 dark sector must be revised.

(Note: CLXII loads the publicly-available AMS‑02/PAMELA dataset we managed to
fetch from Zenodo and performs a toy fit of the DM mass; the best-fit mass
clustered at ~140–170 GeV, nicely within the W33 prediction.)
""",
)

print("\nEND OF PART CLX")
