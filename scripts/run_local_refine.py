import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.edge_to_e8_mapping import local_search_refine_mapping, run_geometry_mapping

m_geom, c_triples, geom_t = run_geometry_mapping()
print("Starting local search refinement from geometric mapping...")
refined, score = local_search_refine_mapping(
    m_geom, relation="abs1", iterations=20000, temp=0.01
)
print("Refined score:", score)
# Save a sample of refined mapping
import json
from pathlib import Path

from utils.json_safe import dump_json

OUT = Path("artifacts")
OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "refined_mapping_sample.json").open("w", encoding="utf-8") as f:
    sample = list(refined.items())[:50]
    dump_json({"score": score, "sample": sample}, f, indent=2)
print("Wrote artifacts/refined_mapping_sample.json")
