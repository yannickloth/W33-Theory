import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.edge_to_e8_mapping import run_iterative_refinement

print("Running iterative refinement demo...")
mapping, anchors, transforms = run_iterative_refinement(max_iter=5, add_tol=1e-4)
print("Result: ", len(mapping), "anchors:", len(anchors))
