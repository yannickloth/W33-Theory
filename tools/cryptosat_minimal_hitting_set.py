"""Find minimal hitting sets using CryptoMiniSat to quickly test core solvability"""

import json
from pathlib import Path

from pycryptosat import Solver

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

suns = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
with open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8") as f:
    sdata = json.load(f)
d_map_sign = {
    tuple(sorted(t["triple"])): t["sign"] for t in sdata["solution"]["d_triples"]
}
D_BITS = {
    t: (True if s == -1 else False) for t, s in d_map_sign.items()
}  # parity True=1

# collect union
union = set()
cores = []
for entry in suns:
    core = [tuple(sorted(tri)) for tri in entry["certificate_rows"]]
    cores.append(core)
    union.update(core)
union = sorted(union)
print("Union size:", len(union))

# test singleton hitting sets
hitting_singletons = []
for t in union:
    ok = True
    for core in cores:
        if t not in core:
            continue
        s = Solver()
        for tri in core:
            if tri == t:
                continue
            rhs = D_BITS.get(tri, False)
            s.add_xor_clause([tri[0] + 1, tri[1] + 1, tri[2] + 1], rhs)
        res = s.solve()
        if res[0]:
            # satisfiable after removing t: core - {t} is satisfiable; so t hits this core
            del s
            continue
        else:
            # still unsat -> t does not hit this core
            del s
            ok = False
            break
    if ok:
        hitting_singletons.append(list(t))

print("Singleton hitting sets found:", hitting_singletons)
open(ART / "cryptosat_singleton_hitting_sets.json", "w", encoding="utf-8").write(
    json.dumps(hitting_singletons, indent=2)
)
