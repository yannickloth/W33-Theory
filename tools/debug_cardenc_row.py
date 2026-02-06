from pysat.card import CardEnc
from pysat.formula import IDPool

vpool = IDPool()
# create sample row x vars
lits = [vpool.id(f"x_21_{u}") for u in range(27)]
enc = CardEnc.equals(lits=lits, bound=1, encoding=1, vpool=vpool)
print("Total clauses for row encode:", len(enc.clauses))
# find clause that is ALO (contains all positive lits)
alo_clause = None
for cl in enc.clauses:
    if set(cl) == set(lits):
        alo_clause = cl
        break
print("ALO clause found?", bool(alo_clause))
if alo_clause:
    print("ALO length", len(alo_clause))
else:
    # print sample clauses
    print("sample clauses (first 10):")
    for c in enc.clauses[:10]:
        print(c)
