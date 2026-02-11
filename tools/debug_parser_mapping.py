import sys
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import json
from pathlib import Path

from tools.w33_rootword_uv_parser import W33RootwordParser

p = W33RootwordParser()
print("edge_to_root sample (first 20):")
for i, (k, v) in enumerate(sorted(p.edge_to_root.items())[:20]):
    print(k, v)
    if i > 18:
        break

minf = json.loads(
    Path(
        "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
    ).read_text(encoding="utf-8")
)
ent = next(e for e in minf if e.get("edge_roots_present"))
roots = [tuple(r) for r in ent["edge_roots"]]
print("\nSample roots and candidate edges:")
for r in roots:
    rt = tuple(int(x) for x in r)
    nrt = tuple(-x for x in rt)
    has = rt in p.vec_to_edge
    has_neg = nrt in p.vec_to_edge
    print(rt, "has->", p.vec_to_edge.get(rt), "neg_has->", p.vec_to_edge.get(nrt))

print("\nTry chain raw")
print(p._try_chain(roots))
