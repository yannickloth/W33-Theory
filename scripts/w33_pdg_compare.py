#!/usr/bin/env python3
"""Compare W33 RG-predicted low-energy masses to PDG reference values.

- Runs `derive_yukawas_from_triads()` -> `integrate_rg()`
- Compares m_t, m_b, m_tau against PDG reference numbers (broad comparison)
- Writes an artifact JSON under `artifacts/` and returns the comparison dict.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Allow direct execution as `python scripts/w33_pdg_compare.py`
    sys.path.insert(0, str(ROOT))

from scripts.w33_mass_synthesis import derive_yukawas_from_triads
from scripts.w33_rg_flow import integrate_rg

# PDG reference (representative values; keep conservative tolerances)
PDG = {
    "top_pole_GeV": 172.9,
    "tau_mass_GeV": 1.77686,
    # approximate MSbar -> MZ mapping (order-of-magnitude) for comparison only
    "b_MSbar_m_b_mb_GeV": 4.18,
    "b_at_MZ_approx_GeV": 2.83,
}


def compare_to_pdg():
    yuk = derive_yukawas_from_triads()
    out = integrate_rg(yuk)

    pred = {
        "m_t_pred_GeV": out.get("m_t_MZ_GeV"),
        "m_b_pred_GeV": out.get("m_b_MZ_GeV"),
        "m_tau_pred_GeV": out.get("m_tau_MZ_GeV"),
    }

    # relative differences (model / PDG)
    rel = {
        "top_rel": float(pred["m_t_pred_GeV"] / PDG["top_pole_GeV"]),
        "tau_rel": float(pred["m_tau_pred_GeV"] / PDG["tau_mass_GeV"]),
        "b_rel": float(pred["m_b_pred_GeV"] / PDG["b_at_MZ_approx_GeV"]),
    }

    comp = {
        "timestamp": int(time.time()),
        "yukawas_GUT": yuk,
        "prediction_MZ_GeV": pred,
        "pdg_reference": PDG,
        "ratios_model_over_pdg": rel,
    }

    out_path = ROOT / "artifacts" / f"w33_pdg_compare_{int(time.time())}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(comp, indent=2), encoding="utf-8")

    print("Wrote PDG comparison artifact:", out_path)
    print(
        "Summary ratios (model/pdg): top={:.2f}, b={:.2f}, tau={:.2f}".format(
            rel["top_rel"], rel["b_rel"], rel["tau_rel"]
        )
    )

    return comp


if __name__ == "__main__":
    compare_to_pdg()
