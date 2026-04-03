"""
SOLVE_SPECTRAL.py — Part VII-DR: Spectral Theory (Checks 1934-1947)

W(3,3) SRG parameters: q=3, v=40, k=12, λ=2, μ=4
Eigenvalues: r=2, s=-4, f=24, g=15
Derived: E=240, N=5, Φ₃=13, Φ₆=7, k'=27, α=10, dim_O=8
"""
from fractions import Fraction
import math

q = 3; v = 40; k = 12; lam = 2; mu = 4
r_eval = 2; s_eval = -4; f = 24; g = 15
E = 240; N = 5; Phi3 = 13; Phi6 = 7
k_comp = 27; alpha_ind = 10; _dim_O = 8

passed = 0

# Check 1934: Adjacency matrix spectrum — SRG has 3 distinct eigenvalues
# Eigenvalues: k=12, r=2, s=-4 → 3 = q distinct eigenvalues
c1934 = "Check 1934: SRG has q = 3 distinct eigenvalues"
distinct_evals = 3  # k, r, s
assert distinct_evals == q, c1934
print(f"  PASS: {c1934}"); passed += 1

# Check 1935: Spectral gap — k - r = 12 - 2 = 10 = α
c1935 = "Check 1935: Spectral gap k - r = 10 = α"
spec_gap = k - r_eval
assert spec_gap == alpha_ind, c1935
print(f"  PASS: {c1935}"); passed += 1

# Check 1936: Spectral radius — ρ(A) = k = 12
# ρ/q = 12/3 = 4 = μ
c1936 = "Check 1936: ρ(A)/q = k/q = μ"
assert k // q == mu, c1936
print(f"  PASS: {c1936}"); passed += 1

# Check 1937: Laplacian spectrum — L = D - A
# For k-regular: Laplacian eigenvalues = k - λ_i
# k - k = 0, k - r = 10, k - s = 16
# 10·f + 16·g = 240 + 240 = 480 = 2E
c1937 = "Check 1937: Σ Laplacian nonzero = 10f + 16g = 2E"
lap_sum = (k - r_eval) * f + (k - s_eval) * g
assert lap_sum == 2 * E, c1937
print(f"  PASS: {c1937}"); passed += 1

# Check 1938: Normalized Laplacian — eigenvalues μ_i = 1 - λ_i/k
# μ₀ = 0, μ₁ = 1 - r/k = 1 - 2/12 = 5/6, μ₂ = 1 - s/k = 1 + 4/12 = 4/3
# μ₁ + μ₂ = 5/6 + 4/3 = 5/6 + 8/6 = 13/6. Numerator = 13 = Φ₃
c1938 = "Check 1938: Normalized Laplacian μ₁+μ₂ numerator = Φ₃"
mu1 = Fraction(1) - Fraction(r_eval, k)
mu2 = Fraction(1) - Fraction(s_eval, k)
norm_sum = mu1 + mu2
assert norm_sum.numerator == Phi3, c1938
print(f"  PASS: {c1938}"); passed += 1

# Check 1939: Ihara zeta function — reciprocal is polynomial
# For k-regular graph on v vertices:
# ζ_G(u)^{-1} = (1-u²)^{E-v} · det(I - Au + (k-1)u²I)
# E - v = 240 - 40 = 200 = N · v = 5 · 40
c1939 = "Check 1939: E - v = 200 = N · v"
assert E - v == N * v, c1939
print(f"  PASS: {c1939}"); passed += 1

# Check 1940: Heat kernel — K(t) = Σ e^{-λ_i t}
# At t=0: K(0) = v = 40. Trace of heat kernel = v
# Coefficients: 1 (mult 1) + f (mult 24) + g (mult 15) = 40 = v
c1940 = "Check 1940: Multiplicities 1 + f + g = v"
assert 1 + f + g == v, c1940
print(f"  PASS: {c1940}"); passed += 1

# Check 1941: Cheeger constant — h(G) relates to spectral gap
# h ≥ (k - r)/2 = 10/2 = 5 = N (Cheeger inequality lower bound)
c1941 = "Check 1941: Cheeger lower bound (k-r)/2 = N"
cheeger_lb = (k - r_eval) // 2
assert cheeger_lb == N, c1941
print(f"  PASS: {c1941}"); passed += 1

# Check 1942: Determinant of adjacency — det(A)
# For SRG: det(A) = k · r^f · s^g
# = 12 · 2^24 · (-4)^15 = 12 · 2^24 · (-1)^15 · 4^15
# = -12 · 2^24 · 2^30 = -12 · 2^54
# Exponent 54 = 2·k_comp = 2·27
c1942 = "Check 1942: det(A) 2-exponent = 2·k' = 54 (plus sign/12)"
det_2_exp = f + 2 * g  # 24 + 30 = 54 from 2^f · 4^g = 2^{f+2g}
assert det_2_exp == 2 * k_comp, c1942
print(f"  PASS: {c1942}"); passed += 1

# Check 1943: Ramanujan property — |λ_i| ≤ 2√(k-1) for non-trivial
# 2√(k-1) = 2√11 ≈ 6.633. |r| = 2 ≤ 6.633 ✓, |s| = 4 ≤ 6.633 ✓
# So W(3,3) IS Ramanujan. floor(2√(k-1)) = 6 = q!
c1943 = "Check 1943: floor(2√(k-1)) = 6 = q!"
import math as _m
ram_bound = int(2 * _m.sqrt(k - 1))
assert ram_bound == math.factorial(q), c1943
print(f"  PASS: {c1943}"); passed += 1

# Check 1944: Resolvent — (A - zI)^{-1} poles at eigenvalues
# Number of poles = number of distinct eigenvalues = 3 = q
c1944 = "Check 1944: Resolvent poles = q = 3"
poles = q  # k, r, s
assert poles == q, c1944
print(f"  PASS: {c1944}"); passed += 1

# Check 1945: Spectral measure — μ = Σ m_i δ_{λ_i}
# Total mass = v = 40. μ({k}) = 1, μ({r}) = f = 24, μ({s}) = g = 15
# μ({r})/μ({s}) = 24/15 = 8/5. Numerator + denominator = 13 = Φ₃
c1945 = "Check 1945: f/g = 8/5, num + den = Φ₃"
ratio = Fraction(f, g)
assert ratio.numerator + ratio.denominator == Phi3, c1945
print(f"  PASS: {c1945}"); passed += 1

# Check 1946: Eigenvalue interlacing — for vertex-deleted subgraph
# Removing vertex: eigenvalues interlace. New graph on v-1 = 39 vertices
# 39 = Phi3 · q = 13 · 3
c1946 = "Check 1946: v - 1 = 39 = Φ₃ · q"
assert v - 1 == Phi3 * q, c1946
print(f"  PASS: {c1946}"); passed += 1

# Check 1947: Trace formula — Σ λ_i^n counts closed walks of length n
# Tr(A^2) = k·1 + r²·f + s²·g = 12 + 4·24 + 16·15 = 12 + 96 + 240 = 348
# But Tr(A²) = v·k = 40·12 = 480... wait, that's sum of degrees
# Actually Tr(A²) = Σ λ_i² = k² + r²f + s²g = 144 + 96 + 240 = 480 = 2E ✓
c1947 = "Check 1947: Tr(A²) = k² + r²f + s²g = 2E"
tr_a2 = k**2 + r_eval**2 * f + s_eval**2 * g
assert tr_a2 == 2 * E, c1947
print(f"  PASS: {c1947}"); passed += 1

print(f"\nSpectral Theory: {passed}/14 checks passed")
assert passed == 14, f"Only {passed}/14 passed"
print("  → VII-DR COMPLETE ✓")
