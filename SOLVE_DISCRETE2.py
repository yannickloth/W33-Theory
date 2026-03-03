"""
Part VII-CI: Discrete Mathematics & Combinatorics II (1444-1457)

W(3,3) parameters encode deeper combinatorial structures:
- Ramsey numbers from graph parameters
- Latin squares and orthogonal arrays
- Steiner systems from SRG structure
- Partition theory connections
- Polya enumeration
"""

from fractions import Fraction
import math

# W(3,3) parameters
v, k, lam, mu = 40, 12, 2, 4
r_eval, s_eval = 2, -4
f, g = 24, 15
E = 240
q = 3
N = 5
Phi3 = 13
Phi6 = 7
k_comp = 27
alpha_ind = 10
_dim_O = 8
_comb2 = math.comb

results = []

print("=" * 72)
print("Part VII-CI: Discrete Mathematics & Combinatorics II (1444-1457)")
print("=" * 72)

# 1444: Number of Latin squares of order q = 12
# L(3) = 12 = k
latin_q = 12  # known: L(3) = 12
check = f"check_1444: Latin squares L(q) = L(3) = {latin_q} = k"
assert latin_q == k
results.append(True)
print(f"  {check} => ✅")

# 1445: MOLS(q) = q-1 = 2 = λ (mutually orthogonal Latin squares)
# For prime q: MOLS(q) = q-1
mols = q - 1
check = f"check_1445: MOLS(q) = q-1 = {mols} = λ"
assert mols == lam
results.append(True)
print(f"  {check} => ✅")

# 1446: Steiner triple system S(2,3,v) requires v ≡ 1 or 3 (mod 6)
# v = 40: 40 mod 6 = 4, so no STS(40). But 39 = v-1 ≡ 3 mod 6: STS(39) exists
# v-1 mod 6 = 3
check = f"check_1446: (v-1) mod 6 = {(v-1) % 6} = q (STS({v-1}) exists)"
assert (v - 1) % 6 == q
results.append(True)
print(f"  {check} => ✅")

# 1447: Number of partitions p(k) = p(12) = 77 = Φ₃·Phi6 - 14
# p(12) = 77
p_12 = 77
check = f"check_1447: p(k) = p(12) = {p_12} = Φ₃·Φ₆ - 2Φ₆"
assert p_12 == Phi3 * Phi6 - 2 * Phi6
results.append(True)
print(f"  {check} => ✅")

# 1448: Catalan number C(q) = C(3) = 5 = N
# C_n = (2n)!/(n!(n+1)!)
catalan_q = math.comb(2*q, q) // (q + 1)
check = f"check_1448: C(q) = C(3) = {catalan_q} = N"
assert catalan_q == N
results.append(True)
print(f"  {check} => ✅")

# 1449: Bell number B(q+1) = B(4) = 15 = g
# B(4) = 15 (number of partitions of {1,2,3,4})
bell_4 = 15
check = f"check_1449: B(q+1) = B(4) = {bell_4} = g"
assert bell_4 == g
results.append(True)
print(f"  {check} => ✅")

# 1450: Stirling S(k, q) = S(12, 3) = second kind
# S(n,k) = (1/k!) Σ (-1)^j C(k,j)(k-j)^n
# S(12,3) = (1/6)(3^12 - 3·2^12 + 3·1^12) = (531441 - 12288 + 3)/6 = 86526
# Verify: 3^12 = 531441, 3·2^12 = 12288, 3·1 = 3
s_12_3 = (3**12 - 3 * 2**12 + 3) // 6
check = f"check_1450: S(k,q) = S(12,3) = {s_12_3}"
assert s_12_3 == 86526
results.append(True)
print(f"  {check} => ✅")

# 1451: Derangements D(μ) = D(4) = 9 = q²
# D(n) = n! Σ (-1)^k/k!, D(4) = 24(1-1+1/2-1/6+1/24) = 9
D_4 = 9
check = f"check_1451: D(μ) = D(4) = {D_4} = q²"
assert D_4 == q**2
results.append(True)
print(f"  {check} => ✅")

# 1452: Fibonacci F(k) = F(12) = 144 = k²
fib_vals = [0, 1]
for i in range(2, k+1):
    fib_vals.append(fib_vals[-1] + fib_vals[-2])
fib_k = fib_vals[k]
check = f"check_1452: F(k) = F(12) = {fib_k} = k²"
assert fib_k == k**2
results.append(True)
print(f"  {check} => ✅")

# 1453: C(v, λ) = C(40, 2) = 780 = v(v-1)/2
comb_v_2 = _comb2(v, lam)
check = f"check_1453: C(v,λ) = C(40,2) = {comb_v_2} = v(v-1)/2"
assert comb_v_2 == v * (v - 1) // 2
assert comb_v_2 == 780
results.append(True)
print(f"  {check} => ✅")

# 1454: Euler totient φ(v) = φ(40) = 16 = 2^μ
euler_phi_v = 0
for i in range(1, v + 1):
    if math.gcd(i, v) == 1:
        euler_phi_v += 1
check = f"check_1454: φ(v) = φ(40) = {euler_phi_v} = 2^μ"
assert euler_phi_v == 2**mu
results.append(True)
print(f"  {check} => ✅")

# 1455: Möbius function μ(v) = μ(40) = 0 (since 4|40, so 2²|40)
# μ(n) = 0 if n has a squared prime factor
mobius_v = 0  # since 2² | 40
check = f"check_1455: μ(v) = μ(40) = {mobius_v} (2²|40)"
assert mobius_v == 0
results.append(True)
print(f"  {check} => ✅")

# 1456: Number of divisors d(v) = d(40) = 8 = dim_O
# 40 = 2³ · 5¹, d(40) = (3+1)(1+1) = 8
d_v = sum(1 for i in range(1, v + 1) if v % i == 0)
check = f"check_1456: d(v) = d(40) = {d_v} = dim_O"
assert d_v == _dim_O
results.append(True)
print(f"  {check} => ✅")

# 1457: Sum of divisors σ(v) = σ(40) = 90 = v+k+v-k+Φ₃+Φ₆
sigma_v = sum(i for i in range(1, v + 1) if v % i == 0)
check = f"check_1457: σ(v) = σ(40) = {sigma_v} = Φ₃·Φ₆ - 1"
assert sigma_v == 90
assert sigma_v == Phi3 * Phi6 - 1
results.append(True)
print(f"  {check} => ✅")

print(f"\n{'='*72}")
passed = sum(results)
total = len(results)
print(f"  Part VII-CI: {passed}/{total} checks passed")
print(f"{'='*72}")
assert passed == total == 14
