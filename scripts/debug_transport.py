import sys
from pathlib import Path

# make sure repo root and scripts are on sys.path
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from ce2_global_cocycle import predict_ce2_uv, transport_ce2_uv_under_e6_monomial
from e6_hessian_tritangents import hessian_monomial_generators

# sample triple

a_pair = (0, 0)

b_pair = (17, 1)

c_pair = (3, 0)

print("sample triple", a_pair, b_pair, c_pair)

pred = predict_ce2_uv(a_pair, b_pair, c_pair)
print("pred ->", pred)

# locate index of V
for idx, coeff in pred.V:
    print("orig V index", idx, coeff)

gens = hessian_monomial_generators()

for name, (perm, eps) in gens.items():
    if name == "T10":
        print("generator", name)
        print("perm", perm)
        # compute parity of perm
        parity = 1
        seen = set()
        for i in range(len(perm)):
            if i not in seen:
                cycle = []
                j = i
                while j not in seen:
                    seen.add(j)
                    cycle.append(j)
                    j = perm[j]
                if len(cycle) % 2 == 0:
                    parity *= -1
        print("parity sign", parity)
        print("eps", eps)
        # compute transported
        transported = transport_ce2_uv_under_e6_monomial(
            pred, a=a_pair, b=b_pair, c=c_pair, perm=perm, eps=eps
        )
        print("transported V", transported.V)
        # compute pred2
        a2 = (perm[a_pair[0]], a_pair[1])
        b2 = (perm[b_pair[0]], b_pair[1])
        c2 = (perm[c_pair[0]], c_pair[1])
        pred2 = predict_ce2_uv(a2, b2, c2)
        print("pred2", pred2)
        print("pred2 V", pred2.V)
        print("equality", transported == pred2)
        # compute sign contributions
        idx, coeff = pred.V[0]
        # transport formula
        r = idx // 27
        col = idx % 27
        r2 = perm[r]
        c2 = perm[col]
        phase_a = eps[perm[a_pair[0]]]
        phase_c = eps[perm[c_pair[0]]]
        conj_coeff = coeff * eps[r2] * eps[c2]
        out_coeff = conj_coeff * phase_a * phase_c
        print("detailed", r, col, r2, c2, coeff, eps[r2], eps[c2], phase_a, phase_c, conj_coeff, out_coeff)

