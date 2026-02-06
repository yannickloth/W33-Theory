from pysat.solvers import Solver

s = Solver(name="crypto")
# add contradictory xor
s.add_xor([1, 2, 3], True)
s.add_xor([1, 2, 3], False)
res = s.solve()
print("solve", res)
try:
    print("core", s.get_core())
except Exception as e:
    print("get_core error", e)

s.delete()
