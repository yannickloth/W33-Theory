import json
import sys
from pathlib import Path
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from tools.w33_rootword_uv_parser import W33RootwordParser

p = W33RootwordParser()
minf = json.loads(
    Path(
        "analysis/minimal_commutator_cycles/minimal_holonomy_cycles_ordered_rootwords.json"
    ).read_text(encoding="utf-8")
)
ent = next(e for e in minf if e.get("edge_roots_present"))
rootword = ent["edge_roots"]
roots = [tuple(int(x) for x in r) for r in rootword]

print("vec_to_edges_map keys sample (count):", len(p.vec_to_edges_map))
print("candidates for each root:")
for idx, r in enumerate(roots):
    rt = tuple(int(x) for x in r)
    nrt = tuple(-x for x in rt)
    c1 = p.vec_to_edges_map.get(rt, [])
    c2 = p.vec_to_edges_map.get(nrt, [])
    print(idx, rt, "->", c1, c2)

# attempt to enumerate closed chains (bounded to 2000 solutions)
print("\nEnumerating closed chains (bounded)")
candidates = []
for r in roots:
    rt = tuple(int(x) for x in r)
    nrt = tuple(-x for x in rt)
    c = []
    c.extend(p.vec_to_edges_map.get(rt, []))
    c.extend(p.vec_to_edges_map.get(nrt, []))
    candidates.append(c)

solutions = []
chosen = [None] * len(candidates)

MAX_SOL = 2000


def dfs(i):
    if len(solutions) >= MAX_SOL:
        return
    if i == len(candidates):
        # check closure
        if chosen[-1][0][1] == chosen[0][0][0]:
            solutions.append(list(chosen))
        return
    for cand in candidates[i]:
        if i == 0:
            chosen[0] = cand
            dfs(1)
        else:
            prev = chosen[i - 1][0]
            curr = cand[0]
            if prev[1] == curr[0]:
                chosen[i] = cand
                dfs(i + 1)


dfs(0)
print("found", len(solutions), "solutions")


def canonicalize_cycle(cyc):
    from tools.w33_rootword_uv_parser import W33RootwordParser as _P

    q = _P()
    return tuple(q._find_canonical_cycle_rotation(cyc))


for sol in solutions[:200]:
    cyc = [sol[0][0][0]] + [e[0][1] for e in sol]
    cyc = cyc[:-1]
    tags = [tag for (_, tag) in sol]
    can = canonicalize_cycle(cyc)
    score = sum(1 for (_e, t) in sol if t == "canon")
    print("cycle", cyc, "canon", can, "score", score, "tags", tags)
