#!/usr/bin/env python3
import sys
from pathlib import Path as _Path

# ensure repo root is on sys.path so `tools` can be imported when run as a script
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from pathlib import Path

from tools.extract_e8_rootword_cocycle import load_edge_root_map

m = load_edge_root_map(Path("artifacts/edge_to_e8_root_combined.json"))
edges = [(17, 18), (17, 28), (26, 27), (28, 3), (20, 35), (34, 37)]
for e in edges:
    print(e, e in m, m.get(e))
