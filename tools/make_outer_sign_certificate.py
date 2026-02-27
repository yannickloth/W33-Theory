import os, json, zipfile
from pathlib import Path
import pandas as pd

REPO = Path(".").resolve()

# if a pre-made zip is available, use it; otherwise assume bundle folder exists
OUTER_ZIP = Path("/mnt/data/H27_OUTER_TWIST_ACTION_BUNDLE_v01.zip")
BUNDLE_DIR = REPO / "H27_OUTER_TWIST_ACTION_BUNDLE_v01"
FUSION_DIR = REPO / "H27_CE2_FUSION_BRIDGE_BUNDLE_v01"
SCH_JSON = REPO / "artifacts" / "schlafli_e6id_to_w33_h27.json"
CE2_SIGN_JSON = REPO / "committed_artifacts" / "ce2_simple_family_sign_map.json"

TMP = REPO / "_tmp_outer"
TMP.mkdir(exist_ok=True)

# --- load outer permutation data ---
if OUTER_ZIP.exists():
    outer_dir = TMP / "outer"
    outer_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUTER_ZIP, "r") as z:
        z.extractall(outer_dir)
    perm40 = json.loads((outer_dir / "perm40_and_H27_pg_ids.json").read_text(encoding="utf-8"))
else:
    perm40 = json.loads((BUNDLE_DIR / "perm40_and_H27_pg_ids.json").read_text(encoding="utf-8"))
perm_pg = {int(k): int(v) for k, v in perm40["perm_on_H27_pg_ids"].items()}

# --- PG id -> vertex_id (bundle labeling) + coords ---
df_pg = pd.read_csv(FUSION_DIR / "pg_point_to_h27_vertex_coords.csv")
pg_to_vid = {int(r.pg_id): int(r.vertex_id) for r in df_pg.itertuples(index=False)}

coords = pd.read_csv(FUSION_DIR / "H27_v0_0_heisenberg_coords.csv")
vid_to_xyz = {int(r.vertex): (int(r.x), int(r.y), int(r.t)) for r in coords.itertuples(index=False)}

# --- E6 id -> vertex_id (bundle labeling) ---
sch = json.loads(SCH_JSON.read_text(encoding="utf-8"))
e6_to_vid = list(sch["maps"]["e6id_to_w33_bundle"])
vid_to_e6 = {v: i for i, v in enumerate(e6_to_vid)}

# --- induced outer permutation on vertex_id then on E6 ids ---
perm_vid = {pg_to_vid[pg]: pg_to_vid[perm_pg[pg]] for pg in perm_pg.keys()}
P_e6 = []
for e6 in range(27):
    v = e6_to_vid[e6]
    v2 = perm_vid[v]
    P_e6.append(vid_to_e6[v2])

assert len(set(P_e6)) == 27, "P_e6 is not a permutation"

# --- write the missing artifact: e6_cubic_affine_heisenberg_model.json ---
model = {"e6id_to_heisenberg": {}}
for e6 in range(27):
    v = e6_to_vid[e6]
    x, y, t = vid_to_xyz[v]
    model["e6id_to_heisenberg"][str(e6)] = {"u": [x, y], "z": t, "w33_vertex_id": v}

( REPO / "artifacts" / "e6_cubic_affine_heisenberg_model.json" ).write_text(
    json.dumps(model, indent=2, sort_keys=True), encoding="utf-8"
)

# --- import CE2 closed form and branch predicate exactly as implemented ---
import sys
sys.path.insert(0, str(REPO))
from scripts import ce2_global_cocycle as cg

sign_map = cg._simple_family_sign_map()
assert len(sign_map) == 864

def branch_constant_line(c_i, m_i, o_i):
    e6id_to_vec, _ = cg._heisenberg_vec_maps()
    uc1, uc2, _ = e6id_to_vec[int(c_i)]
    um1, um2, _ = e6id_to_vec[int(m_i)]
    # direction d = u_m - u_c
    d1 = (um1 - uc1) % 3
    d2 = (um2 - uc2) % 3
    if (d1, d2) == (0, 0):
        return False
    w = cg._f3_omega((uc1, uc2), (d1, d2))
    # exact constant-line test used in repo code-path
    return (d1 != 0) and (int(w) == cg._f3_k_of_direction((d1, d2)))

# --- full 864-key conjugation table + stats ---
rows = []
stats = {
    "chi_det": -1,
    "weil": {"+1": 0, "-1": 0},
    "constant": {"+1": 0, "-1": 0},
}

skipped = 0
for (c, m, o), s in sign_map.items():
    cp, mp, op = P_e6[c], P_e6[m], P_e6[o]
    if (cp, mp, op) not in sign_map:
        skipped += 1
        continue
    sp = sign_map[(cp, mp, op)]
    ratio = int(sp // s)  # ±1
    const = branch_constant_line(c, m, o)
    bucket = "constant" if const else "weil"
    stats[bucket]["+1" if ratio == 1 else "-1"] += 1
    rows.append([c, m, o, s, cp, mp, op, sp, ratio, bucket])

print("skipped keys", skipped, "of", len(sign_map))

df = pd.DataFrame(
    rows,
    columns=["c", "match", "other", "sign", "c2", "match2", "other2", "sign2", "ratio", "branch"],
)

out_dir = TMP / "OUTER_TWIST_SIGN_CERTIFICATE"
out_dir.mkdir(exist_ok=True)

(out_dir / "P_outer_on_E6.json").write_text(json.dumps({"P_e6": P_e6}, indent=2), encoding="utf-8")
(out_dir / "branch_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
df.to_csv(out_dir / "outer_sign_conjugation_full.csv", index=False)

# zip it
zip_path = TMP / "OUTER_TWIST_ACTS_ON_CE2_SIGN_LAYER_CERTIFICATE_v01.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for fn in ["P_outer_on_E6.json", "branch_stats.json", "outer_sign_conjugation_full.csv"]:
        z.write(out_dir / fn, arcname=fn)

print("WROTE:", zip_path)
print("STATS:", stats)
