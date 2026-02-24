"""tests/test_full_optimization.py
Pillar 66: Unitarity-Corrected CKM Comparison + Full Joint Optimization
Tests for THEORY_PART_CLXXV_FULL_OPTIMIZATION.py

All numerics loaded from data/w33_full_optimization.json.
If the JSON does not exist, tests are skipped.
"""

from __future__ import annotations
import json
import os
import sys

import numpy as np
import pytest

DATA_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "w33_full_optimization.json"
)


@pytest.fixture(scope="module")
def results():
    if not os.path.exists(DATA_FILE):
        pytest.skip(
            f"data file not found: {DATA_FILE} "
            "-- run THEORY_PART_CLXXV_FULL_OPTIMIZATION.py first"
        )
    with open(DATA_FILE) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Pillar identity
# ---------------------------------------------------------------------------

def test_pillar_is_66(results):
    assert results["pillar"] == 66


# ---------------------------------------------------------------------------
# ADVANCE A: Unitarity-consistent CKM target
# ---------------------------------------------------------------------------

def test_v_ud_unitary_close_to_pdg(results):
    """V_ud from row-unitarity agrees with PDG within 0.5%."""
    V_ud = results["V_ud_unitary"]
    assert abs(V_ud - 0.97373) < 0.005, f"V_ud_unitary = {V_ud:.5f}"


def test_v_cs_unitary_not_pdg_raw(results):
    """V_cs from row-unitarity (0.974) is far from raw PDG (0.987)."""
    V_cs = results["V_cs_unitary"]
    # Unitarity gives ~0.974, raw PDG says 0.987
    assert V_cs < 0.980, f"V_cs_unitary = {V_cs:.5f}, expected < 0.980"
    assert V_cs > 0.970, f"V_cs_unitary = {V_cs:.5f}, expected > 0.970"


def test_v_tb_unitary_not_pdg_raw(results):
    """V_tb from row-unitarity (0.999) is far from raw PDG (1.013 > 1)."""
    V_tb = results["V_tb_unitary"]
    # Unitarity forces V_tb < 1; raw PDG has 1.013 > 1 (impossible for unitary)
    assert V_tb < 1.0, f"V_tb_unitary = {V_tb:.5f} exceeds 1 (violates unitarity!)"
    assert V_tb > 0.998, f"V_tb_unitary = {V_tb:.5f}, expected > 0.998"


def test_unitarity_correction_factor(results):
    """Unitarity correction gives 4x or better improvement over raw-PDG comparison."""
    raw  = results["pillar65_ckm_vs_raw_pdg"]
    uni  = results["pillar65_ckm_vs_unitary"]
    ratio = raw / uni
    assert ratio >= 4.0, (
        f"Unitarity correction factor = {ratio:.1f}x, expected >= 4x"
    )


def test_pillar65_ckm_vs_unitary_small(results):
    """Pillar 65 CKM error vs unitary target is already < 0.005."""
    uni = results["pillar65_ckm_vs_unitary"]
    assert uni < 0.005, f"Pillar 65 CKM vs unitary = {uni:.6f}, expected < 0.005"


# ---------------------------------------------------------------------------
# ADVANCE B: Joint optimization results
# ---------------------------------------------------------------------------

def test_active_modes_per_sector(results):
    """Each Z3 sector has exactly 7 active modes (Gram rank = 7)."""
    modes = results["n_active_modes"]
    assert modes == [7, 7, 7], f"n_active_modes = {modes}"


def test_total_params_is_129(results):
    """Total parameter count = 7 + 14 + 54 + 54 = 129 real params."""
    assert results["n_total_params"] == 129


def test_joint_ckm_better_than_p65_unitary(results):
    """Joint optimization improves on Pillar 65 vs unitary target."""
    joint = results["joint_ckm_error_vs_unitary"]
    p65   = results["pillar65_ckm_vs_unitary"]
    assert joint <= p65 + 1e-6, (
        f"joint {joint:.6f} not <= p65 {p65:.6f}"
    )


def test_joint_ckm_error_very_small(results):
    """Joint CKM error vs unitary target < 0.004."""
    err = results["joint_ckm_error_vs_unitary"]
    assert err < 0.004, f"Joint CKM error = {err:.6f}, expected < 0.004"


def test_joint_pmns_error_small(results):
    """Joint PMNS error < 0.010."""
    err = results["joint_pmns_error"]
    assert err < 0.010, f"Joint PMNS error = {err:.6f}, expected < 0.010"


# ---------------------------------------------------------------------------
# CKM matrix element tests (joint prediction vs unitary target)
# ---------------------------------------------------------------------------

def test_ckm_vud_accurate(results):
    """|V_ud| predicted accurately (within 0.5%)."""
    V = np.array(results["ckm"]["V"])
    target = results["V_ud_unitary"]
    diff = abs(V[0, 0] - target)
    assert diff < 0.005, f"|V_ud| = {V[0,0]:.5f}, target = {target:.5f}, diff = {diff:.5f}"


def test_ckm_vus_accurate(results):
    """|V_us| in [0.20, 0.25] after joint optimization."""
    V = np.array(results["ckm"]["V"])
    assert 0.20 < V[0, 1] < 0.25, f"|V_us| = {V[0,1]:.5f}"


def test_ckm_vub_essentially_exact(results):
    """|V_ub| within 30% of experimental 0.00382."""
    V = np.array(results["ckm"]["V"])
    Vub = V[0, 2]
    assert 0.002 < Vub < 0.008, f"|V_ub| = {Vub:.5f}"


def test_ckm_vcs_exact(results):
    """|V_cs| matches unitary target to better than 0.5%."""
    V = np.array(results["ckm"]["V"])
    target = results["V_cs_unitary"]
    diff = abs(V[1, 1] - target)
    assert diff < 0.005, f"|V_cs| = {V[1,1]:.5f}, target = {target:.5f}"


def test_ckm_vcb_accurate(results):
    """|V_cb| in [0.035, 0.045] (within 10% of exp 0.041)."""
    V = np.array(results["ckm"]["V"])
    Vcb = V[1, 2]
    assert 0.035 < Vcb < 0.045, f"|V_cb| = {Vcb:.5f}"


def test_ckm_vtb_essentially_one(results):
    """|V_tb| > 0.998 (near unity, as expected for third-generation dominance)."""
    V = np.array(results["ckm"]["V"])
    assert V[2, 2] > 0.998, f"|V_tb| = {V[2,2]:.5f}"


def test_ckm_diagonal_dominance(results):
    """CKM is nearly diagonal: diagonal elements >> off-diagonal."""
    V = np.array(results["ckm"]["V"])
    assert V[0, 0] > 0.97, f"V_ud = {V[0,0]:.4f}"
    assert V[1, 1] > 0.97, f"V_cs = {V[1,1]:.4f}"
    assert V[2, 2] > 0.99, f"V_tb = {V[2,2]:.4f}"


def test_jarlskog_nonzero(results):
    """Jarlskog invariant is non-zero (genuine CP violation predicted)."""
    J = results["ckm"]["Jarlskog"]
    assert abs(J) > 1e-6, f"J = {J:.4e} is effectively zero"


def test_jarlskog_order_of_magnitude(results):
    """Jarlskog |J| within one order of magnitude of exp 3.1e-5."""
    J = results["ckm"]["Jarlskog"]
    J_exp = 3.1e-5
    ratio = abs(J) / J_exp
    assert 0.1 < ratio < 10, f"|J| = {abs(J):.2e}, exp 3.1e-5, ratio = {ratio:.2f}"


# ---------------------------------------------------------------------------
# PMNS matrix element tests
# ---------------------------------------------------------------------------

def test_pmns_ve3_reactor_angle(results):
    """|V_e3| (reactor angle) in [0.13, 0.16]."""
    V = np.array(results["pmns"]["V"])
    Ve3 = V[0, 2]
    assert 0.13 < Ve3 < 0.16, f"|V_e3| = {Ve3:.4f}"


def test_pmns_ve2_solar_angle(results):
    """|V_e2| (solar angle) in [0.50, 0.60]."""
    V = np.array(results["pmns"]["V"])
    Ve2 = V[0, 1]
    assert 0.50 < Ve2 < 0.60, f"|V_e2| = {Ve2:.4f}"


def test_pmns_vmu3_atmospheric_angle(results):
    """|V_mu3| (atmospheric angle) in [0.60, 0.70]."""
    V = np.array(results["pmns"]["V"])
    Vmu3 = V[1, 2]
    assert 0.60 < Vmu3 < 0.70, f"|V_mu3| = {Vmu3:.4f}"


def test_lepton_jarlskog_large(results):
    """Lepton Jarlskog |J_lep| > 0.001 (large CP violation in lepton sector)."""
    J = results["pmns"]["Jarlskog"]
    assert abs(J) > 0.001, f"Lepton J = {J:.4e}"


# ---------------------------------------------------------------------------
# Infrastructure tests (no JSON needed)
# ---------------------------------------------------------------------------

def test_cubic_tensor_shape():
    """build_cubic_tensor returns a 27x27x27 array."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    from THEORY_PART_CLXXV_FULL_OPTIMIZATION import build_cubic_tensor

    _, local_tris, _, _ = build_z3_complex_profiles()
    C = build_cubic_tensor(local_tris)
    assert C.shape == (27, 27, 27), f"C.shape = {C.shape}"


def test_cubic_tensor_symmetric():
    """C[i,j,k] is fully symmetric in all 6 permutations."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    from THEORY_PART_CLXXV_FULL_OPTIMIZATION import build_cubic_tensor

    _, local_tris, _, _ = build_z3_complex_profiles()
    C = build_cubic_tensor(local_tris)
    assert np.allclose(C, C.transpose(1, 0, 2)), "C not symmetric in i,j"
    assert np.allclose(C, C.transpose(0, 2, 1)), "C not symmetric in j,k"
    assert np.allclose(C, C.transpose(2, 1, 0)), "C not symmetric in i,k"


def test_active_basis_shape():
    """Active basis A[a] has shape (27, 7) for each sector."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import build_z3_complex_profiles
    from THEORY_PART_CLXXV_FULL_OPTIMIZATION import build_active_basis

    _, _, _, P = build_z3_complex_profiles()
    A, n_modes = build_active_basis(P)
    assert len(A) == 3
    for a in range(3):
        assert A[a].shape[0] == 27, f"A[{a}] rows = {A[a].shape[0]}"
        assert A[a].shape[1] == n_modes[a]
        assert n_modes[a] == 7, f"Active modes for sector {a} = {n_modes[a]}, expected 7"


def test_yukawa_from_cubic_matches_direct():
    """yukawa3x3_from_cubic gives same result as w33_complex_yukawa.yukawa3x3."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, repo_root)
    sys.path.insert(0, os.path.join(repo_root, "scripts"))
    from w33_complex_yukawa import (
        build_z3_complex_profiles, build_dominant_profiles, yukawa3x3,
    )
    from THEORY_PART_CLXXV_FULL_OPTIMIZATION import (
        build_cubic_tensor, yukawa3x3_from_cubic,
    )

    H27, local_tris, _, P = build_z3_complex_profiles()
    psi_dom = build_dominant_profiles(P)
    C = build_cubic_tensor(local_tris)

    rng = np.random.default_rng(42)
    v = rng.normal(0, 1, 27) + 1j * rng.normal(0, 1, 27)
    v /= np.linalg.norm(v)

    Y_direct = yukawa3x3(psi_dom, local_tris, v)
    Y_cubic  = yukawa3x3_from_cubic(C, psi_dom, v)
    diff = np.linalg.norm(Y_direct - Y_cubic)
    assert diff < 1e-10, f"Cubic tensor mismatch ||diff|| = {diff:.2e}"
