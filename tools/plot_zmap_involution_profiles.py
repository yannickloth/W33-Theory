#!/usr/bin/env python3
"""Produce small diagnostic plots showing z-map histogram and match-count histogram
for the Hessian medium exact census. Saves PNGs under artifacts/min_cert_census_medium_2026_02_10/figures/.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN_JSON = (
    ROOT
    / "artifacts"
    / "min_cert_census_medium_2026_02_10"
    / "e6_f3_trilinear_reduced_orbit_closed_form_equiv_hessian_exact_full.json"
)
OUT_DIR = ROOT / "artifacts" / "min_cert_census_medium_2026_02_10" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with IN_JSON.open(encoding="utf-8") as f:
    dd = json.load(f)

# plot observed matching z-map histogram
z_hist = dd.get("observed_matching_z_map_histogram", {})
if z_hist:
    labels = list(z_hist.keys())
    values = [int(z_hist[k]) for k in labels]
    plt.figure(figsize=(6, 3))
    plt.bar(labels, values, color="#2b8cbe")
    plt.title("Observed matching z-map histogram (Hessian medium run)")
    plt.ylabel("Count")
    plt.tight_layout()
    out1 = OUT_DIR / "zmap_hist_hessian.png"
    plt.savefig(out1, dpi=150)
    plt.close()

# plot match count histogram
mch = dd.get("match_count_histogram", {})
if mch:
    labels = sorted(mch.keys(), key=int)
    values = [int(mch[k]) for k in labels]
    plt.figure(figsize=(4, 3))
    plt.bar(labels, values, color="#a6d96a")
    plt.title("Match count histogram (Hessian medium run)")
    plt.xlabel("match count per rep")
    plt.ylabel("representative count")
    plt.tight_layout()
    out2 = OUT_DIR / "match_count_hist_hessian.png"
    plt.savefig(out2, dpi=150)
    plt.close()

print(f"Wrote figures to {OUT_DIR}")
