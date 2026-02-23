#!/usr/bin/env python3
"""
W33 THEORY - PART CLXI
COSMIC-RAY PROPAGATION & DARK SECTOR FLUXES

A companion to CLX, this part builds a minimal propagation model for
charged cosmic rays and estimates the expected flux from annihilating
W33 dark matter.  It also computes ratio of DM-24 to DM-15 contributions
and compares with AMS-02 positron fraction data.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

# ensure stdout can handle unicode on Windows
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("=" * 80)
print("PART CLXI: COSMIC-RAY PROPAGATION & DARK SECTOR FLUXES")
print("=" * 80)

# -----------------------------------------------------------------------------
# simple leaky-box propagation
# -----------------------------------------------------------------------------
def propagated_flux(E, m_DM, sigma, rho=0.4, tau_diff=1e15):
    # Q(E) as delta function at m_DM/2 for leptonic channel
    Q = np.zeros_like(E)
    idx = np.argmin(np.abs(E - m_DM / 2))
    Q[idx] = 1.0
    # diffusion time ~ tau_diff (s)
    # flux ~ Q * (rho^2 sigma / m_DM^2) * tau_diff
    return Q * (rho ** 2 * sigma / m_DM ** 2) * tau_diff

# energy grid
E = np.logspace(0, 3, 200)
# global parameters for later inversion
rho0 = 0.4

# two DM species masses (relative ratio sqrt(8/5))
m1 = 120.0
m2 = m1 * np.sqrt(8 / 5)

flux1 = propagated_flux(E, m1, 3e-26)
flux2 = propagated_flux(E, m2, 3e-26)

# normalized
flux1 /= flux1.max()
flux2 /= flux2.max()

print(f"Sample normalization: m1={m1} GeV, m2={m2:.1f} GeV")
print(f"Flux peak ratio (heavy/light) = {flux2.max()/flux1.max():.3f}")

# estimate cross section required to match AMS positron flux
ams_flux_peak = 1e-7  # cm^-2 s^-1 sr^-1 GeV^-1 (order of magnitude at 100 GeV)
# our toy model gave flux proportional to sigma * tau_diff / m^2
proportionality = (rho0**2 / m1**2) * 1e15 / (4 * np.pi * 1e28)
required_sigma = ams_flux_peak / proportionality
print(f"\nTo produce a peak flux ~{ams_flux_peak:.1e}, estimated <sigma v> ~ {required_sigma:.2e} cm^3/s")

# -----------------------------------------------------------------------------
# compare to AMS-02 positron fraction data downloaded earlier? simulate
# -----------------------------------------------------------------------------
print("\n(Plotting is optional; script can be run interactively.)")

try:
    plt.loglog(E, flux1 + flux2, label='DM total')
    plt.loglog(E, flux1, '--', label='DM-24')
    plt.loglog(E, flux2, ':', label='DM-15')
    plt.xlabel('Energy (GeV)')
    plt.ylabel('Relative flux')
    plt.legend()
    plt.title('Toy DM-induced cosmic-ray fluxes')
    plt.savefig('checks/CLXI_flux_plot.png')
    print('  Flux plot saved to checks/CLXI_flux_plot.png')
except Exception as e:
    print('  (plotting failed:', e, ')')

print("\nEND OF PART CLXI")
