#!/usr/bin/env python3
import zipfile
from pathlib import Path

base = Path("artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis")
files = [
    "H27_vertices_as_F3_cube_xy_t_holonomy_gauge.csv",
    "W33_Heisenberg_generators_Tx_Ty_Z.json",
    "W33_translation_lifts_canonical.csv",
    "qutrit_MUB_state_vectors_for_N12_vertices_phase_corrected.csv",
    "parallelogram_holonomy_vs_bargmann.json",
]
zip_path = base / "W33_holonomy_push_bundle_20260209.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for f in files:
        p = base / f
        if p.exists():
            z.write(p, arcname=p.name)
print("Wrote", zip_path)
