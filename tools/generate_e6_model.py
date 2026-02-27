"""Regenerate e6_cubic_affine_heisenberg_model.json using current schlafli mapping."""
import json
from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent.resolve()
SCH_JSON = REPO / "artifacts" / "schlafli_e6id_to_w33_h27.json"
FUSION_DIR = REPO / "H27_CE2_FUSION_BRIDGE_BUNDLE_v01"

coords = pd.read_csv(FUSION_DIR / "H27_v0_0_heisenberg_coords.csv")
vid_to_xyz = {int(r.vertex): (int(r.x), int(r.y), int(r.t)) for r in coords.itertuples(index=False)}

sch = json.loads(SCH_JSON.read_text(encoding="utf-8"))
e6_to_vid = list(sch["maps"]["e6id_to_w33_bundle"])

model = {"e6id_to_heisenberg": {}}
for e6 in range(27):
    v = e6_to_vid[e6]
    x, y, t = vid_to_xyz[v]
    model["e6id_to_heisenberg"][str(e6)] = {"u": [x, y], "z": t, "w33_vertex_id": v}

outpath = REPO / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
outpath.write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
print("wrote", outpath, "entries", len(model["e6id_to_heisenberg"]))
