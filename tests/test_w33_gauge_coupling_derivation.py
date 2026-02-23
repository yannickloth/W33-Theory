"""Tests for scripts/w33_gauge_coupling_derivation.py.

These tests verify the two key geometric derivations:
  1. alpha_GUT = 1/(8*pi)  from n_v/(2*pi*n_t) = 40/(2*pi*160)
  2. sin^2(theta_W) = 3/8  from (r-s)/(k-s) with r=2, s=-4, k=12
and that the MSSM running gives physically sensible predictions.
"""
import json
import math
import os
import subprocess
import sys


def test_script_runs():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    res = subprocess.run(
        [sys.executable, "scripts/w33_gauge_coupling_derivation.py"],
        env=env, capture_output=True, text=True,
    )
    assert res.returncode == 0, f"script failed:\n{res.stderr}"
    assert os.path.exists("data/w33_gauge_coupling.json"), "output JSON not written"


def test_alpha_gut_formula():
    """alpha_GUT = n_v/(2*pi*n_t) = 1/(8*pi)."""
    n_v, n_t = 40, 160
    alpha_gut = n_v / (2 * math.pi * n_t)
    assert abs(alpha_gut - 1 / (8 * math.pi)) < 1e-12
    alpha_gut_inv = 1 / alpha_gut
    assert abs(alpha_gut_inv - 8 * math.pi) < 1e-10
    # within 5% of experimental MSSM value ~24.3
    assert abs(alpha_gut_inv - 24.3) / 24.3 < 0.05


def test_weinberg_angle_srg():
    """sin^2(theta_W) = (r-s)/(k-s) = 3/8 for SRG(40,12,2,4) eigenvalues r=2,s=-4,k=12."""
    k, lam, mu = 12, 2, 4
    disc = (lam - mu) ** 2 + 4 * (k - mu)
    r = ((lam - mu) + math.sqrt(disc)) / 2
    s = ((lam - mu) - math.sqrt(disc)) / 2
    assert abs(r - 2) < 1e-9, f"expected r=2, got {r}"
    assert abs(s + 4) < 1e-9, f"expected s=-4, got {s}"
    sin2 = (r - s) / (k - s)
    assert abs(sin2 - 3 / 8) < 1e-12, f"expected 3/8, got {sin2}"


def test_srg_vertex_triangle_count():
    """n_t = n_e * lambda / 3 = 240 * 2 / 3 = 160 for W33."""
    n_v, k, lam = 40, 12, 2
    n_e = n_v * k // 2   # = 240
    n_t = n_e * lam // 3  # = 160
    assert n_v == 40
    assert n_e == 240
    assert n_t == 160


def test_json_output_alpha_gut():
    data = json.load(open("data/w33_gauge_coupling.json"))
    ag = data["alpha_GUT"]["alpha_GUT"]
    ag_inv = data["alpha_GUT"]["alpha_GUT_inv"]
    assert abs(ag - 1 / (8 * math.pi)) < 1e-9
    assert abs(ag_inv - 8 * math.pi) < 1e-6


def test_json_output_weinberg():
    data = json.load(open("data/w33_gauge_coupling.json"))
    sin2 = data["weinberg_angle"]["sin2_theta_W_GUT"]
    assert abs(sin2 - 3 / 8) < 1e-9


def test_mssm_mgut_order_of_magnitude():
    """M_GUT from standard MSSM unification should be between 10^14 and 10^18 GeV."""
    data = json.load(open("data/w33_gauge_coupling.json"))
    M_GUT = data["mssm_running"]["M_GUT_MSSM_GeV"]
    assert 1e14 < M_GUT < 1e18, f"M_GUT = {M_GUT:.2e} out of expected range"


def test_alpha2_mssm_crosscheck():
    """Standard MSSM cross-check: alpha_2^{-1} predicted within 5% of experiment."""
    data = json.load(open("data/w33_gauge_coupling.json"))
    pred = data["mssm_running"]["alpha2_inv_pred_MSSM"]
    exp = data["mssm_running"]["alpha2_inv_exp"]
    err = abs(pred - exp) / exp
    assert err < 0.05, f"alpha_2^{{-1}} prediction off by {100*err:.1f}%"


def test_proton_lifetime_above_bound():
    data = json.load(open("data/w33_gauge_coupling.json"))
    tau = data["proton_lifetime"]["tau_p_years"]
    assert tau > 1.6e34, f"tau_p = {tau:.2e} yr is below the experimental bound"
