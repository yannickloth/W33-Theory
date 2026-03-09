"""Phase XXXI Exploration Script B — Algebraic & geometric structures"""
import math
from fractions import Fraction
from itertools import combinations

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

print("="*70)
print("PHASE XXXI EXPLORATION B")
print("="*70)

# 1. Chromatic polynomial of complete bipartite graphs
print("\n--- 1. Graph Coloring Numbers ---")
# χ(K_n, k) = k(k-1)^(n-1) for complete graph
for n_g in range(2, 8):
    for kk in range(2, 8):
        chi_val = kk * (kk - 1)**(n_g - 1)
        if chi_val in SRG_SET:
            names = [n for n, val in ALL.items() if val == chi_val]
            print(f"  χ(K_{n_g}, {kk}) = {chi_val} = {names}")

# 2. Graph complement chromatic
print("\n--- 2. Trees & Forests ---")
# Cayley's formula: number of labeled trees on n vertices = n^(n-2)
for n_t in range(2, 12):
    trees = n_t ** (n_t - 2)
    if trees in SRG_SET:
        names = [n for n, val in ALL.items() if val == trees]
        print(f"  T({n_t}) labeled trees = {n_t}^{n_t-2} = {trees} = {names}")

# 3. Platonic solid properties
print("\n--- 3. Platonic Solids ---")
platonic = {
    'tetra': {'V': 4, 'E': 6, 'F': 4, 'dual': 'tetra'},
    'cube': {'V': 8, 'E': 12, 'F': 6, 'dual': 'octa'},
    'octa': {'V': 6, 'E': 12, 'F': 8, 'dual': 'cube'},
    'dodeca': {'V': 20, 'E': 30, 'F': 12, 'dual': 'icosa'},
    'icosa': {'V': 12, 'E': 30, 'F': 20, 'dual': 'dodeca'},
}
for name_p, props in platonic.items():
    for prop, val_p in props.items():
        if isinstance(val_p, int) and val_p in SRG_SET:
            names = [n for n, val in ALL.items() if val == val_p]
            print(f"  {name_p}.{prop} = {val_p} = {names}")

# Sum of all Platonic V, E, F
total_v = sum(p['V'] for p in platonic.values())
total_e = sum(p['E'] for p in platonic.values())
total_f = sum(p['F'] for p in platonic.values())
print(f"  ΣV = {total_v}, ΣE = {total_e}, ΣF = {total_f}")
for total, label in [(total_v, 'ΣV'), (total_e, 'ΣE'), (total_f, 'ΣF')]:
    if total in SRG_SET:
        names = [n for n, val in ALL.items() if val == total]
        print(f"  {label} = {total} = {names}")

# 4. Regular polytope properties (4D)
print("\n--- 4. Regular 4-Polytopes ---")
polytopes_4d = {
    '5-cell': {'V': 5, 'E': 10, 'F': 10, 'C': 5},
    'tesseract': {'V': 16, 'E': 32, 'F': 24, 'C': 8},
    '16-cell': {'V': 8, 'E': 24, 'F': 32, 'C': 16},
    '24-cell': {'V': 24, 'E': 96, 'F': 96, 'C': 24},
    '120-cell': {'V': 600, 'E': 1200, 'F': 720, 'C': 120},
    '600-cell': {'V': 120, 'E': 720, 'F': 1200, 'C': 600},
}
for name_p, props in polytopes_4d.items():
    for prop, val_p in props.items():
        if val_p in SRG_SET:
            names = [n for n, val in ALL.items() if val == val_p]
            print(f"  {name_p}.{prop} = {val_p} = {names}")

# 5. Class numbers
print("\n--- 5. Class Numbers h(-d) ---")
# Class numbers of imaginary quadratic fields Q(sqrt(-d))
class_numbers = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 1, 8: 1, 
                 10: 2, 11: 1, 12: 2, 13: 2, 14: 4, 15: 2, 19: 1, 20: 2,
                 23: 3, 24: 2, 35: 2, 39: 4, 40: 2, 43: 1, 47: 5,
                 51: 2, 52: 2, 55: 4, 56: 4, 67: 1, 68: 4, 71: 7,
                 79: 5, 83: 3, 84: 4, 87: 6, 88: 2, 91: 2, 95: 8}
# Check d ∈ SRG_SET
for d, h in class_numbers.items():
    if d in SRG_SET and h in SRG_SET and h > 1:
        names_d = [n for n, val in ALL.items() if val == d]
        names_h = [n for n, val in ALL.items() if val == h]
        print(f"  h(-{d}) = {h}: d={names_d}, h={names_h}")
    elif d in SRG_SET:
        names_d = [n for n, val in ALL.items() if val == d]
        print(f"  h(-{d}) = {h}: d={names_d}")
    elif h in SRG_SET and h > 1:
        names_h = [n for n, val in ALL.items() if val == h]
        print(f"  h(-{d}) = {h} = {names_h}")

# 6. Cyclotomic polynomial evaluations
print("\n--- 6. Cyclotomic Φ_n(x) ---")
def cyclotomic_eval(n, x):
    """Evaluate cyclotomic polynomial Φ_n(x) using Mobius inversion"""
    result = 1
    for d in range(1, n + 1):
        if n % d == 0:
            # Mobius function of n/d
            nd = n // d
            mu_val = mobius(nd)
            if mu_val != 0:
                result *= (x**d - 1)**mu_val if mu_val > 0 else 1
                if mu_val < 0:
                    # Need division
                    pass
    # Simpler: use product formula
    # Φ_n(x) = Π_{d|n} (x^d - 1)^μ(n/d)
    from fractions import Fraction
    num = 1
    den = 1
    for d in range(1, n + 1):
        if n % d == 0:
            mu_val = mobius(n // d)
            if mu_val == 1:
                num *= (x**d - 1)
            elif mu_val == -1:
                den *= (x**d - 1)
    if den != 0:
        return num // den
    return None

def mobius(n):
    if n == 1:
        return 1
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

for n in range(1, 30):
    for x in range(2, 8):
        try:
            val_c = cyclotomic_eval(n, x)
            if val_c and val_c in SRG_SET:
                names = [nm for nm, val in ALL.items() if val == val_c]
                print(f"  Φ_{n}({x}) = {val_c} = {names}")
        except:
            pass

# 7. Sequences arising from q=3 specifically
print("\n--- 7. q=3 Specific Structures ---")
# GF(3^n) sizes
for n in range(1, 8):
    gf_size = 3**n
    if gf_size in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == gf_size]
        print(f"  |GF(3^{n})| = {gf_size} = {names}")
    # Number of irreducible polynomials over GF(3) of degree n
    # N(q,n) = (1/n) Σ_{d|n} μ(n/d) q^d
    irr = 0
    for d in range(1, n + 1):
        if n % d == 0:
            irr += mobius(n // d) * 3**d
    irr //= n
    if irr in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == irr]
        print(f"  #irr(GF(3), deg {n}) = {irr} = {names}")

# 8. Symmetry groups sizes
print("\n--- 8. Group Orders ---")
# S_n, A_n sizes
for n in range(1, 10):
    sn = math.factorial(n)
    an = sn // 2
    if sn in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == sn]
        print(f"  |S_{n}| = {sn} = {names}")
    if an in SRG_SET and n > 1:
        names = [nm for nm, val in ALL.items() if val == an]
        print(f"  |A_{n}| = {an} = {names}")

# Dihedral group D_n has order 2n
for n in range(2, 130):
    if 2*n in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == 2*n]
        if n in SRG_SET:
            nnames = [nm for nm, val in ALL.items() if val == n]
            print(f"  |D_{n}| = 2·{nnames} = {2*n} = {names}")

# 9. Lattice path counting
print("\n--- 9. Lattice Paths ---")
# Delannoy numbers D(m,n) = Σ C(m,k)·C(n,k)·2^k
def delannoy(m, n):
    return sum(math.comb(m, kk) * math.comb(n, kk) * (2**kk) for kk in range(min(m,n)+1))

for m in range(1, 10):
    for n in range(m, 10):
        d = delannoy(m, n)
        if d in SRG_SET:
            names = [nm for nm, val in ALL.items() if val == d]
            print(f"  Delannoy({m},{n}) = {d} = {names}")

# Narayana numbers
def narayana(n, kk):
    return math.comb(n, kk) * math.comb(n, kk-1) // n

for n in range(2, 12):
    for kk in range(1, n+1):
        try:
            nar = narayana(n, kk)
            if nar in SRG_SET:
                names = [nm for nm, val in ALL.items() if val == nar]
                print(f"  Narayana({n},{kk}) = {nar} = {names}")
        except:
            pass

# 10. Combinatorial identities
print("\n--- 10. Binomial Sum Identities ---")
# Σ C(n,k)^2 = C(2n,n)
for n in range(1, 15):
    central = math.comb(2*n, n)
    if central in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == central]
        print(f"  C(2·{n},{n}) = {central} = {names}")

# Vandermonde-type
# C(m+n, r) = Σ C(m,k)C(n,r-k)
# Specific: C(v+k, something)?
for a in range(1, 50):
    for b in range(1, min(a+1, 20)):
        cb = math.comb(a, b)
        if cb in SRG_SET and cb > 1:
            if a in SRG_SET and b in SRG_SET:
                names_a = [nm for nm, val in ALL.items() if val == a]
                names_b = [nm for nm, val in ALL.items() if val == b]
                names_cb = [nm for nm, val in ALL.items() if val == cb]
                print(f"  C({names_a},{names_b}) = {cb} = {names_cb}")

# 11. Fibonacci / Lucas modular
print("\n--- 11. Fibonacci Modular Arithmetic ---")
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# F(n) mod SRG values
for name_m, val_m in sorted(ALL.items(), key=lambda x: x[1]):
    if val_m < 3:
        continue
    for n in range(1, 30):
        fm = fib(n) % val_m
        if fm in SRG_SET and fm > 1 and fm < val_m:
            pass  # Too many

# Pisano periods already checked. What about Lucas mod?
def lucas(n):
    if n == 0: return 2
    if n == 1: return 1
    a, b = 2, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# Fibonacci at SRG values
print("  Fibonacci at SRG values:")
for name, val_n in sorted(ALL.items(), key=lambda x: x[1]):
    if val_n < 1 or val_n > 30:
        continue
    f_val = fib(val_n)
    if f_val in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == f_val]
        print(f"    F({name}={val_n}) = {f_val} = {names}")

# 12. Euclidean algorithm steps
print("\n--- 12. GCD Chain Lengths ---")
def gcd_steps(a, b):
    """Number of steps in Euclidean algorithm"""
    steps = 0
    while b > 0:
        a, b = b, a % b
        steps += 1
    return steps

for name_a, val_a in sorted(ALL.items(), key=lambda x: x[1]):
    if val_a < 2:
        continue
    for name_b, val_b in sorted(ALL.items(), key=lambda x: x[1]):
        if val_b < 2 or val_b >= val_a:
            continue
        steps = gcd_steps(val_a, val_b)
        if steps in SRG_SET and steps > 1:
            names = [nm for nm, val in ALL.items() if val == steps]
            print(f"  gcd_steps({name_a}={val_a}, {name_b}={val_b}) = {steps} = {names}")

# 13. Jacobi symbol patterns
print("\n--- 13. Jacobi Symbols ---")
def jacobi(a, n):
    """Compute Jacobi symbol (a/n)"""
    if n <= 0 or n % 2 == 0:
        return None
    a = a % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in [3, 5]:
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a = a % n
    if n == 1:
        return result
    return 0

# Count Jacobi = +1 vs -1 for SRG moduli
for name_n, val_n in [('N', 5), ('phi6', 7), ('phi3', 13), ('albert', 27), ('v', 40)]:
    if val_n % 2 == 0:
        continue
    plus_count = sum(1 for a in range(1, val_n) if jacobi(a, val_n) == 1)
    minus_count = sum(1 for a in range(1, val_n) if jacobi(a, val_n) == -1)
    if plus_count in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == plus_count]
        print(f"  #{'{'}(a/{val_n})=+1{'}'} = {plus_count} = {names}")
    if minus_count in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == minus_count]
        print(f"  #{'{'}(a/{val_n})=-1{'}'} = {minus_count} = {names}")

# 14. Multinomial coefficients
print("\n--- 14. Multinomial Coefficients ---")
# n! / (k1! k2! ... km!)
for total in range(3, 15):
    # Partitions of total into SRG-value parts
    for p1 in range(1, total):
        for p2 in range(p1, total - p1 + 1):
            p3 = total - p1 - p2
            if p3 >= p2:
                mn = math.factorial(total) // (math.factorial(p1) * math.factorial(p2) * math.factorial(p3))
                if mn in SRG_SET and mn > 1:
                    if total in SRG_SET:
                        total_n = [nm for nm, val in ALL.items() if val == total]
                        names = [nm for nm, val in ALL.items() if val == mn]
                        print(f"  ({total_n}; {p1},{p2},{p3}) = {mn} = {names}")

# 15. Permanent of small matrices
print("\n--- 15. Small Matrix Permanents ---")
# Permanent of J_n (all-ones matrix) = n!
# Permanent of I_n + J_n
# Derangements: D(n) = n! * Σ (-1)^k/k!
derangements = [1, 0, 1, 2, 9, 44, 265, 1854]
for i, d in enumerate(derangements):
    if d in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == d]
        print(f"  D({i}) derangements = {d} = {names}")
    # Subfactorials
# Subfactorial !n = D(n) already

# 16. Partition function p(n) deeper
print("\n--- 16. Partition Pairs ---")
# Already T411 covers p(2)=2, p(3)=3, p(4)=5, p(7)=15
# Check deeper: p(n) for larger n → SRG
partitions = [1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77, 101, 135, 176, 231]
for i, p_val in enumerate(partitions):
    if p_val in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == p_val]
        print(f"  p({i}) = {p_val} = {names}")
# Products/ratios of partition values
for i in range(len(partitions)):
    for j in range(i+1, len(partitions)):
        if partitions[j] > 0 and partitions[i] > 0:
            prod = partitions[i] * partitions[j]
            if prod in SRG_SET:
                names = [nm for nm, val in ALL.items() if val == prod]
                print(f"  p({i})·p({j}) = {partitions[i]}·{partitions[j]} = {prod} = {names}")

# 17. Smith totient 
print("\n--- 17. Iterated Totient ---")
for name, val_n in sorted(ALL.items(), key=lambda x: x[1]):
    if val_n < 3:
        continue
    chain = [val_n]
    curr = val_n
    while curr > 1:
        curr = euler_phi(curr)
        chain.append(curr)
    chain_len = len(chain)
    if chain_len in SRG_SET and chain_len > 1:
        names = [nm for nm, val in ALL.items() if val == chain_len]
        print(f"  φ-chain({name}={val_n}) length = {chain_len} = {names}")
    # Also check intermediate values
    for step, c in enumerate(chain):
        if step > 0 and c in SRG_SET and c != val_n:
            names = [nm for nm, val in ALL.items() if val == c]
            # Only print if step is interesting
            if step in SRG_SET:
                snames = [nm for nm, val in ALL.items() if val == step]
                print(f"  φ^{step}({name}={val_n}) = {c} = {names} (step={snames})")

# 18. Maximal independent set / clique counts  
print("\n--- 18. Vertex/Edge Covers ---")
# For SRG(v,k,λ,μ): independence number α = v - k = 28? No, α of SRG(40,12,2,4)
# Actually Hoffman bound: α ≤ v·(-s)/(k-s) = 40·4/(12+4) = 160/16 = 10
# So α ≤ 10 = θ
# Clique number ω ≤ v·r/(k+r-... hmm let me think
# ω ≤ 1 - k/s = 1 - 12/(-4) = 1+3 = 4 = μ
print(f"  α ≤ θ = {theta} (Hoffman bound)")
print(f"  ω ≤ μ = {mu} (Lovász bound)")
print(f"  α + ω ≤ {theta + mu}")
if theta + mu in SRG_SET:
    names = [nm for nm, val in ALL.items() if val == theta + mu]
    print(f"  α + ω bound = {theta + mu} = {names}")
# α·ω ≤ 40
print(f"  α·ω bound = {theta * mu} = {theta}·{mu}")
if theta * mu in SRG_SET:
    names = [nm for nm, val in ALL.items() if val == theta * mu]
    print(f"  α·ω = {theta * mu} = {names}")

# 19. Chebyshev function values
print("\n--- 19. Chebyshev θ(n) ---")
# θ(n) = Σ_{p≤n} ln(p)  (Chebyshev's theta)
# ψ(n) = Σ_{p^k≤n} ln(p)
# Integer version: primorial
# θ(n) counts Σ ln(p) for p ≤ n
# Use exp(θ(n)) = primorial(n)
primes_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
for n_p in range(2, 50):
    prod = 1
    for p in primes_list:
        if p > n_p:
            break
        prod *= p
    if prod in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == prod]
        print(f"  exp(θ({n_p})) = ∏p≤{n_p} = {prod} = {names}")

# 20. Bernstein basis values
print("\n--- 20. Ballot Numbers ---")
# Ballot number: B(n,k) = (n-k)/(n+k) · C(n+k, k) for n > k
for n in range(2, 15):
    for kk in range(1, n):
        if (n + kk) > 0:
            ballot = (n - kk) * math.comb(n + kk, kk) // (n + kk)
            if ballot in SRG_SET and ballot > 1:
                names = [nm for nm, val in ALL.items() if val == ballot]
                print(f"  Ballot({n},{kk}) = {ballot} = {names}")

# 21. Tribonacci-like with different seeds
print("\n--- 21. Generalized Recurrences ---")
# Narayana's cows: a(n) = a(n-1) + a(n-3), a(1)=a(2)=a(3)=1
nara = [1, 1, 1]
for i in range(3, 25):
    nara.append(nara[-1] + nara[-3])
for i, val_n in enumerate(nara):
    if val_n in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == val_n]
        print(f"  NarayanaCow({i+1}) = {val_n} = {names}")

# Hofstadter Q sequence: Q(n) = Q(n - Q(n-1)) + Q(n - Q(n-2))
# Actually Q(n) = Q(n - Q(n-1)), Q(1) = Q(2) = 1
hof = [0, 1, 1]
for i in range(3, 30):
    hof.append(hof[i - hof[i-1]])
for i in range(1, len(hof)):
    if hof[i] in SRG_SET and hof[i] > 1:
        names = [nm for nm, val in ALL.items() if val == hof[i]]
        # Only if index is also SRG
        if i in SRG_SET:
            inames = [nm for nm, val in ALL.items() if val == i]
            print(f"  Hofstadter Q({i}={inames}) = {hof[i]} = {names}")

# 22. Repunits
print("\n--- 22. Repunits ---")
for base in [2, 3, 10]:
    for n in range(1, 15):
        rep = (base**n - 1) // (base - 1)
        if rep in SRG_SET:
            names = [nm for nm, val in ALL.items() if val == rep]
            print(f"  R_{n}(base {base}) = {rep} = {names}")

# 23. Stern's diatomic sequence
print("\n--- 23. Stern's Diatomic ---")
stern = [0, 1]
for i in range(2, 50):
    if i % 2 == 0:
        stern.append(stern[i // 2])
    else:
        stern.append(stern[(i-1)//2] + stern[(i+1)//2])

for i in range(1, len(stern)):
    if stern[i] in SRG_SET and stern[i] > 1:
        names = [nm for nm, val in ALL.items() if val == stern[i]]
        if i in SRG_SET:
            inames = [nm for nm, val in ALL.items() if val == i]
            print(f"  st({i}={inames}) = {stern[i]} = {names}")

# 24. Double factorial
print("\n--- 24. Double Factorial ---")
def double_factorial(n):
    if n <= 0: return 1
    result = 1
    while n > 0:
        result *= n
        n -= 2
    return result

for n in range(1, 20):
    df = double_factorial(n)
    if df in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == df]
        print(f"  {n}!! = {df} = {names}")

# 25. Euler's totient sums and products
print("\n--- 25. Totient Algebra ---")
# φ(a·b) relationships
for name_a, val_a in sorted(ALL.items(), key=lambda x: x[1]):
    if val_a < 2:
        continue
    for name_b, val_b in sorted(ALL.items(), key=lambda x: x[1]):
        if val_b < 2 or val_b > val_a:
            continue
        if val_a * val_b <= 500:
            phi_prod = euler_phi(val_a * val_b)
            if phi_prod in SRG_SET:
                names = [nm for nm, val in ALL.items() if val == phi_prod]
                print(f"  φ({name_a}·{name_b}={val_a*val_b}) = {phi_prod} = {names}")

# 26. Farey sequence lengths
print("\n--- 26. Farey Sequence ---")
# |F_n| = 1 + Σ_{k=1}^{n} φ(k) = 1 + Φ(n) where Φ is totient summatory
for n in range(1, 50):
    farey_len = 1 + sum(euler_phi(kk) for kk in range(1, n+1))
    if farey_len in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == farey_len]
        print(f"  |F_{n}| = {farey_len} = {names}")

# 27. Zeta function at negative integers
print("\n--- 27. Zeta-related ---")
# ζ(-2n) = 0 for n ≥ 1
# ζ(-1) = -1/12 → denominator = 12 = k!
# ζ(-3) = 1/120 → denominator = 120 = E/2!
# Riemann zeta at negative odd integers: ζ(1-2n) = -B_{2n}/(2n)
print(f"  ζ(-1) = -1/12: denominator = 12 = k")
print(f"  ζ(-3) = 1/120: denominator = 120 = E/2")
# Apéry's constant ζ(3) ≈ 1.202...
# ζ(2) = π²/6 → 6 = δ
print(f"  ζ(2) = π²/6: denominator = 6 = δ")
# ζ(4) = π⁴/90
# ζ(6) = π⁶/945

# 28. Egyptian fraction representations
print("\n--- 28. Unit Fraction Representations ---")
# 1/a + 1/b = 1/n has d(n²) solutions
# For n ∈ SRG, count solutions
for name, val_n in sorted(ALL.items(), key=lambda x: x[1]):
    if val_n < 2 or val_n > 30:
        continue
    count = 0
    n2 = val_n * val_n
    for d in range(1, int(math.sqrt(n2)) + 1):
        if n2 % d == 0:
            count += 1
    count = 2 * count  # Include d and n2/d
    # Actually: number of ways 1/a + 1/b = 1/n with a ≤ b
    # equals number of divisors d of n² with n < d ≤ n² (then b = n+n²/d, a = ...)
    # Simpler: just count divisors of n²
    n_sq_divs = sum(1 for d in range(1, n2+1) if n2 % d == 0)
    half = (n_sq_divs + 1) // 2  # solutions with a ≤ b
    if half in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == half]
        print(f"  #(1/a+1/b=1/{name}={val_n}) = {half} = {names}")
    if n_sq_divs in SRG_SET:
        names = [nm for nm, val in ALL.items() if val == n_sq_divs]
        print(f"  d({val_n}²) = d({n2}) = {n_sq_divs} = {names}")

# 29. Nim-values / Sprague-Grundy
print("\n--- 29. Game Theory ---")
# Grundy values for Nim heaps
# For single-pile Nim: G(n) = n
# For Wythoff's game: positions (a,b) with G=0 are golden ratio related
# Already covered by golden ratio in T417

# Nimber multiplication
# a ⊗ b in GF(2^n)
# For Nim-values up to 15 (included in Nimber field)
# 2 ⊗ 3 = ? In GF(2^2): 2⊗3 = 1... let's compute

print("\n--- 30. Musical / Physical Constants ---")
# Just ratios: 3/2 (fifth), 4/3 (fourth), 5/4 (major third)
# These are SRG ratios!
print(f"  Perfect fifth = q/lam = {q}/{lam} = {q/lam}")
print(f"  Perfect fourth = mu/q = {mu}/{q} = {mu/q:.4f}")
print(f"  Major third = N/mu = {N}/{mu} = {N/mu}")

# Additional: 12-TET semitones per octave = k = 12
print(f"  12-TET semitones = k = {k}")
# Circle of fifths: 12 keys = k
# 7 naturals per octave
print(f"  Naturals per octave = phi6 = {phi6}")
# 5 sharps/flats
print(f"  Sharps/flats = N = {N}")

print("\n" + "="*70)
print("EXPLORATION B COMPLETE")
print("="*70)
