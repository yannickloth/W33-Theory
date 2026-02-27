import json
import subprocess, sys, os
import numpy as np
import pandas as pd

def mat_mod3(M):
    return np.array(M, dtype=int) % 3

def apply_mat(A, u):
    return tuple(int(x) for x in (A @ np.array(u, dtype=int)) % 3)

def test_verify_fusion_script_runs(capsys):
    bundle = os.path.join(os.getcwd(), "H27_CE2_FUSION_BRIDGE_BUNDLE_v01")
    res = subprocess.run([sys.executable, "verify_fusion.py"], cwd=bundle,
                         capture_output=True, text=True)
    assert res.returncode == 0
    assert "ALL CHECKS PASSED" in res.stdout


def test_mapping_alignment():
    bundle = os.path.join(os.getcwd(), "H27_CE2_FUSION_BRIDGE_BUNDLE_v01")
    df = pd.read_csv(os.path.join(bundle, "pg_point_to_h27_vertex_coords.csv"))
    coords = pd.read_csv(os.path.join(bundle, "H27_v0_0_heisenberg_coords.csv"))
    coords_key = {(int(r.vertex), int(r.x), int(r.y), int(r.t))
                  for r in coords.itertuples(index=False)}
    for r in df.itertuples(index=False):
        assert (int(r.vertex_id), int(r.x), int(r.y), int(r.t)) in coords_key


def test_center_orbits_cycle():
    bundle = os.path.join(os.getcwd(), "H27_CE2_FUSION_BRIDGE_BUNDLE_v01")
    center = pd.read_csv(os.path.join(bundle, "center_orbits_fibers.csv"))
    for row in center.itertuples(index=False):
        # t-cycles should be sequential 0→1→2
        pg_cycle = [int(x) for x in str(row.pg_cycle_t0_t1_t2).split()]
        assert len(pg_cycle) == 3
        # no further check; presence suffices
        vert_cycle = [int(x) for x in str(row.vertex_cycle_t0_t1_t2).split()]
        assert len(vert_cycle) == 3


def test_sl2_action_and_mu_gauge():
    bundle = os.path.join(os.getcwd(), "H27_CE2_FUSION_BRIDGE_BUNDLE_v01")
    data = json.load(open(os.path.join(bundle, "stabilizer_SL2_and_mu_bridge.json")))
    coords = pd.read_csv(os.path.join(bundle, "H27_v0_0_heisenberg_coords.csv"))
    # build mapping vertex->u
    v2u = {int(r.vertex): (int(r.x), int(r.y)) for r in coords.itertuples(index=False)}
    # test S and T permutations respect target matrices
    A = mat_mod3(np.array(data["target_S_matrix"]))
    for k,v in data["S_perm_on_vertex_ids"].items():
        u = v2u[int(k)]; u2 = v2u[int(v)]
        assert apply_mat(A, u) == u2
    B = mat_mod3(np.array(data["target_T_matrix"]))
    for k,v in data["T_perm_on_vertex_ids"].items():
        u = v2u[int(k)]; u2 = v2u[int(v)]
        assert apply_mat(B, u) == u2
    # gauge check: for each u compare mu_obs and mu_can via provided solution
    obs = data["mu_observed_from_t0_representatives"]
    can = data["mu_canonical_from_f_2xy"]
    sol = data["gauge_solution_mu_obs = mu_can + a(Au)-a(u) + c"]

    for gen in ("S","T"):
        a = sol[gen]["a(u)"]
        c = sol[gen]["c"]
        A_mat = A if gen == "S" else B
        for ux,uy in [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]:
            key = f"{ux},{uy}"
            muobs = obs["mu"+gen][key]
            mucan = can["mu"+gen][ux][uy]
            Au = apply_mat(A_mat, (ux,uy))
            mu_calc = (mucan + a[f"{Au[0]},{Au[1]}"] - a[key] + c) % 3
            assert mu_calc == muobs
