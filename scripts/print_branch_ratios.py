import json
from pathlib import Path
import numpy as np
import sys
# ensure workspace root on sys.path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))
from scripts.ce2_global_cocycle import (_simple_family_sign_map,
                                         _heisenberg_vec_maps,
                                         _f3_omega,
                                         _f3_k_of_direction)

A = np.array([[1, 2], [2, 0]], dtype=int) % 3
b = np.array([0, 2], dtype=int) % 3

def apply_outer_h27(u, t):
    up = tuple(int(x) for x in (A @ np.array(u) + b) % 3)
    x, y = u
    tp = (2 * t + (2 + 2 * x + y)) % 3
    return up, int(tp)

def branch_type(c, match, other):
    e6id_to_vec, _ = _heisenberg_vec_maps()
    uc1, uc2, zc = e6id_to_vec[int(c)]
    um1, um2, zm = e6id_to_vec[int(match)]
    uo1, uo2, zo = e6id_to_vec[int(other)]
    d1 = (int(um1) - int(uc1)) % 3
    d2 = (int(um2) - int(uc2)) % 3
    if d1 == 0 and d2 == 0:
        raise ValueError("zero direction")
    w = _f3_omega((uc1, uc2), (d1, d2))
    if d1 != 0 and int(w) == _f3_k_of_direction((d1, d2)):
        return "constant"
    return "weil"

model = json.load(open(Path("artifacts") / "e6_cubic_affine_heisenberg_model.json"))
mapping = model["e6id_to_heisenberg"]
vec_to_eid = {}
for k, v in mapping.items():
    u = (int(v["u"][0]) % 3, int(v["u"][1]) % 3)
    z = int(v["z"]) % 3
    vec_to_eid[(u[0], u[1], z)] = int(k)

perm = [-1] * 27
for eid, v in mapping.items():
    eid = int(eid)
    u = (int(v["u"][0]) % 3, int(v["u"][1]) % 3)
    z = int(v["z"]) % 3
    up, zp = apply_outer_h27(u, z)
    perm[eid] = vec_to_eid[(up[0], up[1], zp)]

sign_map = _simple_family_sign_map()
ratios = {+1: 0, -1: 0}
branch_ratios = {"constant": {+1: 0, -1: 0}, "weil": {+1: 0, -1: 0}}
for (c, m, o), s in sign_map.items():
    c2 = perm[c]
    m2 = perm[m]
    o2 = perm[o]
    s2 = sign_map[(c2, m2, o2)]
    r = int(s2) * int(s)
    ratios[r] += 1
    br = branch_type(c, m, o)
    branch_ratios[br][r] += 1

print("ratios", ratios)
print("branch_ratios", branch_ratios)
