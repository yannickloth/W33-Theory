#!/usr/bin/env python3
"""
Recompute the local weld:
  K = <g2,g3,g5,g8,g9> ⊂ PSp(4,3) on SRG36
and its induced (no-deck) torsor action on the axis-192 completion torsor.

Inputs (expected next to this script or in the same relative structure):
  - TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip  (contains nested bundles)
  - TOE_pocket_transport_glue_orbit480_v01_20260227_bundle.zip (pocket_geometry.json)
  - TOE_w33_axis192_torsor_v01_20260227_bundle.zip (axis torsor + sigma↦r mapping)
Outputs:
  - K_schreier_edges_cocycle.csv
  - K_orbit_pockets_54.csv
  - torsor_right_multiplication_C3.json
"""
import os, zipfile, json, re
from collections import deque
import pandas as pd

HERE=os.path.dirname(os.path.abspath(__file__))

HOL=os.path.join(HERE, "..", "TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip")
POCKET=os.path.join(HERE, "..", "TOE_pocket_transport_glue_orbit480_v01_20260227_bundle.zip")
TORSOR=os.path.join(HERE, "..", "TOE_w33_axis192_torsor_v01_20260227_bundle.zip")

def perm_comp(p,q):
    return tuple(p[i] for i in q)
def perm_inv(p):
    inv=[0]*len(p)
    for i,j in enumerate(p):
        inv[j]=i
    return tuple(inv)

def apply_perm_to_pocket(p, pocket):
    return tuple(sorted(p[i] for i in pocket))

def extract_nested(zip_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path,'r') as z:
        z.extractall(target_dir)

def find_file(root, filename):
    for r,ds,fs in os.walk(root):
        for f in fs:
            if f==filename:
                return os.path.join(r,f)
    return None

tmp=os.path.join(HERE,"_tmp_recompute")
if os.path.exists(tmp):
    import shutil; shutil.rmtree(tmp)
os.makedirs(tmp, exist_ok=True)

# Unpack holonomy + nested zips
extract_nested(HOL, os.path.join(tmp,"hol"))
hol_dir=os.path.join(tmp,"hol","TOE_holonomy_Z2_flatZ3_v01_20260227")
nested=[os.path.join(hol_dir,f) for f in os.listdir(hol_dir) if f.endswith(".zip")]
for nz in nested:
    extract_nested(nz, os.path.join(tmp, os.path.splitext(os.path.basename(nz))[0]))

e6_dir=None
for d in os.listdir(tmp):
    if "TOE_E6pair_SRG_triangle_decomp" in d:
        e6_dir=os.path.join(tmp,d)
        break
assert e6_dir is not None
gen_path=find_file(e6_dir,"sp43_generators_on_e6pairs_36.json")
assert gen_path is not None

gens=json.load(open(gen_path))
gens=[tuple(g) for g in gens]

# Load pocket geometry
with zipfile.ZipFile(POCKET,'r') as z:
    pg_path=[n for n in z.namelist() if n.endswith("pocket_geometry.json")][0]
    pg=json.loads(z.read(pg_path).decode("utf-8"))
pockets=[tuple(sorted(p)) for p in pg["pockets"]]
silent_of={}
for k,v in pg["silent_of_pocket"].items():
    key=tuple(sorted(json.loads(k)))
    silent_of[key]=v

# Load sigma↦r mapping + torsor encodings (just for identity index)
with zipfile.ZipFile(TORSOR,'r') as z:
    stab_to_oct=json.loads(z.read("pocket_mult_stabilizer_to_octonion_axis192.json").decode("utf-8"))
sigma_to_r={}
for k_str,info in stab_to_oct["sigma_to_r"].items():
    sigma=tuple(eval(k_str))
    sigma_to_r[sigma]=info

# Subgroup K generators
gen_idx=[2,3,5,8,9]
K_gens=[gens[i] for i in gen_idx]
gen_names=[f"g{i}" for i in gen_idx]

# Build K orbit on pockets
base_pocket=(0,1,2,14,15,17,27)
assert base_pocket in silent_of

orbit=[base_pocket]
pocket_to_id={base_pocket:0}
rep_perm={base_pocket:tuple(range(36))}
parent={base_pocket:None}
q=deque([base_pocket])

while q:
    Q=q.popleft()
    kQ=rep_perm[Q]
    for name,g in zip(gen_names, K_gens):
        Q2=apply_perm_to_pocket(g,Q)
        if Q2 not in pocket_to_id:
            pocket_to_id[Q2]=len(orbit)
            orbit.append(Q2)
            parent[Q2]=(Q,name)
            rep_perm[Q2]=perm_comp(g,kQ)
            q.append(Q2)

loc=list(base_pocket)
loc_to_i={v:i for i,v in enumerate(loc)}
def restrict_to_sigma(r_perm):
    image=[r_perm[v] for v in loc]
    if sorted(image)!=sorted(loc):
        return None
    return tuple(loc_to_i[r_perm[v]] for v in loc)

sigma_id=(0,1,2,3,4,5,6)
sigma_a=(1,3,5,0,2,4,6)
sigma_b=(3,0,4,1,5,2,6)
sigma_to_exp={sigma_id:0, sigma_a:1, sigma_b:2}

rows=[]
for Q in orbit:
    qid=pocket_to_id[Q]
    kQ=rep_perm[Q]
    for name,g in zip(gen_names, K_gens):
        Q2=apply_perm_to_pocket(g,Q)
        q2id=pocket_to_id[Q2]
        kQ2=rep_perm[Q2]
        r=perm_comp(perm_inv(kQ2), perm_comp(g,kQ))
        sigma=restrict_to_sigma(r)
        exp=sigma_to_exp[sigma]
        info=sigma_to_r[sigma]
        rows.append({
            "from_id": qid,
            "to_id": q2id,
            "gen": name,
            "sigma": str(sigma),
            "exp": exp,
            "oct_r_stab_index": info["r_stab_index"],
            "oct_r_perm": str(info["r_perm"]),
            "oct_r_signs": str(info["r_signs"]),
            "oct_r_order": info["r_order"],
        })

df=pd.DataFrame(rows)
df.to_csv(os.path.join(HERE,"K_schreier_edges_cocycle.csv"), index=False)

# Orbit CSV
orbit_rows=[]
for Q in orbit:
    par=parent[Q]
    orbit_rows.append({
        "orbit_id": pocket_to_id[Q],
        "pocket_vertices": list(Q),
        "axis_vertex": silent_of[Q],
        "parent_orbit_id": pocket_to_id[par[0]] if par else None,
        "parent_gen": par[1] if par else None,
    })
pd.DataFrame(orbit_rows).sort_values("orbit_id").to_csv(os.path.join(HERE,"K_orbit_pockets_54.csv"), index=False)

print("OK")
print("K pocket orbit size:", len(orbit))
print("Cocycle exp counts:", dict(df["exp"].value_counts()))
