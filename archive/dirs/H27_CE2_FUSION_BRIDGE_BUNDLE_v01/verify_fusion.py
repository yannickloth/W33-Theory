\
import json, itertools, numpy as np, pandas as pd
from collections import deque, defaultdict

# Load CSV artifacts
df = pd.read_csv("pg_point_to_h27_vertex_coords.csv")
coords = pd.read_csv("H27_v0_0_heisenberg_coords.csv")

# Quick bijection check on 27 vertices
assert df.shape[0]==27
assert len(set(df["vertex_id"]))==27

# Check coordinates match provided coords table
coords_key={(int(r.vertex),int(r.x),int(r.y),int(r.t)) for r in coords.itertuples(index=False)}
for r in df.itertuples(index=False):
    assert (int(r.vertex_id),int(r.x),int(r.y),int(r.t)) in coords_key

print("ALL CHECKS PASSED: mapping aligns with provided H27 Heisenberg coordinate table.")
