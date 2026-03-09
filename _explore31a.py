"""Phase XXXI Exploration Script A — Deeper number theory & algebraic structures"""
import math
from itertools import combinations, product
from functools import reduce

# SRG(40,12,2,4) parameters
v, k, lam, mu, q = 40, 12, 2, 4, 3
E = v * k // 2  # 240
r, s = 2, -4
f, g = 24, 15
theta, phi3, phi6 = 10, 13, 7
dimO, N, albert, delta = 8, 5, 27, 6

ALL = {'v': v, 'k': k, 'lam': lam, 'mu': mu, 'q': q, 'E': E, 'r': r, 's': s,
       'f': f, 'g': g, 'theta': theta, 'phi3': phi3, 'phi6': phi6,
       'dimO': dimO, 'N': N, 'albert': albert, 'delta': delta}
SRG_SET = set(ALL.values())

print("="*70)
print("PHASE XXXI EXPLORATION A")
print("="*70)

# 1. Dedekind numbers
print("\n--- 1. Dedekind Numbers ---")
# D(0)=2, D(1)=3, D(2)=6, D(3)=20, D(4)=168
dedekind = [2, 3, 6, 20, 168]
for i, d in enumerate(dedekind):
    if d in SRG_SET:
        names = [n for n, val in ALL.items() if val == d]
        print(f"  D({i}) = {d} = {names}")
    # check ratios/combos
for i in range(len(dedekind)):
    for j in range(i+1, len(dedekind)):
        ratio = dedekind[j] / dedekind[i]
        if ratio == int(ratio) and int(ratio) in SRG_SET:
            names = [n for n, val in ALL.items() if val == int(ratio)]
            print(f"  D({j})/D({i}) = {dedekind[j]}/{dedekind[i]} = {int(ratio)} = {names}")

# 2. Bernoulli numbers (numerators)
print("\n--- 2. Bernoulli Numbers ---")
from fractions import Fraction
def bernoulli(n):
    B = [Fraction(0)] * (n + 1)
    B[0] = Fraction(1)
    for m in range(1, n + 1):
        B[m] = Fraction(0)
        for kk in range(m):
            B[m] -= math.comb(m + 1, kk) * B[kk]
        B[m] /= (m + 1)
    return B

bern = bernoulli(20)
for i, b in enumerate(bern):
    if b != 0:
        num = abs(b.numerator)
        den = b.denominator
        if num in SRG_SET and num > 1:
            names = [n for n, val in ALL.items() if val == num]
            print(f"  |B_{i} num| = {num} = {names} (B_{i} = {b})")
        if den in SRG_SET and den > 1:
            names = [n for n, val in ALL.items() if val == den]
            print(f"  B_{i} den = {den} = {names} (B_{i} = {b})")

# 3. Catalan numbers
print("\n--- 3. Catalan Numbers ---")
for i in range(15):
    c = math.comb(2*i, i) // (i + 1)
    if c in SRG_SET:
        names = [n for n, val in ALL.items() if val == c]
        print(f"  C({i}) = {c} = {names}")
    for name, val in ALL.items():
        if val > 1 and c > 1 and c % val == 0 and c // val in SRG_SET:
            names2 = [n for n, v2 in ALL.items() if v2 == c // val]
            print(f"  C({i})/{name} = {c}/{val} = {c//val} = {names2}")

# 4. Motzkin numbers
print("\n--- 4. Motzkin Numbers ---")
motzkin = [1, 1, 2, 4, 9, 21, 51, 127, 323, 835]
for i, m in enumerate(motzkin):
    if m in SRG_SET:
        names = [n for n, val in ALL.items() if val == m]
        print(f"  Motz({i}) = {m} = {names}")

# 5. Euler numbers
print("\n--- 5. Euler Numbers ---")
def euler_numbers(n):
    """Compute Euler numbers E_0, E_2, E_4, ..."""
    # Secant numbers: E_0=1, E_2=-1, E_4=5, E_6=-61, E_8=1385, ...
    # But tangent numbers (odd-indexed zigzag): T_1=1, T_3=2, T_5=16, T_7=272
    # Zigzag numbers (up/down): A_0=1, A_1=1, A_2=1, A_3=2, A_4=5, A_5=16, A_6=61
    zigzag = [0] * (n + 1)
    zigzag[0] = 1
    for i in range(1, n + 1):
        zigzag[i] = 0
        # Use recurrence
        if i == 1:
            zigzag[1] = 1
        else:
            # A(n) = sum over ... alternating tangent/secant
            pass
    # Direct computation
    result = []
    for m in range(n + 1):
        # Euler zigzag number via explicit formula
        if m == 0:
            result.append(1)
        elif m == 1:
            result.append(1)
        else:
            # A(n) can be computed via matrix method
            T = [0] * (m + 1)
            T[0] = 1
            for i in range(1, m + 1):
                for j in range(i, 0, -1):
                    T[j] = T[j] + T[j-1]
                if i % 2 == 0:
                    for j in range(i, 0, -1):
                        T[j] = T[j] + T[j-1]
                else:
                    for j in range(0, i):
                        T[j] = T[j] + T[j+1]
            result.append(T[0] if m % 2 == 0 else T[m])
    return result

# Simpler: compute zigzag/tangent numbers directly
# A000111: 1, 1, 1, 2, 5, 16, 61, 272, 1385
# Tangent numbers: 1, 2, 16, 272, 7936
# Secant numbers: 1, 1, 5, 61, 1385
print("  Tangent numbers: T(1)=1, T(3)=2, T(5)=16, T(7)=272")
tangent = [1, 2, 16, 272]
for i, t in enumerate(tangent):
    idx = 2*i + 1
    if t in SRG_SET:
        names = [n for n, val in ALL.items() if val == t]
        print(f"  T({idx}) = {t} = {names}")

print("  Secant numbers: E(0)=1, E(2)=1, E(4)=5, E(6)=61, E(8)=1385")
secant = [1, 1, 5, 61, 1385]
for i, sc in enumerate(secant):
    idx = 2*i
    if sc in SRG_SET:
        names = [n for n, val in ALL.items() if val == sc]
        print(f"  E({idx}) = {sc} = {names}")

# 6. Divisor function values
print("\n--- 6. Divisor Function σ_k(n) ---")
def sigma(n, kk):
    """Sum of kth powers of divisors of n"""
    return sum(d**kk for d in range(1, n+1) if n % d == 0)

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    for kk in range(1, 6):
        s_val = sigma(val, kk)
        if s_val in SRG_SET:
            names2 = [n for n, v2 in ALL.items() if v2 == s_val]
            print(f"  σ_{kk}({name}={val}) = {s_val} = {names2}")

# 7. Sum-of-divisors chain
print("\n--- 7. Aliquot/Sum-of-divisors chain ---")
def aliquot(n):
    """Sum of proper divisors"""
    return sum(d for d in range(1, n) if n % d == 0)

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    s = aliquot(val)
    if s in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == s]
        print(f"  s({name}={val}) = {s} = {names2}")
    # Second iterate
    if s > 0:
        s2 = aliquot(s)
        if s2 in SRG_SET:
            names2 = [n for n, v2 in ALL.items() if v2 == s2]
            print(f"  s(s({name}={val})) = s({s}) = {s2} = {names2}")

# 8. Radical (product of distinct prime factors)
print("\n--- 8. Radical rad(n) ---")
def radical(n):
    r = 1
    for p in range(2, n+1):
        if n % p == 0:
            r *= p
            while n % p == 0:
                n //= p
    return r

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    rad = radical(val)
    if rad in SRG_SET and rad != val:
        names2 = [n for n, v2 in ALL.items() if v2 == rad]
        print(f"  rad({name}={val}) = {rad} = {names2}")

# 9. Multiplicative order
print("\n--- 9. Multiplicative Order ord_n(a) ---")
def mult_order(a, n):
    """Order of a modulo n"""
    if math.gcd(a, n) != 1:
        return None
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
        if order > n:
            return None
    return order

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    for a in range(2, 20):
        if math.gcd(a, val) != 1:
            continue
        o = mult_order(a, val)
        if o and o in SRG_SET:
            names2 = [n for n, v2 in ALL.items() if v2 == o]
            # Only print interesting ones
            if o != val and o > 1:
                print(f"  ord_{val}({a}) = {o} = {names2}")

# 10. Primitive roots
print("\n--- 10. Primitive Roots ---")
def primitive_root_count(n):
    """Count of primitive roots mod n"""
    if n <= 1:
        return 0
    # Primitive roots exist iff n = 1, 2, 4, p^k, 2p^k
    count = 0
    for a in range(1, n):
        if math.gcd(a, n) == 1:
            o = mult_order(a, n)
            if o == n - 1:  # For primes, euler_phi(n) = n-1
                count += 1
    return count

# Number of primitive roots mod p = phi(p-1)
for name, val in [('N', 5), ('phi6', 7), ('phi3', 13)]:
    count = primitive_root_count(val)
    if count in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == count]
        print(f"  #PrimRoots(mod {name}={val}) = φ({val}-1) = {count} = {names2}")
    # Smallest primitive root
    for a in range(2, val):
        if math.gcd(a, val) == 1:
            o = mult_order(a, val)
            if o == val - 1:
                if a in SRG_SET:
                    names2 = [n for n, v2 in ALL.items() if v2 == a]
                    print(f"  smallest prim root mod {val} = {a} = {names2}")
                break

# 11. Legendre symbol / Quadratic residues
print("\n--- 11. Quadratic Residue Counts ---")
for p in [5, 7, 13, 3]:
    if p < 3:
        continue
    qr_count = len(set(a*a % p for a in range(1, p)))
    if qr_count in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == qr_count]
        print(f"  #QR(mod {p}) = {qr_count} = {names2}")

# 12. Mobius function chain
print("\n--- 12. Mertens function M(n) ---")
def mobius(n):
    if n == 1:
        return 1
    # Factor
    factors = []
    temp = n
    for p in range(2, int(math.sqrt(n)) + 2):
        if temp % p == 0:
            count = 0
            while temp % p == 0:
                temp //= p
                count += 1
            if count > 1:
                return 0
            factors.append(p)
    if temp > 1:
        factors.append(temp)
    return (-1)**len(factors)

def mertens(n):
    return sum(mobius(i) for i in range(1, n+1))

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    m = mertens(val)
    if abs(m) in SRG_SET and abs(m) > 1:
        names2 = [n for n, v2 in ALL.items() if v2 == abs(m)]
        print(f"  M({name}={val}) = {m}, |M| = {abs(m)} = {names2}")

# 13. Primorial / factorial ratios
print("\n--- 13. Factorial & Primorial Ratios ---")
factorials = {i: math.factorial(i) for i in range(1, 15)}
for i in range(2, 12):
    for j in range(1, i):
        ratio = factorials[i] // factorials[j]
        if ratio in SRG_SET:
            names = [n for n, val in ALL.items() if val == ratio]
            print(f"  {i}!/{j}! = {ratio} = {names}")

# Primorial
primorial = [1]
primes = [2, 3, 5, 7, 11, 13]
p = 1
for pr in primes:
    p *= pr
    primorial.append(p)

for i in range(len(primorial)):
    if primorial[i] in SRG_SET:
        names = [n for n, val in ALL.items() if val == primorial[i]]
        print(f"  primorial({primes[i-1] if i > 0 else 1}) = {primorial[i]} = {names}")

# 14. Continued fraction of sqrt(SRG values)
print("\n--- 14. Continued Fractions ---")
def cf_sqrt(n, terms=10):
    """Continued fraction expansion of sqrt(n)"""
    a0 = int(math.sqrt(n))
    if a0 * a0 == n:
        return [a0]
    cf = [a0]
    m, d, a = 0, 1, a0
    for _ in range(terms):
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        cf.append(a)
        if a == 2 * a0:
            break
    return cf

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    sqrt_val = math.sqrt(val)
    if sqrt_val != int(sqrt_val):
        cf = cf_sqrt(val)
        period = cf[1:]
        period_len = len(period)
        if period_len in SRG_SET and period_len > 1:
            names2 = [n for n, v2 in ALL.items() if v2 == period_len]
            print(f"  CF period len(√{name}={val}) = {period_len} = {names2}")
        # Sum of period
        period_sum = sum(period)
        if period_sum in SRG_SET:
            pass # too noisy

# 15. Perfect power check / p-adic valuations
print("\n--- 15. p-adic Valuations ---")
def p_adic_val(n, p):
    """p-adic valuation of n"""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v

# v_p(n!) = Legendre's formula
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    for p in [2, 3, 5, 7]:
        leg = 0
        pk = p
        while pk <= val:
            leg += val // pk
            pk *= p
        if leg in SRG_SET and leg > 1:
            names2 = [n for n, v2 in ALL.items() if v2 == leg]
            print(f"  v_{p}({name}!={val}!) = {leg} = {names2}")

# 16. Polygonal root
print("\n--- 16. Polygonal Root Tests ---")
def is_s_gonal(n, s):
    """Check if n is an s-gonal number, return index if so"""
    # n = k((s-2)k - (s-4))/2
    # (s-2)k^2 - (s-4)k - 2n = 0
    a = s - 2
    b = -(s - 4)
    c = -2 * n
    disc = b*b - 4*a*c
    if disc < 0:
        return None
    sqrt_disc = int(math.sqrt(disc))
    if sqrt_disc * sqrt_disc != disc:
        return None
    kk = (-b + sqrt_disc) / (2 * a)
    if kk == int(kk) and kk > 0:
        return int(kk)
    return None

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 3:
        continue
    for s in range(3, 20):
        idx = is_s_gonal(val, s)
        if idx and idx in SRG_SET and idx > 1:
            names2 = [n for n, v2 in ALL.items() if v2 == idx]
            print(f"  {name}={val} is {s}-gonal at index {idx} = {names2}")

# 17. Kaprekar routine
print("\n--- 17. Digital Root ---")
def digital_root(n, base=10):
    while n >= base:
        n = sum(int(d) for d in str(n)) if base == 10 else sum_digits(n, base)
    return n

def sum_digits(n, base):
    s = 0
    while n > 0:
        s += n % base
        n //= base
    return s

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    for base in [2, 10]:
        dr = digital_root(val, base)
        if dr in SRG_SET and dr > 1 and dr != val:
            names2 = [n for n, v2 in ALL.items() if v2 == dr]
            if base == 10:
                print(f"  DR_10({name}={val}) = {dr} = {names2}")

# 18. Collatz stopping time
print("\n--- 18. Collatz Stopping Time ---")
def collatz_steps(n):
    """Steps to reach 1"""
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3*n + 1
        steps += 1
        if steps > 1000:
            return -1
    return steps

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    steps = collatz_steps(val)
    if steps in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == steps]
        print(f"  Collatz({name}={val}) = {steps} steps = {names2}")

# 19. Egyptian fraction / Harmonic numbers
print("\n--- 19. Harmonic Numbers ---")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    h = Fraction(0)
    for i in range(1, val + 1):
        h += Fraction(1, i)
    if h.numerator in SRG_SET and h.numerator > 1:
        names2 = [n for n, v2 in ALL.items() if v2 == h.numerator]
        print(f"  H({name}={val}) numerator = {h.numerator} = {names2}")
    if h.denominator in SRG_SET and h.denominator > 1:
        names2 = [n for n, v2 in ALL.items() if v2 == h.denominator]
        print(f"  H({name}={val}) denominator = {h.denominator} = {names2}")

# 20. Sum/product of consecutive primes
print("\n--- 20. Consecutive Prime Sums ---")
for start in range(20):
    primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for length in range(2, 10):
        if start + length <= len(primes_list):
            s = sum(primes_list[start:start+length])
            if s in SRG_SET:
                names = [n for n, val in ALL.items() if val == s]
                seg = primes_list[start:start+length]
                print(f"  Σ primes[{start}:{start+length}] = {seg} = {s} = {names}")

# 21. Fermat numbers
print("\n--- 21. Fermat & Mersenne ---")
for i in range(8):
    fermat = 2**(2**i) + 1
    if fermat in SRG_SET:
        names = [n for n, val in ALL.items() if val == fermat]
        print(f"  F_{i} = {fermat} = {names}")

for i in range(2, 12):
    mersenne = 2**i - 1
    if mersenne in SRG_SET:
        names = [n for n, val in ALL.items() if val == mersenne]
        print(f"  M_{i} = 2^{i}-1 = {mersenne} = {names}")

# 22. Regular polygon diagonals
print("\n--- 22. Polygon Diagonals ---")
for n in range(3, 50):
    diag = n * (n - 3) // 2
    if diag in SRG_SET and diag > 0:
        names = [nn for nn, val in ALL.items() if val == diag]
        print(f"  diag({n}-gon) = {diag} = {names}")

# 23. Compositions & ordered partitions
print("\n--- 23. Number of Compositions ---")
# Number of compositions of n into k parts = C(n-1, k-1)
for name_n, val_n in sorted(ALL.items(), key=lambda x: x[1]):
    if val_n < 3:
        continue
    for name_k, val_k in sorted(ALL.items(), key=lambda x: x[1]):
        if val_k < 2 or val_k >= val_n:
            continue
        comp = math.comb(val_n - 1, val_k - 1)
        if comp in SRG_SET and comp > 1:
            names2 = [n for n, v2 in ALL.items() if v2 == comp]
            print(f"  C({name_n}={val_n}, {name_k}={val_k} parts) = {comp} = {names2}")

# 24. Ackermann-like / Hyperoperations
print("\n--- 24. Tetration ---")
# a^^b (tetration)
for a in [2, 3]:
    for b in range(1, 6):
        result = a
        for _ in range(b - 1):
            result = a ** result
            if result > 1e10:
                result = -1
                break
        if result in SRG_SET:
            names = [n for n, val in ALL.items() if val == result]
            print(f"  {a}^^{b} = {result} = {names}")

# 25. Sum of totients
print("\n--- 25. Totient Summatory ---")
def euler_phi(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    tot_sum = sum(euler_phi(i) for i in range(1, val + 1))
    if tot_sum in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == tot_sum]
        print(f"  Φ({name}={val}) = Σφ(1..{val}) = {tot_sum} = {names2}")

# 26. Highly composite numbers
print("\n--- 26. Highly Composite ---")
hc = [1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360]
for i, h in enumerate(hc):
    if h in SRG_SET:
        names = [n for n, val in ALL.items() if val == h]
        print(f"  HC({i}) = {h} = {names}")

# 27. Abundant / deficient
print("\n--- 27. Abundancy ---")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    s = sigma(val, 1)
    abundance = s - 2 * val
    if abs(abundance) in SRG_SET and abs(abundance) > 0:
        names2 = [n for n, v2 in ALL.items() if v2 == abs(abundance)]
        print(f"  σ(1,{name}={val})-2·{val} = {abundance} → |{abundance}| = {names2}")

# 28. Superperfect
print("\n--- 28. Iterated Sigma ---")
for name, val in sorted(ALL.items(), key=lambda x: x[1]):
    if val < 2:
        continue
    s1 = sigma(val, 1)
    s2 = sigma(s1, 1) if s1 < 10000 else -1
    if s2 in SRG_SET:
        names2 = [n for n, v2 in ALL.items() if v2 == s2]
        print(f"  σ(σ({name}={val})) = σ({s1}) = {s2} = {names2}")

# 29. Ramsey numbers
print("\n--- 29. Ramsey Numbers ---")
ramsey = {(3,3): 6, (3,4): 9, (3,5): 14, (3,6): 18, (3,7): 23, (3,8): 28, (3,9): 36,
          (4,4): 18, (4,5): 25}
for (a, b), val_r in ramsey.items():
    if val_r in SRG_SET:
        names = [n for n, val in ALL.items() if val == val_r]
        print(f"  R({a},{b}) = {val_r} = {names}")

# 30. Exponent patterns
print("\n--- 30. Power Relations ---")
for base in range(2, 10):
    for exp in range(2, 10):
        val_p = base ** exp
        if val_p in SRG_SET:
            names = [n for n, val in ALL.items() if val == val_p]
            if base in SRG_SET:
                bname = [n for n, val in ALL.items() if val == base]
                print(f"  {bname}^{exp} = {val_p} = {names}")
            if exp in SRG_SET:
                ename = [n for n, val in ALL.items() if val == exp]
                print(f"  {base}^{ename} = {val_p} = {names}")

print("\n" + "="*70)
print("EXPLORATION A COMPLETE")
print("="*70)
