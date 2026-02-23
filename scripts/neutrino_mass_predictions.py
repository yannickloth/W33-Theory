#!/usr/bin/env python3
"""Predict neutrino mass ratios from the Gram matrices.

We select the Gram with the smallest principal eigenvalue ratio as a proxy
for the neutrino Dirac coupling (since neutrino masses are the most
hierarchical).  Scaling the largest eigenvalue to an assumed heaviest
neutrino mass (e.g. 0.05 eV) yields a predicted spectrum which can be
compared to oscillation data.

This script is largely exploratory and prints the resulting mass ratios.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# ensure repo root on path
import os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

from scripts.yukawa_analysis import load_gram_list


def principal_ratio(G: np.ndarray) -> float:
    vals = np.linalg.eigvalsh(G)
    vals.sort()
    sqrt_vals = np.sqrt(vals)
    return float(sqrt_vals[-1] / sqrt_vals[0])


def main():
    grams = load_gram_list()
    if not grams:
        print("no Gram matrices available")
        sys.exit(1)

    ratios = [principal_ratio(np.array(G, dtype=float)) for G in grams]
    idx = int(np.argmin(ratios))
    Gnu = np.array(grams[idx], dtype=float)
    vals = np.linalg.eigvalsh(Gnu)
    vals.sort()
    sqrt_vals = np.sqrt(vals)

    # assume heaviest neutrino ~ 0.05 eV (rough value from oscillations)
    heavy_mass = 0.05  # eV
    # override if we can fetch a more recent limit
    from scripts.experimental_data import fetch_neutrino_mass_limits
    limits = fetch_neutrino_mass_limits()
    if limits and "masser" in limits:
        heavy_mass = min(heavy_mass, limits["masser"])
        print(f"using fetched electron-neutrino mass limit {limits['masser']} eV")
    scale = heavy_mass / sqrt_vals[-1]
    preds = scale * sqrt_vals
    ratios_pred = (preds[1]/preds[0], preds[2]/preds[1], preds[2]/preds[0])

    print(f"Selected Gram index {idx} with principal ratio {ratios[idx]:.3f}")
    print("Predicted neutrino masses (eV)", preds[:3])
    print("Inter-generation ratios (2/1,3/2,3/1)", ratios_pred)

    Path("data").mkdir(exist_ok=True)
    json.dump({"index": idx, "ratios": ratios, "predicted": preds.tolist()}, open("data/neutrino_mass_predictions.json", "w"), indent=2)
    print("saved data/neutrino_mass_predictions.json")


if __name__ == "__main__":
    main()
