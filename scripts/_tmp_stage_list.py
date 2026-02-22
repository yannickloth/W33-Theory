#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path("committed_artifacts")
add_list = []
# scripts to stage (modified)
scripts = [
    "scripts/dd_shrink_conflict.py",
    "scripts/register_dd_obstructions.py",
    "scripts/solve_e8_embedding_cpsat.py",
    "scripts/analyze_dd_repro.py",
    "scripts/print_dd_repro_summary.py",
    "scripts/_tmp_create_dd_pair_obstruction_50_51.py",
    "scripts/_tmp_collect_git_status.py",
    "scripts/_tmp_get_root_vector.py",
]
for s in scripts:
    if Path(s).exists():
        add_list.append(s)
# dd_shrink_result canonical: initial_reproducible True or shrink_status in ['already_minimal','shrunk']
for p in ART.glob("PART_CVII_dd_shrink_result_*.json"):
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
        if j.get("initial_reproducible") or j.get("shrink_status") in (
            "already_minimal",
            "shrunk",
        ):
            add_list.append(str(p))
    except Exception:
        pass
# dd_pair_obstruction: include those with solver_status == INFEASIBLE
for p in ART.glob("PART_CVII_dd_pair_obstruction_*.json"):
    try:
        j = json.loads(p.read_text(encoding="utf-8"))
        if j.get("solver_status") == "INFEASIBLE":
            add_list.append(str(p))
    except Exception:
        pass
# dd_seed_initial: include all
for p in ART.glob("PART_CVII_dd_seed_initial_*.json"):
    add_list.append(str(p))
add_list = sorted(set(add_list))
open("checks/_tmp_stage_list.txt", "w", encoding="utf-8").write("\n".join(add_list))
print("Wrote checks/_tmp_stage_list.txt with", len(add_list), "entries")
