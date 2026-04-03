"""Phase XXX Exploration Script A — Partition theory, modular arithmetic, and combinatorial identities."""
import math
from functools import lru_cache

# SRG constants
v, k, lam, mu, q = 40, 12, 2, 4, 3
E = 240; r = 2; s = -4; f = 24; g = 15
theta = 10; phi3 = 13; phi6 = 7; dimO = 8; N = 5; albert = 27; delta = 6

ALL = {'v':v,'k':k,'λ':lam,'μ':mu,'q':q,'E':E,'r':r,'s':s,'f':f,'g':g,
       'θ':theta,'Φ₃':phi3,'Φ₆':phi6,'dimO':dimO,'N':N,'albert':albert,'δ':delta}
VALS = set(ALL.values())

# ============ PARTITION FUNCTION p(n) ============
@lru_cache(maxsize=500)
def partition_p(n):
    if n < 0: return 0
    if n == 0: return 1
    total = 0
    for i in range(1, n+1):
        sign = (-1)**(i+1)
        g1 = i*(3*i-1)//2
        g2 = i*(3*i+1)//2
        if g1 <= n: total += sign * partition_p(n - g1)
        if g2 <= n: total += sign * partition_p(n - g2)
    return total

print("=== PARTITION FUNCTION p(n) ===")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val >= 1:
        pv = partition_p(val)
        hit = pv in VALS
        if hit or pv < 10000:
            print(f"  p({name}={val}) = {pv}" + (" *** HIT" if hit else ""))

# ============ PARTITION CONGRUENCES ============
print("\n=== PARTITION CONGRUENCES (Ramanujan) ===")
for n in range(200):
    pn = partition_p(n)
    if pn % 5 == 0 and n % 5 == 4:
        if n in VALS or pn in VALS:
            print(f"  p({n}) = {pn} ≡ 0 (mod 5), n ≡ 4 (mod 5)" + (f" n={n} in VALS" if n in VALS else "") + (f" p(n)={pn} in VALS" if pn in VALS else ""))

# ============ CATALAN NUMBERS ============
print("\n=== CATALAN NUMBERS ===")
for n in range(20):
    cn = math.comb(2*n, n) // (n+1)
    if cn in VALS:
        print(f"  C({n}) = {cn} *** HIT")

# ============ BELL NUMBERS ============
print("\n=== BELL NUMBERS ===")
def bell(n):
    if n == 0: return 1
    b = [[0]*(n+1) for _ in range(n+1)]
    b[0][0] = 1
    for i in range(1, n+1):
        b[i][0] = b[i-1][i-1]
        for j in range(1, i+1):
            b[i][j] = b[i][0] + b[i-1][j-1] if j == 1 else b[i][j-1] + b[i-1][j-1]
    return b[n][0]

for n in range(15):
    bn = bell(n)
    if bn in VALS:
        print(f"  B({n}) = {bn} *** HIT")

# ============ STIRLING NUMBERS (2nd kind) ============
print("\n=== STIRLING NUMBERS S(n,k) ===")
@lru_cache(maxsize=10000)
def stirling2(n, k):
    if n == 0 and k == 0: return 1
    if n == 0 or k == 0: return 0
    return k * stirling2(n-1, k) + stirling2(n-1, k-1)

for n in range(1, 15):
    for kk in range(1, n+1):
        s = stirling2(n, kk)
        if s in VALS and s > 1:
            print(f"  S({n},{kk}) = {s} *** HIT")

# ============ BERNOULLI NUMBERS (numerators) ============
print("\n=== BERNOULLI NUMBER CONNECTIONS ===")
from fractions import Fraction
@lru_cache(maxsize=200)
def bernoulli(n):
    if n == 0: return Fraction(1)
    if n == 1: return Fraction(-1, 2)
    if n % 2 == 1 and n > 1: return Fraction(0)
    s = Fraction(0)
    for kk in range(n):
        s += Fraction(math.comb(n+1, kk)) * bernoulli(kk)
    return -s / (n+1)

for n in range(0, 30, 2):
    bn = bernoulli(n)
    num = abs(bn.numerator)
    den = bn.denominator
    if num in VALS:
        print(f"  |B_{n}| numerator = {num} *** HIT")
    if den in VALS:
        print(f"  B_{n} denominator = {den} *** HIT")

# ============ DEDEKIND NUMBERS (small) ============
print("\n=== DEDEKIND NUMBERS ===")
dedekind = [2, 3, 6, 20, 168, 7581, 7828354]
for i, d in enumerate(dedekind):
    if d in VALS:
        print(f"  D({i}) = {d} *** HIT")

# ============ MOTZKIN NUMBERS ============
print("\n=== MOTZKIN NUMBERS ===")
def motzkin(n):
    if n <= 1: return 1
    m = [0]*(n+1)
    m[0] = m[1] = 1
    for i in range(2, n+1):
        m[i] = ((2*i+1)*m[i-1] + 3*(i-1)*m[i-2]) // (i+2) if ((2*i+1)*m[i-1] + 3*(i-1)*m[i-2]) % (i+2) == 0 else -1
    return m[n]

# Direct computation
motzkin_nums = [1, 1, 2, 4, 9, 21, 51, 127, 323, 835]
for i, m in enumerate(motzkin_nums):
    if m in VALS:
        print(f"  M({i}) = {m} *** HIT")

# ============ NARAYANA NUMBERS ============
print("\n=== NARAYANA NUMBERS N(n,k) ===")
for n in range(1, 12):
    for kk in range(1, n+1):
        nar = math.comb(n, kk) * math.comb(n, kk-1) // n
        if nar in VALS and nar > 1:
            print(f"  Nar({n},{kk}) = {nar} *** HIT")

# ============ EULER NUMBERS ============
print("\n=== EULER NUMBERS (tangent/secant) ===")
@lru_cache(maxsize=200)
def euler_number(n):
    if n == 0: return 1
    s = 0
    for kk in range(n):
        s += math.comb(n, kk) * euler_number(kk) * (-1)**(n-kk)
    # Actually use standard definition
    return 0  # Placeholder

# Use tangent numbers T_n instead
tangent = [0, 1, 0, 2, 0, 16, 0, 272]
secant = [1, 0, 1, 0, 5, 0, 61, 0, 1385]
for i, t in enumerate(tangent):
    if t in VALS and t > 1:
        print(f"  T_{i} (tangent) = {t} *** HIT")

# ============ MODULAR ARITHMETIC PATTERNS ============
print("\n=== MODULAR PATTERNS ===")
# Powers mod SRG values
for base_name, base in [('λ',lam),('q',q),('μ',mu),('N',N)]:
    for mod_name, mod in ALL.items():
        if mod > 1 and base != mod:
            for exp in range(1, 50):
                result = pow(base, exp, mod)
                if result == 0:
                    break
    # Discrete logarithm: find smallest e with base^e ≡ target (mod m)
    pass

# Check: 2^n mod various
print("\n=== 2^n mod SRG values ===")
for mod_name, mod in sorted(ALL.items(), key=lambda x: x[1]):
    if mod > 2:
        powers = []
        for n in range(1, mod+1):
            val_p = pow(2, n, mod)
            if val_p in VALS:
                powers.append((n, val_p))
        if powers:
            for n, vp in powers[:3]:
                print(f"  2^{n} mod {mod_name}={mod} = {vp}" + (" *** HIT" if vp in VALS else ""))

# ============ LUCAS NUMBERS ============
print("\n=== LUCAS NUMBERS ===")
lucas = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
for i, l in enumerate(lucas):
    if l in VALS:
        print(f"  L({i}) = {l} *** HIT")

# ============ PELL NUMBERS ============
print("\n=== PELL NUMBERS ===")
pell = [0, 1, 2, 5, 12, 29, 70, 169, 408]
for i, p in enumerate(pell):
    if p in VALS:
        print(f"  Pell({i}) = {p} *** HIT")

# ============ TRIBONACCI ============
print("\n=== TRIBONACCI NUMBERS ===")
trib = [0, 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149, 274]
for i, t in enumerate(trib):
    if t in VALS:
        print(f"  Trib({i}) = {t} *** HIT")

# ============ JACOBSTHAL NUMBERS ============
print("\n=== JACOBSTHAL NUMBERS ===")
jac = [0, 1, 1, 3, 5, 11, 21, 43, 85, 171]
for i, j in enumerate(jac):
    if j in VALS:
        print(f"  Jac({i}) = {j} *** HIT")

# ============ PERRIN SEQUENCE ============
print("\n=== PERRIN SEQUENCE ===")
perrin = [3, 0, 2, 3, 2, 5, 5, 7, 10, 12, 17, 22, 29, 39]
for i, p in enumerate(perrin):
    if p in VALS:
        print(f"  Perrin({i}) = {p} *** HIT")

# ============ PADOVAN SEQUENCE ============
print("\n=== PADOVAN SEQUENCE ===")
padovan = [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 16, 21, 28, 37, 49]
for i, p in enumerate(padovan):
    if p in VALS:
        print(f"  Padovan({i}) = {p} *** HIT")

# ============ PRIMITIVE ROOTS ============
print("\n=== PRIMITIVE ROOTS ===")
def primitive_roots(p):
    if p < 2: return []
    roots = []
    phi_p = p - 1  # For prime p
    for g_cand in range(2, p):
        if pow(g_cand, phi_p, p) == 1:
            is_prim = True
            # Check all proper divisors of phi_p
            temp = phi_p
            factors = set()
            d = 2
            while d*d <= temp:
                while temp % d == 0:
                    factors.add(d)
                    temp //= d
                d += 1
            if temp > 1:
                factors.add(temp)
            for fac in factors:
                if pow(g_cand, phi_p // fac, p) == 1:
                    is_prim = False
                    break
            if is_prim:
                roots.append(g_cand)
    return roots

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val > 2:
        # Check if val is prime
        is_prime = all(val % i != 0 for i in range(2, int(val**0.5)+1)) and val > 1
        if is_prime:
            roots = primitive_roots(val)
            num_roots = len(roots)
            smallest = roots[0] if roots else None
            if num_roots in VALS:
                print(f"  #{'{'}prim roots mod {name}={val}{'}'} = {num_roots} *** HIT")
            if smallest in VALS:
                print(f"  smallest prim root mod {name}={val} = {smallest} *** HIT")

# ============ WILSON QUOTIENT ============
print("\n=== WILSON QUOTIENTS ===")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val > 1:
        is_prime = all(val % i != 0 for i in range(2, int(val**0.5)+1)) and val > 1
        if is_prime:
            wq = (math.factorial(val-1) + 1) // val
            if wq % val == 0:
                print(f"  Wilson quotient W({name}={val}) is divisible by {val} (Wilson prime)")

# ============ SUBFACTORIAL (DERANGEMENTS) ============
print("\n=== DERANGEMENTS !n ===")
def subfactorial(n):
    if n == 0: return 1
    if n == 1: return 0
    return (n-1) * (subfactorial(n-1) + subfactorial(n-2))

for n in range(1, 15):
    dn = subfactorial(n)
    if dn in VALS:
        print(f"  !{n} = {dn} *** HIT")

# ============ CARMICHAEL FUNCTION ============
print("\n=== CARMICHAEL FUNCTION λ(n) ===")
def carmichael_lambda(n):
    if n <= 2: return 1
    # factorize
    factors = {}
    temp = n
    d = 2
    while d*d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    
    result = 1
    for p, e in factors.items():
        if p == 2 and e >= 3:
            pe = p**(e-2)  # λ(2^e) = 2^(e-2) for e≥3
        elif p == 2 and e == 2:
            pe = 2
        elif p == 2 and e == 1:
            pe = 1
        else:
            pe = (p-1) * p**(e-1)  # λ(p^e) = φ(p^e) for odd p
        result = result * pe // math.gcd(result, pe)
    return result

print("  Carmichael λ(n) for SRG values:")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val > 1:
        cl = carmichael_lambda(val)
        hit = cl in VALS
        if hit:
            print(f"  λ_c({name}={val}) = {cl}" + " *** HIT")

# ============ REPUNIT DIVISIBILITY ============
print("\n=== REPUNIT CONNECTIONS ===")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val > 1 and math.gcd(val, 10) == 1:
        # Find smallest n with val | R_n (repunit 111...1)
        r = 0
        for n in range(1, 500):
            r = (r * 10 + 1) % val
            if r == 0:
                if n in VALS:
                    print(f"  {name}={val} divides R_{n} *** HIT (n in VALS)")
                break

# ============ PERFECT POWER CHECK ============
print("\n=== PERFECT POWERS IN SRG ===")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val > 1:
        for base in range(2, val):
            for exp in range(2, 20):
                if base**exp == val:
                    print(f"  {name}={val} = {base}^{exp}")
                elif base**exp > val:
                    break

# ============ DIGIT SUM IN VARIOUS BASES ============
print("\n=== DIGIT SUM IN BASE q=3 ===")
def digit_sum_base(n, b):
    s = 0
    while n > 0:
        s += n % b
        n //= b
    return s

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val >= 1:
        ds3 = digit_sum_base(val, 3)
        if ds3 in VALS:
            print(f"  S_3({name}={val}) = {ds3}" + " *** HIT")

# ============ DIGITAL ROOT ============
print("\n=== DIGITAL ROOT (base 10) ===")
def digital_root(n):
    if n == 0: return 0
    return 1 + (n-1) % 9

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val >= 1:
        dr = digital_root(val)
        if dr in VALS:
            print(f"  dr({name}={val}) = {dr}" + " *** HIT")

# ============ ARITHMETIC PROGRESSION DETECTION ============
print("\n=== ARITHMETIC PROGRESSIONS IN SRG VALUES ===")
sorted_vals = sorted(VALS)
for i in range(len(sorted_vals)):
    for j in range(i+1, len(sorted_vals)):
        d = sorted_vals[j] - sorted_vals[i]
        # Check how long the AP continues
        length = 2
        nxt = sorted_vals[j] + d
        while nxt in VALS:
            length += 1
            nxt += d
        if length >= 3:
            ap = [sorted_vals[i] + d*step for step in range(length)]
            print(f"  AP with d={d}: {ap}")

# ============ SUM/PRODUCT IDENTITIES ============
print("\n=== SUM/PRODUCT IDENTITIES ===")
vals_list = sorted(VALS)
# Check pairs that sum to SRG values
for i in range(len(vals_list)):
    for j in range(i, len(vals_list)):
        s = vals_list[i] + vals_list[j]
        if s in VALS:
            print(f"  {vals_list[i]} + {vals_list[j]} = {s}")

print("\n=== PRODUCT PAIRS ===")
for i in range(len(vals_list)):
    for j in range(i, len(vals_list)):
        p = vals_list[i] * vals_list[j]
        if p in VALS:
            print(f"  {vals_list[i]} × {vals_list[j]} = {p}")

print("\n=== DIFFERENCE PAIRS ===")
for i in range(len(vals_list)):
    for j in range(i+1, len(vals_list)):
        d = vals_list[j] - vals_list[i]
        if d in VALS:
            print(f"  {vals_list[j]} - {vals_list[i]} = {d}")

# ============ POWER SUM ============
print("\n=== POWER SUM IDENTITIES ===")
for p_exp in range(2, 5):
    # Sum of p-th powers of small SRG constants
    subsets = [(lam, q), (lam, mu), (lam, q, mu), (q, mu, N)]
    for sub in subsets:
        ps = sum(x**p_exp for x in sub)
        if ps in VALS:
            print(f"  Σ x^{p_exp} for x∈{sub} = {ps} *** HIT")

# ============ RISING/FALLING FACTORIALS ============
print("\n=== RISING FACTORIALS (Pochhammer) ===")
for name1, val1 in ALL.items():
    for name2, val2 in ALL.items():
        if 0 < val2 <= 6 and val1 > 0:
            # (val1)_val2 = val1 * (val1+1) * ... * (val1+val2-1)
            rf = 1
            for i in range(val2):
                rf *= (val1 + i)
            if rf in VALS:
                print(f"  ({name1}={val1})_{'{'}({name2}={val2}){'}'} = {rf} *** HIT")

print("\n\n=== EXPLORATION 30A COMPLETE ===")
