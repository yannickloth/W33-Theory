from pysat.card import CardEnc
from pysat.formula import IDPool

vpool = IDPool()
x_var = {(i, u): vpool.id(f"x_{i}_{u}") for i in range(27) for u in range(27)}
row = 21
lits = [x_var[(row, u)] for u in range(27)]
enc = CardEnc.equals(lits=lits, bound=1, encoding=1, vpool=vpool)
print("expected lits for row21:", lits[:5], "...", lits[-5:])
print("clauses count for row21 encode:", len(enc.clauses))
alo = [cl for cl in enc.clauses if set(cl) == set(lits)]
print("alo found?", bool(alo))
if alo:
    print("ALO length", len(alo[0]))
    print("ALO first 10 lits", alo[0][:10])
else:
    print("sample clauses:")
    for c in enc.clauses[:20]:
        print(c)
