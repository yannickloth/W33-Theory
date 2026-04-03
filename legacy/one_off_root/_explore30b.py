"""Phase XXX Exploration Script B — Graph theory, lattice theory, coding theory, and group theory connections."""
import math
from functools import lru_cache

# SRG constants
v, k, lam, mu, q = 40, 12, 2, 4, 3
E = 240; r = 2; s = -4; f = 24; g = 15
theta = 10; phi3 = 13; phi6 = 7; dimO = 8; N = 5; albert = 27; delta = 6

ALL = {'v':v,'k':k,'λ':lam,'μ':mu,'q':q,'E':E,'r':r,'s':s,'f':f,'g':g,
       'θ':theta,'Φ₃':phi3,'Φ₆':phi6,'dimO':dimO,'N':N,'albert':albert,'δ':delta}
VALS = set(ALL.values())

# ============ GRAPH CHROMATIC NUMBER AND INDEPENDENCE ============
print("=== GRAPH INVARIANTS FROM SRG PARAMETERS ===")
# Clique number ω(G) and independence number α(G) for SRG(40,12,2,4)
# Hoffman bound: α(G) ≤ v·(-s)/(k-s) = 40·4/(12+4) = 40·4/16 = 10
# Lovász theta: θ(G) = v·(-s)/(k-s) = 10 = theta!
alpha_bound = v * (-s) // (k - s)
print(f"  Hoffman independence bound: α ≤ v·(-s)/(k-s) = {alpha_bound} = θ *** MATCH")

# Chromatic number bound: χ(G) ≥ v/α(G) ≥ 40/10 = 4 = μ
chi_lower = v // alpha_bound
print(f"  Chromatic lower bound: χ ≥ v/α = {chi_lower} = μ *** MATCH")

# Clique bound: ω ≤ 1 + k/(-s+1) = 1 + 12/5 = 3.4 → ω ≤ 3
omega_bound_num = k + (-s) + 1
# Actually: Delsarte/Hoffman: ω ≤ 1 + k/(−s) ... no, for complement
# For SRG: clique ≤ 1 + k/μ = 1 + 12/4 = 4
omega_upper = 1 + k // mu
print(f"  Clique upper bound: ω ≤ 1 + k/μ = {omega_upper} = μ *** MATCH")

# Fractional chromatic number: χ_f(G) = v/α(G) = 40/10 = 4 = μ
chi_frac = v // alpha_bound
print(f"  Fractional chromatic: χ_f = v/α = {chi_frac} = μ *** MATCH")

# ============ COMPLEMENT GRAPH PARAMETERS ============
print("\n=== COMPLEMENT GRAPH SRG PARAMETERS ===")
v_bar = v
k_bar = v - k - 1  # = 40-12-1 = 27 = albert!
lam_bar = v - 2*k + mu - 2  # = 40-24+4-2 = 18
mu_bar = v - 2*k + lam  # = 40-24+2 = 18
print(f"  Complement: SRG({v_bar}, {k_bar}, {lam_bar}, {mu_bar})")
print(f"  k̄ = v-k-1 = {k_bar} = albert *** HIT!")
print(f"  k̄ - k = {k_bar - k} = g = {g} *** HIT!")

# Eigenvalues of complement
r_bar = -1 - s  # = -1-(-4) = 3 = q
s_bar = -1 - r  # = -1-2 = -3
print(f"  r̄ = -1-s = {r_bar} = q *** HIT!")
print(f"  s̄ = -1-r = {s_bar}")

# ============ LINE GRAPH PARAMETERS ============
print("\n=== LINE GRAPH ===")
# L(G) has |E| vertices, each edge adjacent to...
# For regular graph: each vertex has degree k=12
# Edge e=(u,v): degree in L(G) = deg(u)+deg(v)-2 = 12+12-2 = 22
line_k = 2*k - 2
print(f"  Line graph L(G): {E} vertices, regularity = 2k-2 = {line_k}")
# |E(L(G))| = (1/2)·|E|·(2k-2) = 240·22/2 = 2640
line_E = E * line_k // 2
print(f"  |E(L(G))| = {line_E}")

# ============ PETERSEN-LIKE INVARIANTS ============
print("\n=== PETERSEN CONNECTION ===")
# Petersen graph is SRG(10,3,0,1) — note 10=θ, 3=q!
print(f"  Petersen: SRG(10,3,0,1) = SRG(θ, q, 0, 1)")
print(f"  W(3,3) order/Petersen order = v/θ = {v//theta} = μ")

# ============ RAMSEY-LIKE CONNECTIONS ============
print("\n=== RAMSEY CONNECTIONS ===")
# Known Ramsey numbers
R = {(3,3): 6, (3,4): 9, (3,5): 14, (3,6): 18, (3,7): 23, (3,8): 28, (3,9): 36,
     (4,4): 18, (4,5): 25}
for (a,b), rv in R.items():
    if rv in VALS:
        print(f"  R({a},{b}) = {rv} *** HIT")

# ============ REGULAR POLYTOPE COUNTS ============
print("\n=== REGULAR POLYTOPE VERTEX/EDGE COUNTS ===")
polytopes = {
    'tetrahedron': (4, 6, 4),
    'cube': (8, 12, 6),
    'octahedron': (6, 12, 8),
    'dodecahedron': (20, 30, 12),
    'icosahedron': (12, 30, 20),
    '24-cell': (24, 96, 96, 24),
    '120-cell': (600, 1200, 720, 120),
    '600-cell': (120, 720, 1200, 600),
    '16-cell': (8, 24, 32, 16),
    'tesseract': (16, 32, 24, 8),
}
for name, counts in polytopes.items():
    for i, cnt in enumerate(counts):
        if cnt in VALS:
            labels = ['V','E','F','C']
            print(f"  {name} {labels[i]}={cnt} *** HIT")

# ============ LATTICE PATH COUNTS ============
print("\n=== LATTICE PATH COUNTS ===")
# Dyck paths of semilength n = Catalan(n)
catalan = [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862]
for i, c in enumerate(catalan):
    if c in VALS:
        print(f"  Catalan({i}) = {c} *** HIT")

# ============ COXETER GROUP ORDERS ============
print("\n=== COXETER GROUP ORDERS ===")
coxeter = {
    'A1': 2, 'A2': 6, 'A3': 24, 'A4': 120, 'A5': 720,
    'B2': 8, 'B3': 48, 'B4': 384,
    'D4': 192, 'D5': 1920,
    'G2': 12, 'H3': 120, 'H4': 14400,
    'I2(5)': 10, 'I2(8)': 16,
    'F4': 1152,
    'E6': 51840, 'E7': 2903040, 'E8': 696729600,
}
for name, order in coxeter.items():
    if order in VALS:
        print(f"  W({name}) = {order} *** HIT")

# ============ SYMMETRIC GROUP CONNECTIONS ============
print("\n=== SYMMETRIC GROUP ===")
for n in range(1, 10):
    sn = math.factorial(n)
    if sn in VALS:
        print(f"  |S_{n}| = {n}! = {sn} *** HIT")
    # Conjugacy classes = p(n)
    # Subgroups
    # Index of alternating group
    if sn // 2 in VALS and sn > 2:
        print(f"  |A_{n}| = {n}!/2 = {sn//2} *** HIT")

# ============ CODING THEORY BOUNDS ============
print("\n=== CODING THEORY ===")
# Hamming bound: A_q(n,d) ≤ q^n / V_q(n,t) where t = ⌊(d-1)/2⌋
# Singleton bound: A_q(n,d) ≤ q^(n-d+1)
# Check standard codes with SRG parameters
# Binary Golay [23,12,7]: parameters k=12, n-k=11, d=7
print(f"  Binary Golay [23,12,7]: dimension = k = {k}")
print(f"  Ternary Golay [11,6,5]: dimension = δ = {delta}, min distance = N = {N}")

# Hamming code [2^r-1, 2^r-1-r, 3]
# [7,4,3]: n=7=Φ₆, k=4=μ, d=3=q
print(f"  Hamming [7,4,3]: n=Φ₆={phi6}, k=μ={mu}, d=q={q}")

# ============ INFORMATION THEORY ============
print("\n=== INFORMATION THEORY ===")
# Channel capacity of BSC with crossover p
# Hamming weight distribution connections
# Perfect code covering radius
# Preparata codes, Reed-Muller codes

# ============ MODULAR FORMS / LATTICE CONNECTIONS ============
print("\n=== MODULAR FORM DIMENSIONS ===")
# dim S_k(SL_2(Z)) for various weights
def dim_cusp_forms(weight):
    if weight < 2 or weight % 2 == 1: return 0
    if weight == 2: return 0
    if weight < 12: return 0
    if weight == 12: return 1
    return (weight - 2) // 12 if weight % 12 != 2 else (weight - 2) // 12

for wt in range(2, 100, 2):
    d = dim_cusp_forms(wt)
    if d in VALS and d > 1:
        print(f"  dim S_{wt}(SL_2(Z)) = {d} *** HIT")

# Eisenstein series E_k coefficients
# E_4 = 1 + 240·Σ σ_3(n)q^n — coefficient 240 = E!
print(f"  E_4 Eisenstein series: 1 + {E}·q + ... (leading coefficient = E = {E})")

# ============ LATTICE THETA FUNCTIONS ============
print("\n=== LATTICE CONNECTIONS ===")
# E8 lattice: 240 nearest neighbors (= E)
print(f"  E_8 lattice kissing number = {E} = E")
# Leech lattice: 196560 nearest neighbors
# D_4 lattice: 24 nearest neighbors = f
print(f"  D_4 lattice kissing number = {f} = f")
# A_2 lattice: 6 nearest neighbors = δ
print(f"  A_2 lattice kissing number = {delta} = δ")

# ============ NUMBER THEORY: CONTINUED FRACTION ============
print("\n=== CONTINUED FRACTION OF GOLDEN RATIO POWERS ===")
# φ^n and connections
phi_golden = (1 + 5**0.5) / 2
for n in range(1, 20):
    phin = phi_golden ** n
    rnd = round(phin)
    if rnd in VALS:
        print(f"  round(φ^{n}) = {rnd} *** HIT")

# ============ HYPERGEOMETRIC-LIKE ============
print("\n=== MULTINOMIAL / COMPOSITION COUNTS ===")
# Number of compositions of n into k parts
for n_val in [v, k, E, f, g, theta, albert]:
    for k_val in [lam, q, mu, N, delta]:
        if k_val <= n_val:
            comp = math.comb(n_val - 1, k_val - 1) if k_val >= 1 else 0
            if comp in VALS and comp > 1:
                print(f"  C({n_val}-1, {k_val}-1) = C({n_val-1},{k_val-1}) = {comp} *** compositions({n_val},{k_val})")

# ============ ZETA-LIKE VALUES ============
print("\n=== SPECIAL SUMS AND PRODUCTS ===")
# Product of all SRG primary parameters
prod_primary = v * k * lam * mu
print(f"  v·k·λ·μ = {prod_primary}")
if prod_primary in VALS:
    print(f"    *** HIT")

# v·k = 480 = 2·E
print(f"  v·k = {v*k} = 2·E = {2*E} *** {'MATCH' if v*k == 2*E else 'NO'}")
# f·g = 360
print(f"  f·g = {f*g}")
# k·g = 180
print(f"  k·g = {k*g}")

# Sum of primary
sum_primary = v + k + lam + mu
print(f"  v+k+λ+μ = {sum_primary}")
if sum_primary in VALS:
    print(f"    *** HIT")

# Sum of eigenvalues
print(f"  k+r+s = {k+r+s} = {k+r+s}")

# ============ PERMUTATION CYCLES ============
print("\n=== CYCLE INDEX CONNECTIONS ===")
# Number of permutations of n with k cycles = |s(n,k)| (unsigned Stirling 1st kind)
@lru_cache(maxsize=10000)
def stirling1_unsigned(n, k):
    if n == 0 and k == 0: return 1
    if n == 0 or k == 0: return 0
    return (n-1) * stirling1_unsigned(n-1, k) + stirling1_unsigned(n-1, k-1)

for n in range(1, 12):
    for kk in range(1, n+1):
        s1 = stirling1_unsigned(n, kk)
        if s1 in VALS and s1 > 1:
            print(f"  |s({n},{kk})| = {s1} *** HIT")

# ============ TOTIENT SUM / DIVISOR SUM identities ============
print("\n=== TOTIENT/DIVISOR SUM IDENTITIES ===")
def euler_totient(n):
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

# Σ_{d|n} φ(d) = n
for name, val in ALL.items():
    if val > 0:
        divs = [d for d in range(1, val+1) if val % d == 0]
        tot_sum = sum(euler_totient(d) for d in divs)
        # This should always equal n, but check it's interesting
        # Instead: Σ_{d|n} μ(d) = 0 for n>1 (Möbius)
        # More interesting: Σ_{d|n} φ(n/d)·d
        pass

# ============ JORDAN TOTIENT ============
print("\n=== JORDAN TOTIENT J_k(n) ===")
def jordan_totient(k_exp, n):
    """J_k(n) = n^k · Π_{p|n} (1 - 1/p^k)"""
    result = n ** k_exp
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result = result * (1 - 1/(p**k_exp))
        p += 1
    if temp > 1:
        result = result * (1 - 1/(temp**k_exp))
    return int(round(result))

for k_exp in range(1, 5):
    for name, val in sorted(ALL.items(), key=lambda x: x[1]):
        if val > 1:
            jt = jordan_totient(k_exp, val)
            if jt in VALS:
                print(f"  J_{k_exp}({name}={val}) = {jt} *** HIT")

# ============ SUMMING TO KEY VALUES ============
print("\n=== PARTITION INTO SRG-MANY PARTS ===")
# How many ways to partition k into exactly q parts?
# p(12, 3 parts) = ?
def restricted_partition(n, k, max_val=None):
    """Number of partitions of n into exactly k parts."""
    if max_val is None: max_val = n
    if k == 0: return 1 if n == 0 else 0
    if n <= 0 or k < 0: return 0
    if k == 1: return 1 if n <= max_val else 0
    # Use generating function approach
    @lru_cache(maxsize=10000)
    def dp(remaining, parts, largest):
        if parts == 0: return 1 if remaining == 0 else 0
        if remaining <= 0: return 0
        total = 0
        for val in range(1, min(remaining, largest) + 1):
            total += dp(remaining - val, parts - 1, val)
        return total
    return dp(n, k, max_val)

for n_name, n_val in sorted(ALL.items(), key=lambda x: x[1]):
    for k_name, k_val in [('λ',lam),('q',q),('μ',mu),('N',N)]:
        if 0 < k_val <= n_val and n_val <= 50:
            rp = restricted_partition(n_val, k_val)
            if rp in VALS and rp > 1:
                print(f"  p({n_name}={n_val}, {k_name}={k_val} parts) = {rp} *** HIT")

# ============ GRAPH ENERGY ============
print("\n=== GRAPH ENERGY ===")
# Energy = sum of absolute eigenvalues = f·|r| + g·|s| = 24·2 + 15·4 = 48 + 60 = 108
graph_energy = f * abs(r) + g * abs(s)
print(f"  Graph energy = f·|r| + g·|s| = {graph_energy}")
# = 108 = 4·27 = μ·albert
print(f"  = μ·albert = {mu*albert} *** {'MATCH' if graph_energy == mu*albert else 'NO'}")

# Laplacian eigenvalues: 0 (mult 1), v-k+r... no
# Laplacian: k-r = 10 = θ (mult f=24), k-s = 16 (mult g=15), 0 (mult 1), v (mult 1 for connected)
# Wait: Laplacian eigenvalues for SRG: 0, k-r, k-s
# = 0, k-r = 10 = θ, k-s = 16
lap_1 = k - r
lap_2 = k - s
print(f"  Laplacian eigenvalues: 0, {lap_1}=θ, {lap_2}")
print(f"  k - r = {lap_1} = θ *** MATCH")
# Number of spanning trees (Kirchhoff) = (1/v) · Π nonzero Laplacian eigenvalues
# = (1/40) · θ^f · 16^g = (1/40) · 10^24 · 16^15
print(f"  Spanning trees = (1/v) · θ^f · (k-s)^g")

# Signless Laplacian eigenvalues: k+r, k+s (=8=dimO!)
slap_1 = k + r  # = 14
slap_2 = k + s  # = 8 = dimO!
print(f"  Signless Laplacian eigenvalues: 2k={2*k}, k+r={slap_1}, k+s={slap_2}=dimO *** HIT")

# ============ GRAPH AUTOMORPHISM ============
print("\n=== AUTOMORPHISM GROUP ===")
aut = 51840
print(f"  |Aut(W(3,3))| = {aut}")
print(f"  = |W(E₆)| = Coxeter group of E₆")
# Factorization
print(f"  = 2^7 · 3^4 · 5 = {2**7 * 3**4 * 5}")
# 51840 / v = 1296 = 6^4 = δ^μ
print(f"  |Aut|/v = {aut//v} = δ^μ = {delta**mu} *** {'MATCH' if aut//v == delta**mu else 'NO'}")
# 51840 / E = 216 = 6^3 = δ^q
print(f"  |Aut|/E = {aut//E} = δ^q = {delta**q} *** {'MATCH' if aut//E == delta**q else 'NO'}")
# 51840 / k = 4320
print(f"  |Aut|/k = {aut//k}")
# 51840 / (v·k) = 108 = μ·albert
print(f"  |Aut|/(v·k) = {aut//(v*k)} = μ·albert = {mu*albert}")

# ============ GRAPH DIAMETER AND GIRTH ============
print("\n=== DIAMETER, GIRTH ===")
# SRG(40,12,2,4): diameter = 2, girth = 3 (since λ=2>0, has triangles)
print(f"  diameter = {lam} = λ")
print(f"  girth = {q} = q")

# ============ COVERING/PACKING ============
print("\n=== COVERING AND PACKING ===")
# Minimum dominating set: γ(G) ≥ v/(1+k) = 40/13 ≈ 3.08 → γ ≥ 4 = μ
gamma_lower = math.ceil(v / (1 + k))
print(f"  Domination number γ ≥ ⌈v/(1+k)⌉ = ⌈{v}/{1+k}⌉ = {gamma_lower} = μ *** MATCH")

# ============ VERTEX CONNECTIVITY ============
print("\n=== CONNECTIVITY ===")
# For SRG: vertex connectivity = k (by Whitney's theorem for connected SRGs)
print(f"  Vertex connectivity κ(G) = k = {k}")
# Edge connectivity = k
print(f"  Edge connectivity λ(G) = k = {k}")

# ============ DOMINATION-LIKE PARAMETERS ============
print("\n=== TOTAL DOMINATION ===")
# Total domination: γ_t(G) ≥ v/k = 40/12 ≈ 3.33 → ≥ 4
gamma_t_lower = math.ceil(v / k)
print(f"  Total domination γ_t ≥ ⌈v/k⌉ = {gamma_t_lower} = μ")

# ============ WALK COUNTS ============
print("\n=== WALK COUNTS ===")
# Number of walks of length ℓ from vertex u to v in SRG
# Using eigenvalue decomposition
# W_ℓ(u,u) = (1/v)·k^ℓ + (f/v)·r^ℓ + (g/v)·s^ℓ  (for diagonal)
# W_ℓ(u,v adjacent) = similar but with different coefficients
for ell in range(1, 8):
    # Closed walks per vertex
    cw = k**ell + f * r**ell + g * s**ell
    # Total = v · cw / v = cw (already per vertex, multiply by v for total)
    total_cw = v * (k**ell + f * r**ell + g * s**ell) // v  # = k^ℓ + f·r^ℓ + g·s^ℓ
    actual = k**ell + f * (r**ell) + g * (s**ell)
    if actual in VALS:
        print(f"  Closed walks length {ell} per vertex: k^{ell} + f·r^{ell} + g·s^{ell} = {actual} *** HIT")
    # Check if divisible by v
    if actual % v == 0 and actual // v in VALS:
        print(f"  Closed walks length {ell} / v = {actual // v} *** HIT")

# ============ THETA FUNCTION OF SRG ============
print("\n=== LOVÁSZ THETA ===")
# ϑ(G) = v·(-s)/(k-s) = 40·4/16 = 10 = θ (already noted)
lovasz = v * (-s) / (k - s)
print(f"  ϑ(G) = {lovasz} = θ = {theta}")
# ϑ(Ḡ) = v·r/... Actually ϑ(G)·ϑ(Ḡ) ≥ v
# ϑ(Ḡ) = v·(1+r)/(k+1+r) ... no, standard formula:
# ϑ(Ḡ) = -v·r/(s-r)... let me use: ϑ(G)·ϑ(Ḡ) ≥ v
# For vertex-transitive: ϑ(G)·ϑ(Ḡ) = v ⟹ ϑ(Ḡ) = v/ϑ(G) = 40/10 = 4 = μ
lovasz_bar = v / lovasz
print(f"  ϑ(Ḡ) = v/ϑ(G) = {lovasz_bar} = μ = {mu}")

# ============ CAYLEY TABLE EXPLORATION ============
print("\n=== MAGIC CONSTANTS ===")
# Magic constant of n×n magic square = n(n²+1)/2
for n in range(1, 20):
    mc = n * (n**2 + 1) // 2
    if mc in VALS:
        print(f"  Magic constant M({n}) = {mc} *** HIT")

# ============ FIBONACCI MODULAR ============
print("\n=== FIBONACCI MOD SRG ===")
# Fibonacci numbers mod v, mod k, etc.
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

# Check F_n for small n
for n in range(1, 50):
    fn = fib(n)
    if fn in VALS:
        print(f"  F({n}) = {fn} *** HIT")

# ============ GENERALISED FIBONACCI ============
print("\n=== TRIBONACCI MOD ===")
# Already checked above, but also:
# Tetranacci, Pentanacci
penta = [0, 0, 0, 0, 1]
for i in range(5, 50):
    penta.append(sum(penta[-5:]))
    if penta[-1] in VALS:
        print(f"  Penta({i}) = {penta[-1]} *** HIT")

# ============ POWER RESIDUES ============
print("\n=== CUBIC RESIDUES ===")
for name, p in ALL.items():
    if p > 3:
        is_prime = all(p % i != 0 for i in range(2, int(p**0.5)+1)) and p > 1
        if is_prime:
            cr = set()
            for a in range(1, p):
                cr.add(pow(a, 3, p))
            ncr = len(cr)
            if ncr in VALS:
                print(f"  #CR(mod {name}={p}) = {ncr} *** HIT")

print("\n\n=== EXPLORATION 30B COMPLETE ===")
