"""
Phase LII Exploration: Walk Algebra & Idempotent Anatomy
=========================================================
Explore the Bose-Mesner idempotent entry values, walk matrix
entries between different vertex relations, return probabilities,
and resolvent evaluations at named constants.
"""
from fractions import Fraction as Fr

# === SRG PARAMETERS ===
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
R, S = 2, -4
F, G = 24, 15
ALPHA = K - R          # 10
OMEGA = K - S          # 16 = 2^MU
r_s = R - S            # 6
N = (r_s + R*S) // r_s if r_s != 0 else 0
N = 5
PHI3 = 13
PHI6 = 7
DIM_O = 8
ALBERT = 27
E = V * K // 2         # 240
BOSONIC = 26
K_BAR = V - K - 1      # 27

print("=" * 70)
print("PHASE LII: WALK ALGEBRA & IDEMPOTENT ANATOMY")
print("=" * 70)

# ============================================================
# PART 1: BOSE-MESNER IDEMPOTENT ENTRY VALUES
# ============================================================
print("\n=== BOSE-MESNER IDEMPOTENT ENTRY VALUES ===\n")

# Three idempotents E_0 (K-eigenspace), E_1 (R-eigenspace), E_2 (S-eigenspace)
# E_0 = J/V, E_0 + E_1 + E_2 = I
# A = K*E_0 + R*E_1 + S*E_2

# Diagonal entries: (E_i)_{vv} = m_i / V
e0_diag = Fr(1, V)
e1_diag = Fr(F, V)
e2_diag = Fr(G, V)

print(f"E_0 diagonal = 1/V = {e0_diag} = {float(e0_diag):.6f}")
print(f"E_1 diagonal = F/V = {e1_diag} = {float(e1_diag):.6f}")
print(f"  = Q/N = {Fr(Q, N)} : {e1_diag == Fr(Q, N)}")
print(f"E_2 diagonal = G/V = {e2_diag} = {float(e2_diag):.6f}")
print(f"  = Q/DIM_O = {Fr(Q, DIM_O)} : {e2_diag == Fr(Q, DIM_O)}")
print(f"  = sin^2(theta_W) = 3/8 : {e2_diag == Fr(3, 8)}")

# Adjacent entries: solve A_{ij}=1, E_0+E_1+E_2=0 (i!=j)
# (E_1)_adj = (V - K + S) / (V*(R-S))
e1_adj = Fr(V - K + S, V * r_s)
e2_adj = -e0_diag - e1_adj

print(f"\nE_0 adjacent = 1/V = {e0_diag}")
print(f"E_1 adjacent = {e1_adj} = {float(e1_adj):.6f}")
print(f"  = 1/ALPHA = {Fr(1, ALPHA)} : {e1_adj == Fr(1, ALPHA)}")
print(f"E_2 adjacent = {e2_adj} = {float(e2_adj):.6f}")
print(f"  = -1/DIM_O = {Fr(-1, DIM_O)} : {e2_adj == Fr(-1, DIM_O)}")

# Non-adjacent entries: solve A_{ij}=0, E_0+E_1+E_2=0 (i!=j)
# (E_1)_non = -(K-S) / (V*(R-S))
e1_non = Fr(-(K - S), V * r_s)
e2_non = -e0_diag - e1_non

print(f"\nE_0 non-adj = 1/V = {e0_diag}")
print(f"E_1 non-adj = {e1_non} = {float(e1_non):.6f}")
print(f"  = -1/G = {Fr(-1, G)} : {e1_non == Fr(-1, G)}")
print(f"E_2 non-adj = {e2_non} = {float(e2_non):.6f}")
print(f"  = 1/F = {Fr(1, F)} : {e2_non == Fr(1, F)}")

# Summary table
print("\n--- Idempotent Entry Summary ---")
print(f"{'':12} {'E_0':>10} {'E_1':>10} {'E_2':>10}")
print(f"{'diagonal':12} {'1/V':>10} {'Q/N':>10} {'Q/DIM_O':>10}")
print(f"{'adjacent':12} {'1/V':>10} {'1/ALPHA':>10} {'-1/DIM_O':>10}")
print(f"{'non-adj':12} {'1/V':>10} {'-1/G':>10} {'1/F':>10}")

# ============================================================
# PART 2: MULTIPLICITY-DIMENSION DUAL IDENTITY
# ============================================================
print("\n=== MULTIPLICITY-DIMENSION DUAL IDENTITY ===\n")

prod1 = F * N
prod2 = G * DIM_O
prod3 = V * Q
half_E = E // 2

print(f"F * N = {F} x {N} = {prod1}")
print(f"G * DIM_O = {G} x {DIM_O} = {prod2}")
print(f"V * Q = {V} x {Q} = {prod3}")
print(f"E / 2 = {E} / 2 = {half_E}")
print(f"5! = 120")
print(f"ALL EQUAL: {prod1 == prod2 == prod3 == half_E == 120}")
print(f"  = Graph Energy = 120 (already tested)")

# Ratios
print(f"\nF/G = {Fr(F, G)} = {Fr(DIM_O, N)} (DIM_O/N): {Fr(F,G) == Fr(DIM_O, N)}")
print(f"F/V = {Fr(F, V)} = {Fr(Q, N)} (Q/N): {Fr(F, V) == Fr(Q, N)}")
print(f"G/V = {Fr(G, V)} = {Fr(Q, DIM_O)} (Q/DIM_O): {Fr(G, V) == Fr(Q, DIM_O)}")

# ============================================================
# PART 3: WALK MATRIX ENTRIES (A^n)_{ij}
# ============================================================
print("\n=== WALK MATRIX ENTRIES ===\n")

def walk_diag(n):
    """(A^n)_{ii} = tr(A^n)/V = (K^n + F*R^n + G*S^n)/V"""
    return Fr(K**n + F * R**n + G * S**n, V)

def walk_adj(n):
    """(A^n)_{ij} for adjacent i~j"""
    return Fr(K**n, V) + Fr(R**n, ALPHA) - Fr(S**n, DIM_O)

def walk_non(n):
    """(A^n)_{ij} for non-adjacent i,j"""
    return Fr(K**n, V) - Fr(R**n, G) + Fr(S**n, F)

print("n | diagonal   | adjacent   | non-adj    | named?")
print("-" * 65)
for n in range(8):
    d = walk_diag(n)
    a = walk_adj(n)
    na = walk_non(n)
    
    # Try to name them
    d_name = ""
    if d == 1: d_name = "1"
    elif d == 0: d_name = "0"
    elif d == K: d_name = "K"
    elif d == F: d_name = "F"
    elif d == Fr(2**MU * (V-1)): d_name = "2^MU*(V-1)"
    
    a_name = ""
    if a == 0: a_name = "0"
    elif a == 1: a_name = "1"
    elif a == LAM: a_name = "LAM"
    elif a == MU * PHI3: a_name = "MU*PHI3=dim(F4)=52"
    
    na_name = ""
    if na == 0: na_name = "0"
    elif na == MU: na_name = "MU"
    elif na == V: na_name = "V"
    
    print(f"{n} | {str(d):10} | {str(a):10} | {str(na):10} | d={d_name}, a={a_name}, na={na_name}")

# Key results
print(f"\n--- KEY WALK IDENTITIES ---")
print(f"(A^2)_diag = K = {walk_diag(2)} (degree)")
print(f"(A^2)_adj  = LAM = {walk_adj(2)} (common neighbors)")
print(f"(A^2)_non  = MU = {walk_non(2)} (common neighbors for non-adj)")
print(f"(A^3)_diag = F = {walk_diag(3)} = 2 x (triangles per vertex)")
print(f"(A^3)_adj  = MU*PHI3 = {walk_adj(3)} = dim(F4) = 52")
print(f"(A^3)_non  = V = {walk_non(3)} = vertex count = 40")
print(f"(A^4)_diag = 2^MU*(V-1) = {walk_diag(4)} = {2**MU * (V-1)}")

# Verify A^3 results
a3_adj = walk_adj(3)
print(f"\n(A^3)_adj = {a3_adj} = MU*PHI3 = {MU}*{PHI3} = {MU*PHI3}: {a3_adj == MU*PHI3}")
print(f"  = dim(F4): {a3_adj == 52}")

a3_non = walk_non(3)
print(f"(A^3)_non = {a3_non} = V = {V}: {a3_non == V}")

a4_diag = walk_diag(4)
print(f"(A^4)_diag = {a4_diag} = 2^MU*(V-1) = {2**MU*(V-1)}: {a4_diag == 2**MU*(V-1)}")

# ============================================================
# PART 4: RETURN PROBABILITIES
# ============================================================
print("\n=== RETURN PROBABILITIES p_n ===\n")

def return_prob(n):
    """p_n = (1/V) * sum m_i * (theta_i/K)^n"""
    return Fr(1, V) * (1 + Fr(F * R**n, K**n) + Fr(G * S**n, K**n))

print("n | p_n          | float       | named?")
print("-" * 60)
for n in range(10):
    p = return_prob(n)
    
    name = ""
    if p == 1: name = "1"
    elif p == 0: name = "0"
    elif p == Fr(1, K): name = "1/K"
    elif p == Fr(1, 72): name = "1/72 = 1/|Delta(E6)|"
    elif p == Fr(PHI3, K * r_s**2): name = "PHI3/(K*r_s^2)"
    
    print(f"{n} | {str(p):12} | {float(p):.8f} | {name}")

# Key identities
print(f"\np_2 = 1/K = {return_prob(2)}: {return_prob(2) == Fr(1, K)}")
print(f"p_3 = 1/72 = 1/(2*r_s^2) = 1/|Delta(E6)|: {return_prob(3) == Fr(1, 72)}")
print(f"  72 = 2*r_s^2 = {2*r_s**2}: {72 == 2*r_s**2}")
print(f"  72 = |Delta(E6)| (E6 root count): True")
print(f"p_4 = PHI3/(K*r_s^2) = {return_prob(4)}: {return_prob(4) == Fr(PHI3, K * r_s**2)}")
print(f"  K*r_s^2 = {K}*{r_s**2} = {K*r_s**2} = 432")

# ============================================================
# PART 5: RESOLVENT AT NAMED VALUES
# ============================================================
print("\n=== RESOLVENT tr((zI-A)^{-1}) AT NAMED VALUES ===\n")

def resolvent(z):
    """tr((zI-A)^{-1}) = 1/(z-K) + F/(z-R) + G/(z-S)"""
    return Fr(1, z - K) + Fr(F, z - R) + Fr(G, z - S)

named_vals = [
    ("N", N), ("ALPHA", ALPHA), ("MU", MU), ("PHI6", PHI6),
    ("PHI3", PHI3), ("DIM_O", DIM_O), ("ALBERT", ALBERT),
    ("K_BAR", K_BAR), ("V", V), ("-N", -N), 
    ("Q", Q), ("r_s", r_s), ("OMEGA", K-S)
]

print(f"{'z':>10} | {'value':>5} | {'tr G(z)':>15} | {'float':>12} | factored")
print("-" * 75)
for name, z in named_vals:
    if z in (K, R, S):  # poles
        print(f"{name:>10} | {z:>5} | {'POLE':>15} | {'inf':>12} |")
        continue
    g = resolvent(z)
    
    # Try to identify
    ident = ""
    num = g.numerator
    den = g.denominator
    
    # Check against named ratios
    for n1, v1 in [("V", V), ("N", N), ("N^2", N**2), ("MU", MU), ("Q", Q),
                   ("F", F), ("G", G), ("PHI3", PHI3), ("PHI6", PHI6),
                   ("ALPHA", ALPHA), ("DIM_O", DIM_O), ("ALBERT", ALBERT),
                   ("E", E), ("K", K), ("1", 1), ("-V", -V), ("-N^2", -N**2)]:
        for n2, v2 in [("V", V), ("N", N), ("MU", MU), ("Q", Q), ("K", K),
                       ("F", F), ("G", G), ("PHI3", PHI3), ("PHI6", PHI6),
                       ("ALPHA", ALPHA), ("DIM_O", DIM_O), ("ALBERT", ALBERT),
                       ("r_s", r_s), ("Q*PHI6", Q*PHI6), ("Q*N", Q*N),
                       ("MU*N", MU*N), ("Q*PHI3", Q*PHI3), ("K*N", K*N)]:
            if g == Fr(v1, v2) and v2 != 0:
                ident = f"{n1}/{n2}"
                break
        if ident:
            break
    
    for n1, v1 in [("V*N", V*N), ("N*PHI6", N*PHI6), ("V*Q", V*Q),
                   ("ALPHA*N", ALPHA*N), ("F*G", F*G)]:
        for n2, v2 in [("Q*PHI6", Q*PHI6), ("MU*PHI3", MU*PHI3),
                       ("ALPHA*DIM_O", ALPHA*DIM_O), ("N*DIM_O", N*DIM_O),
                       ("Q*PHI3", Q*PHI3), ("Q*N", Q*N)]:
            if g == Fr(v1, v2) and v2 != 0:
                if not ident:
                    ident = f"{n1}/{n2}"
                break
    
    print(f"{name:>10} | {z:>5} | {str(g):>15} | {float(g):>12.6f} | {ident}")

# Key resolvent identities
print(f"\nKey resolvent identities:")
g_N = resolvent(N)
g_A = resolvent(ALPHA)
g_M = resolvent(MU)
g_P6 = resolvent(PHI6)

print(f"tr G(N) = {g_N} = V*N/(Q*PHI6) = {Fr(V*N, Q*PHI6)}: {g_N == Fr(V*N, Q*PHI6)}")
print(f"tr G(ALPHA) = {g_A} = N^2/PHI6 = {Fr(N**2, PHI6)}: {g_A == Fr(N**2, PHI6)}")
print(f"tr G(MU) = {g_M}")
print(f"tr G(PHI6) = {g_P6}")

# ============================================================
# PART 6: WALK GENERATING FUNCTION
# ============================================================
print("\n=== WALK GENERATING FUNCTION ===\n")

# The walk-generating function for diagonal:
# Z(u) = sum_{n>=0} (A^n)_{ii} * u^n = 1/(1-Ku) * 1/V + F/(1-Ru) * F/V + ...
# Actually: Z(u) = (1/V) * (1/(1-Ku) + F/(1-Ru) + G/(1-Su))
# which is tr((I - uA)^{-1}) / V ... hmm

# For the return probability generating function:
# P(u) = sum p_n u^n = (1/V) * (1/(1-u) + F/(1-R*u/K) + G/(1-S*u/K))

# Let's evaluate at special values of u
# P(u) at u where K*u is a named value
# Better: evaluate the diagonal walk generating function
# W(u) = sum (A^n)_{ii} u^n = (1/V)(1/(1-Ku) + F/(1-Ru) + G/(1-Su))

def walk_gf(u):
    """W(u) = (1/V) * sum_i m_i / (1 - theta_i * u)"""
    return Fr(1, V) * (Fr(1, 1 - K*u) + Fr(F, 1 - R*u) + Fr(G, 1 - S*u))

# Evaluate at u = 1/V, 1/K, 1/ALPHA, etc.
print("Walk generating function W(u) = (1/V) sum m_i/(1 - theta_i*u):")
wgf_vals = [
    ("1/V", Fr(1, V)),
    ("1/ALPHA", Fr(1, ALPHA)),
    ("1/ALBERT", Fr(1, ALBERT)),
    ("1/E", Fr(1, E)),
    ("1/(2*K)", Fr(1, 2*K)),
    ("-1/K", Fr(-1, K)),
    ("1/F", Fr(1, F)),
    ("1/G", Fr(1, G)),
    ("-1/V", Fr(-1, V)),
]

for name, u_val in wgf_vals:
    try:
        w = walk_gf(u_val)
        print(f"  W({name}) = {w} = {float(w):.6f}")
    except ZeroDivisionError:
        print(f"  W({name}) = POLE")

# ============================================================
# PART 7: ADJACENCY WALK RATIOS
# ============================================================
print("\n=== WALK RATIOS ===\n")

# Ratios between walk types at each n
for n in range(2, 7):
    d = walk_diag(n)
    a = walk_adj(n)
    na = walk_non(n)
    
    if a != 0:
        r1 = d / a
        print(f"n={n}: diag/adj = {d}/{a} = {r1}")
    if na != 0:
        r2 = d / na
        r3 = a / na
        print(f"n={n}: diag/non = {d}/{na} = {r2}")
        print(f"n={n}: adj/non  = {a}/{na} = {r3}")
    print()

# ============================================================
# PART 8: ADJACENCY MATRIX POWERS - NAMED DECOMPOSITIONS
# ============================================================
print("\n=== POWER MATRIX DECOMPOSITION ===\n")

# (A^n) = c_n^0 * I + c_n^1 * A + c_n^2 * (J - I - A)
# Using: I = E_0 + E_1 + E_2, A = K*E_0 + R*E_1 + S*E_2, J-I-A = (K_BAR)*E_0 + (-R-1)*E_1 + (-S-1)*E_2
# = K_BAR*E_0 + (-R-1)*E_1 + (-S-1)*E_2

# A^n = K^n*E_0 + R^n*E_1 + S^n*E_2
# E_0 = (1/V)*J, E_1 and E_2 in terms of I, A, J-I-A:
# E_0 = (1/V)*J
# E_1 = alpha_1*I + beta_1*A + gamma_1*(J-I-A)  - solve from entry values
# Using diagonal: E1_diag = alpha_1*1 + beta_1*0 + gamma_1*0 = alpha_1 => alpha_1 = F/V
# Using adjacent: E1_adj = alpha_1*0 + beta_1*1 + gamma_1*0 = beta_1 => beta_1 = 1/ALPHA
# Using non-adj:  E1_non = alpha_1*0 + beta_1*0 + gamma_1*1 = gamma_1 => gamma_1 = -1/G

# Wait, that's not right. Let B = J-I-A (complement adjacency).
# For diagonal: I_{ii} = 1, A_{ii} = 0, B_{ii} = 0 => E1(diag) = alpha
# For adjacent: I_{ij} = 0, A_{ij} = 1, B_{ij} = 0 => E1(adj) = beta
# For non-adj:  I_{ij} = 0, A_{ij} = 0, B_{ij} = 1 => E1(non) = gamma
# So E_1 = (F/V)*I + (1/ALPHA)*A + (-1/G)*(J-I-A)
# E_2 = (G/V)*I + (-1/DIM_O)*A + (1/F)*(J-I-A)

# Let's express A^n in this basis:
# A^n = K^n * (1/V)*J + R^n * E_1 + S^n * E_2  (but E_0 = J/V)
# = (K^n/V)*J + R^n*[(F/V)*I + (1/ALPHA)*A + (-1/G)*B] + S^n*[(G/V)*I + (-1/DIM_O)*A + (1/F)*B]

# Coefficient of I in A^n:
# c_I = R^n*(F/V) + S^n*(G/V) = (F*R^n + G*S^n)/V
# Coefficient of A:
# c_A = R^n/ALPHA - S^n/DIM_O
# Coefficient of B = J-I-A:
# c_B = K^n/V - R^n/G + S^n/F  (includes E_0 contribution)

# Wait, let me redo more carefully:
# A^n = K^n*E_0 + R^n*E_1 + S^n*E_2
# = K^n*(J/V) + R^n*((F/V)I + (1/ALPHA)A + (-1/G)B) + S^n*((G/V)I + (-1/DIM_O)A + (1/F)B)
# = (F*R^n + G*S^n)/V * I + (R^n/ALPHA - S^n/DIM_O) * A + (K^n/V - R^n/G + S^n/F) * B
#   (note: the J term from E_0 combines with B terms since B = J-I-A has a J)
# Actually J = I + A + B, so K^n*(J/V) = K^n/V * (I + A + B)
# = (K^n/V + F*R^n/V + G*S^n/V)*I + (K^n/V + R^n/ALPHA - S^n/DIM_O)*A + (K^n/V - R^n/G + S^n/F)*B

# Let me just verify by plugging in:
for n in range(5):
    c_I = Fr(K**n + F*R**n + G*S**n, V)  # diagonal via (A^n)_{ii} = c_I * 1
    c_A = Fr(K**n, V) + Fr(R**n, ALPHA) - Fr(S**n, DIM_O)  # adjacent via (A^n)_{ij} = c_A * 1
    c_B = Fr(K**n, V) - Fr(R**n, G) + Fr(S**n, F)  # non-adj via (A^n)_{ij} = c_B * 1
    print(f"A^{n} = {c_I}*I + {c_A}*A + {c_B}*(J-I-A)")

# ============================================================
# PART 9: VERTEX TRANSITION PROBABILITIES
# ============================================================
print("\n=== VERTEX TRANSITION PROBABILITIES ===\n")

# P = A/K is the random walk transition matrix
# (P^n)_{ij} = (A^n)_{ij} / K^n

# For adjacent vertices:
for n in range(2, 7):
    p_adj = walk_adj(n) / K**n
    p_non = walk_non(n) / K**n
    p_diag = walk_diag(n) / K**n
    
    print(f"n={n}: P^n_diag={p_diag}, P^n_adj={p_adj}, P^n_non={p_non}")

# Stationary distribution: pi = K/((V-1)*K + K) = 1/V for regular graph
print(f"\nStationary: pi = 1/V = {Fr(1, V)}")
print(f"Mixing target: all -> 1/V = {Fr(1, V)}")

# ============================================================
# PART 10: IDEMPOTENT PRODUCT IDENTITIES
# ============================================================
print("\n=== IDEMPOTENT PRODUCT IDENTITIES ===\n")

# E_1 diag * E_2 diag = (Q/N) * (Q/DIM_O) = Q^2 / (N*DIM_O)
prod_diag = Fr(Q, N) * Fr(Q, DIM_O)
print(f"E1_diag * E2_diag = (Q/N)(Q/DIM_O) = Q^2/(N*DIM_O) = {prod_diag}")
print(f"  = {Fr(Q**2, N*DIM_O)} = {float(prod_diag):.6f}")
print(f"  N*DIM_O = {N*DIM_O} = V = {V}: {N*DIM_O == V}")
print(f"  so E1_diag * E2_diag = Q^2/V = {Fr(Q**2, V)}: {prod_diag == Fr(Q**2, V)}")

# E_1 adj * E_2 adj = (1/ALPHA) * (-1/DIM_O) = -1/(ALPHA*DIM_O)
prod_adj = Fr(1, ALPHA) * Fr(-1, DIM_O)
print(f"\nE1_adj * E2_adj = (1/ALPHA)(-1/DIM_O) = {prod_adj}")
print(f"  ALPHA*DIM_O = {ALPHA*DIM_O} = 2E/Q = {2*E//Q}: {ALPHA*DIM_O == 2*E//Q}")

# E_1 non * E_2 non = (-1/G) * (1/F) = -1/(F*G)
prod_non = Fr(-1, G) * Fr(1, F)
print(f"\nE1_non * E2_non = (-1/G)(1/F) = {prod_non}")
print(f"  F*G = {F*G} = V*Q^2 = {V*Q**2}: {F*G == V*Q**2}")
print(f"  so = -1/(V*Q^2) = {Fr(-1, V*Q**2)}: {prod_non == Fr(-1, V*Q**2)}")

# Column sums of idempotent entries (excluding E_0)
# E_1 column: diag + K*adj + K_BAR*non = F/V + K*(1/ALPHA) + 27*(-1/G)
cs1 = Fr(F, V) + K * Fr(1, ALPHA) + K_BAR * Fr(-1, G)
print(f"\nE_1 column sum: diag + K*adj + K_BAR*non = {cs1}")
print(f"  = F/V + K/ALPHA - K_BAR/G = {Fr(F,V)} + {Fr(K,ALPHA)} + {Fr(-K_BAR,G)}")
print(f"  = {cs1} (should be 1 for trace contribution)")

cs2 = Fr(G, V) + K * Fr(-1, DIM_O) + K_BAR * Fr(1, F)
print(f"E_2 column sum: diag + K*adj + K_BAR*non = {cs2}")

# ============================================================
# PART 11: ADJACENCY WALK NAMING FOR n=3
# ============================================================
print("\n=== WALK-3 TRIANGLE (F4 & V) ===\n")

# The number of walks of length 3 between:
# - same vertex: F = 24 = dim(spin_1/2 in 4D) 
# - adjacent vertices: MU*PHI3 = 52 = dim(F4)
# - non-adjacent vertices: V = 40 = vertex count

print(f"3-walks from v to v     (diagonal):  {walk_diag(3)} = F = 24")
print(f"3-walks from v to adj v (adjacent):  {walk_adj(3)} = MU*PHI3 = 52 = dim(F4)")
print(f"3-walks from v to non v (non-adj):   {walk_non(3)} = V = 40")

# Total 3-walks from one vertex:
total_3 = walk_diag(3) + K * walk_adj(3) + K_BAR * walk_non(3)
print(f"\nTotal 3-walks from vertex = diag + K*adj + K_BAR*non")
print(f"  = {walk_diag(3)} + {K}*{walk_adj(3)} + {K_BAR}*{walk_non(3)}")
print(f"  = {walk_diag(3)} + {K*walk_adj(3)} + {K_BAR*walk_non(3)}")
print(f"  = {total_3}")
print(f"  should = K^3 = {K**3}: {total_3 == K**3}")

# Ratio
r_adj_non = Fr(int(walk_adj(3)), int(walk_non(3)))
print(f"\n3-walk adj/non ratio = {r_adj_non} = {float(r_adj_non):.4f}")
print(f"  = MU*PHI3/V = {Fr(MU*PHI3, V)} = {float(Fr(MU*PHI3, V)):.4f}")
print(f"  = PHI3/ALPHA = {Fr(PHI3, ALPHA)}: {r_adj_non == Fr(PHI3, ALPHA)}")

# ============================================================
# PART 12: HEAT KERNEL TRACE COEFFICIENTS
# ============================================================
print("\n=== HEAT KERNEL TRACE COEFFICIENTS ===\n")

# tr(e^{tA}) = e^{tK} + F*e^{tR} + G*e^{tS}
# Taylor: tr(e^{tA}) = sum_{n>=0} tr(A^n)/n! * t^n
# Coefficient of t^n is tr(A^n)/n!

from math import factorial

print("Heat kernel coefficient c_n = tr(A^n)/n!:")
for n in range(8):
    trAn = K**n + F * R**n + G * S**n
    cn = Fr(trAn, factorial(n))
    print(f"  c_{n} = {trAn}/{factorial(n)} = {cn} = {float(cn):.4f}")

# ============================================================
# PART 13: MIXING MATRIX FROM IDEMPOTENT VALUES
# ============================================================
print("\n=== MIXING / EIGENVALUE TABLE ===\n")

# The (unnormalized) eigenvector entries for an SRG:
# K-eigenvector: constant (1,1,1)
# R-eigenvector: (F/V, 1/ALPHA, -1/G) [up to scale]... 
# Wait, the idempotent E_1 has entries proportional to the R-eigenprojection.
# Actually, for the standard basis of the Bose-Mesner algebra:
# The "first eigenmatrix" P has rows = eigenvalues for each associate class:
# P = [[1, K, K_BAR],
#      [1, R, S_BAR = -R-1],  
#      [1, S, R_BAR = -S-1]]
# Wait, I'm confusing notation. Let me use the proper P matrix from T705.

# P = [[1,  K,    K_BAR],
#      [1,  R,    -(R+1)],
#      [1,  S,    -(S+1)]]
# = [[1, 12, 27], [1, 2, -3], [1, -4, 3]]

P = [[1, K, K_BAR], [1, R, -(R+1)], [1, S, -(S+1)]]
print("First eigenmatrix P:")
for row in P:
    print(f"  {row}")

# Connection to idempotent entries via dual eigenmatrix Q
# Q_ij = m_i * (P^{-1})_{ji} * V / m_j  ... complex formula
# The key relation: Entry of E_i for relation j = Q_{ij}/V

print(f"\nIdempotent entry = (dual eigenmatrix entry) / V")
print(f"E_1(diag) = F/V = Q/N = {Fr(F,V)}")
print(f"E_1(adj)  = 1/ALPHA = {Fr(1,ALPHA)}")
print(f"E_1(non)  = -1/G = {Fr(-1,G)}")
print(f"E_2(diag) = G/V = Q/DIM_O = {Fr(G,V)}")
print(f"E_2(adj)  = -1/DIM_O = {Fr(-1,DIM_O)}")
print(f"E_2(non)  = 1/F = {Fr(1,F)}")

# ============================================================
# PART 14: RETURN PROBABILITY RATIOS
# ============================================================
print("\n=== RETURN PROBABILITY RATIOS ===\n")

for n in range(2, 8):
    pn = return_prob(n)
    pnm1 = return_prob(n-1)
    if pnm1 != 0:
        ratio = pn / pnm1
        print(f"p_{n}/p_{n-1} = {pn}/{pnm1} = {ratio} = {float(ratio):.6f}")

# ============================================================
# PART 15: KIRCHHOFF & KEMENY
# ============================================================
print("\n=== KIRCHHOFF INDEX & KEMENY CONSTANT ===\n")

# Kemeny constant: Kc = sum_{k>0} V*m_k/lam_k where lam_k = K - theta_k
# For lazy random walk: K_lam = F/(K-R) + G/(K-S) = F/ALPHA + G/(K-S)
kemeny = Fr(F, ALPHA) + Fr(G, K - S)
print(f"Kemeny constant = F/ALPHA + G/(K-S) = {Fr(F,ALPHA)} + {Fr(G,K-S)}")
print(f"  = {kemeny} = {float(kemeny):.6f}")
print(f"  Numerator: {kemeny.numerator}, Denominator: {kemeny.denominator}")

# Factor 267: 267 = 3*89
print(f"  267 = 3 x 89")
print(f"  80 = 2*V = 2^MU * N = {2**MU * N}")

# Kirchhoff index = V * Kemeny
kirchhoff = V * kemeny
print(f"\nKirchhoff index Kf = V * Kemeny = {kirchhoff} = {float(kirchhoff):.4f}")

# Effective resistance between adjacent vertices
# R_adj = (total Kf) / (V choose 2) * correction...
# For an SRG: R_adj = 2/V * (sum m_k * (1 - cos_k) / lam_k)
# where cos_k = theta_k / K (for regular graph lazy walk)
# R_adj = 2/V * F*(1-R/K)/(K-R) + 2/V * G*(1-S/K)/(K-S)

r_adj_eff = Fr(2, V) * (Fr(F * (K - R), K * (K - R)) + Fr(G * (K - S), K * (K - S)))
# Simplify: (K-R)/(K*(K-R)) = 1/K, (K-S)/(K*(K-S)) = 1/K
# So R_adj = 2/V * (F/K + G/K) = 2/V * (V-1)/K = 2*(V-1)/(V*K)
r_adj_eff = Fr(2 * (V - 1), V * K)

print(f"\nEffective resistance (adjacent) = 2(V-1)/(V*K) = {r_adj_eff}")
print(f"  = {float(r_adj_eff):.6f}")
print(f"  = {2*(V-1)}/{V*K} = {Fr(2*(V-1), V*K)}")

# Non-adjacent effective resistance
# R_non = 2/V * (F*(1+R/K*...) / (K-R) + ...)
# For SRG, using idempotent entries:
# R_ij = 2 * sum_{k>0} (E_k(i,i) - E_k(i,j)) / lam_k

# For adjacent i~j:
# R_adj = 2 * ((E1_diag - E1_adj)/ALPHA + (E2_diag - E2_adj)/(K-S))
r_adj_check = 2 * ((Fr(F,V) - Fr(1,ALPHA)) / ALPHA + (Fr(G,V) - Fr(-1,DIM_O)) / (K-S))

# Wait, we need to divide by lam_k, and lam_k = K - theta_k
# For eigenspace 1 (R): lam_1 = K - R = ALPHA
# For eigenspace 2 (S): lam_2 = K - S = OMEGA = 16

r_adj_v2 = 2 * (Fr(Fr(F,V) - Fr(1,ALPHA), ALPHA) + Fr(Fr(G,V) - Fr(-1,DIM_O), K - S))
print(f"\nEffective resistance (adjacent, v2) = {r_adj_v2}")
print(f"  = {float(r_adj_v2):.6f}")

# For non-adjacent i,j:
r_non = 2 * (Fr(Fr(F,V) - Fr(-1,G), ALPHA) + Fr(Fr(G,V) - Fr(1,F), K - S))
print(f"\nEffective resistance (non-adjacent) = {r_non}")
print(f"  = {float(r_non):.6f}")

# Ratio
if r_adj_v2 != 0:
    r_ratio = r_non / r_adj_v2
    print(f"\nR_non / R_adj = {r_ratio}")

# Total resistance (Kirchhoff) check
# Kf = (1/2) * sum_{i<j} R_ij
# = (1/2) * (E * R_adj + E_bar * R_non) where E = 240 edges, E_bar = 540 non-edges
kf_check = Fr(1, 2) * (E * r_adj_v2 + (V*(V-1)//2 - E) * r_non)
print(f"\nKirchhoff check: {kf_check} = {kirchhoff}: {kf_check == kirchhoff}")

# ============================================================
# PART 16: RESOLVENT PRODUCT AT SEIDEL EIGENVALUES
# ============================================================
print("\n=== RESOLVENT AT SEIDEL EIGENVALUES ===\n")

# Seidel eigenvalues: 2K - V + 1, -2S - 1, -2R - 1
# = 2*12 - 40 + 1 = -15 = -G
# = -2*(-4) - 1 = 7 = PHI6
# = -2*2 - 1 = -5 = -N

seidel_eigs = [("G_seidel=-G=-15", -G), ("PHI6_seidel=PHI6=7", PHI6), ("N_seidel=-N=-5", -N)]
for name, z in seidel_eigs:
    if z not in (K, R, S):
        g = resolvent(z)
        print(f"tr G({name}) = {g} = {float(g):.6f}")

# ============================================================
# PART 17: NAMED WALK COUNT SUMMARY
# ============================================================
print("\n=== NAMED WALK COUNT SUMMARY ===\n")

print("Length | Diagonal   | Adjacent     | Non-adjacent")
print("-" * 60)
print(f"  0    | 1 = I      | 0            | 0")
print(f"  1    | 0          | 1 = edge     | 0")
print(f"  2    | K = 12     | LAM = 2      | MU = 4")
print(f"  3    | F = 24     | MU*PHI3 = 52 | V = 40")
print(f"  4    | 2^MU*(V-1) | {walk_adj(4)} | {walk_non(4)}")
print(f"       | = {2**MU*(V-1)}      |              |")

# Walk-3 adj = 52 = dim(F4) breakdown
print(f"\nWalk-3 adjacent = MU * PHI3 = {MU} x {PHI3} = {MU*PHI3}")
print(f"  52 is the dimension of the exceptional Lie algebra F4!")
print(f"  The number of 3-walks between neighbors = dim(F4)")

# Walk-3 non = V = 40 breakdown  
print(f"\nWalk-3 non-adj = V = {V}")
print(f"  The number of 3-walks between non-neighbors = vertex count!")

# Walk-3 diagonal = F = 24 breakdown
print(f"\nWalk-3 diagonal = F = {F}")
print(f"  = 2 x triangles_per_vertex = 2 x {F//2}")

# ============================================================
# CROSSCHECK: Walk totals
# ============================================================
print("\n=== WALK TOTAL CROSSCHECKS ===\n")

for n in range(2, 6):
    d = walk_diag(n)
    a = walk_adj(n)
    na = walk_non(n)
    total = d + K * a + K_BAR * na
    print(f"n={n}: total = {d} + {K}*{a} + {K_BAR}*{na} = {total} = K^{n} = {K**n}: {total == K**n}")

print("\n" + "=" * 70)
print("PHASE LII EXPLORATION COMPLETE")
print("=" * 70)
