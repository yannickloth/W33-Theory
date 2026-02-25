import sympy as sp

vals=[0.3066628615989846, 0.31973384590377835]
for v in vals:
    print('v=',v,'nsimplify->', sp.nsimplify(v, [sp.sqrt(2), sp.sqrt(3), sp.pi]))
