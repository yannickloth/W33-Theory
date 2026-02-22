from pycryptosat import Solver

s = Solver()
# add contradictory XORs: x1 xor x2 xor x3 = 1 and x1 xor x2 xor x3 = 0
s.add_xor_clause([1, 2, 3], True)
s.add_xor_clause([1, 2, 3], False)
res = s.solve()
print("solve result", res)
print("conflict", s.get_conflict())
