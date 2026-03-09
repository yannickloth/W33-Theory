V,K,LAM,MU,Q=40,12,2,4,3;E=V*K//2;R,S=2,-4;F,G=24,15;N=Q+2
THETA=K-R;ALPHA=V//MU;OMEGA=MU;DIM_O=K-MU;ALBERT=V-(Q**2+MU)
PHI3=Q**2+Q+1;PHI6=Q**2-Q+1;K_BAR=V-1-K;AUT=51840
from fractions import Fraction as Fr

def charpoly(x):
    return (x-K)*(x-R)**F*(x-S)**G

def comp_charpoly(x):
    return (x-K_BAR)*(x+R+1)**F*(x+S+1)**G

print("=== CHAR POLY AT SPECIAL POINTS ===")
print("p(-1) = -PHI3*Q^(V-1):", charpoly(-1)==-PHI3*Q**(V-1))
print("p(1) = -(K-1)*N^G:", charpoly(1)==-(K-1)*N**G)
print("p(q) = -Q^2*PHI6^G:", charpoly(Q)==-Q**2*PHI6**G)
print("p(-q) = -G*N^F:", charpoly(-Q)==-G*N**F)
print("p(0) = -Q*2^(DIM_O*PHI6):", charpoly(0)==-Q*2**(DIM_O*PHI6))
print("p(MU) = -2^72 where 72=|Delta(E6)|:", charpoly(MU)==-2**72)
print("p(-MU) = 0 (since -MU=S):", charpoly(-MU)==0)
print("p(N) = -PHI6*Q^(2*ALBERT):", charpoly(N)==-PHI6*Q**(2*ALBERT))
print("p(DIM_O) = -MU*(r-s)^F*K^G:", charpoly(DIM_O)==-MU*(R-S)**F*K**G)
print("p(r-s) = -(r-s)*OMEGA^F*ALPHA^G:", charpoly(R-S)==-(R-S)*OMEGA**F*ALPHA**G)

print()
print("=== COMPLEMENT CHAR POLY ===")
print("A_bar eigenvalues: K_bar=27, -(R+1)=-3, -(S+1)=3")
print("p_comp(0) = Q^42 where 42=V+LAM:", comp_charpoly(0)==Q**(V+LAM))
print("p_comp(Q) = 0 (since Q=-(S+1)):", comp_charpoly(Q)==0)

print()
print("=== INTERLACING ===")
g1,g2,g3,g4,g5 = (-3)-S, R-(-3), (-S-1)-R, K-(-S-1), K_BAR-K
print(f"Gaps: {g1}, {g2}, {g3}, {g4}, {g5}")
print(f"= 1, N, 1, Q^2, G: {(g1,g2,g3,g4,g5)==(1,N,1,Q**2,G)}")
print(f"Gap product = {g1*g2*g3*g4*g5} = ALBERT*N^2 = {ALBERT*N**2}: {g1*g2*g3*g4*g5==ALBERT*N**2}")

print()
print("=== FACTOR TABLE ===")
print(f"x=-1: (x-K)=-PHI3={-1-K}, (x-R)=-Q={-1-R}, (x-S)=Q={-1-S}")
print(f"x=1: (x-K)=-(K-1)={1-K}, (x-R)=-1={1-R}, (x-S)=N={1-S}")
print(f"x=Q: (x-K)=-Q^2={Q-K}, (x-R)=1={Q-R}, (x-S)=PHI6={Q-S}")
print(f"x=N: (x-K)=-PHI6={N-K}, (x-R)=Q={N-R}, (x-S)=Q^2={N-S}")
print(f"x=MU: (x-K)=-DIM_O={MU-K}, (x-R)=LAM={MU-R}, (x-S)=DIM_O={MU-S}")
print(f"x=DIM_O: (x-K)=-MU={DIM_O-K}, (x-R)=r-s={DIM_O-R}, (x-S)=K={DIM_O-S}")
print(f"x=r-s: (x-K)=-(r-s)={R-S-K}, (x-R)=OMEGA={R-S-R}, (x-S)=ALPHA={R-S-S}")

# Verify all factor assertions
assert -1-K == -PHI3 and -1-R == -Q and -1-S == Q
assert 1-K == -(K-1) and 1-R == -1 and 1-S == N
assert Q-K == -Q**2 and Q-R == 1 and Q-S == PHI6
assert N-K == -PHI6 and N-R == Q and N-S == Q**2
assert MU-K == -DIM_O and MU-R == LAM and MU-S == DIM_O
assert DIM_O-K == -MU and DIM_O-R == R-S and DIM_O-S == K
assert R-S-K == -(R-S) and R-S-R == OMEGA and R-S-S == ALPHA
print("All factor assertions verified!")

print()
print("=== POLYNOMIAL SYMMETRIES ===")
# Notice MU and DIM_O are symmetric:
# MU-K = -DIM_O, DIM_O-K = -MU → MU+DIM_O = K!
print(f"MU + DIM_O = K: {MU+DIM_O} = {K}: {MU+DIM_O==K}")
# MU-S = DIM_O, DIM_O-S = K → these are shifted by MU:
print(f"MU-S = DIM_O: {MU-S} = {DIM_O}: {MU-S==DIM_O}")
print(f"DIM_O-S = K: {DIM_O-S} = {K}: {DIM_O-S==K}")
# MU-R = LAM, DIM_O-R = r-s:
print(f"MU-R = LAM: {MU-R} = {LAM}: {MU-R==LAM}")
print(f"DIM_O-R = r-s: {DIM_O-R} = {R-S}: {DIM_O-R==R-S}")

# Similarly for 1 and Q, -1 and -Q, these pair up.
# 1-S = N, Q-S = PHI6 → related by Q-1=LAM shift
# 1-R = -1, Q-R = 1 → shift of LAM
# -1-K = -PHI3, -Q-K = -G (is -Q-K=-15? -3-12=-15=G(-1)=-G)
print(f"-Q-K = -G: {-Q-K} = {-G}: {-Q-K==-G}")

print()
print("=== CAYLEY-HAMILTON TRACES ===")
# tr(A^n) = K^n + f*R^n + g*S^n
for n in range(1, 9):
    tr = K**n + F*R**n + G*S**n
    print(f"tr(A^{n}) = {tr}")

# tr(A^0) = V = 40
# tr(A^1) = 0 (always for undirected graph)
# tr(A^2) = 2E = VK
# tr(A^3) = 6*C3 (6 times number of triangles)
# tr(A^4) relates to paths of length 4
print()
tr0 = K**0 + F*R**0 + G*S**0
tr1 = K + F*R + G*S
tr2 = K**2 + F*R**2 + G*S**2
tr3 = K**3 + F*R**3 + G*S**3
print(f"tr(A^0) = {tr0} = V: {tr0==V}")
print(f"tr(A^1) = {tr1} = 0: {tr1==0}")
print(f"tr(A^2) = {tr2} = 2E = {2*E}: {tr2==2*E}")
print(f"tr(A^3) = {tr3} = 6*C3 = {6*160}: {tr3==6*160}")

# Higher traces:
tr4 = K**4 + F*R**4 + G*S**4
tr5 = K**5 + F*R**5 + G*S**5
tr6 = K**6 + F*R**6 + G*S**6
print(f"tr(A^4) = {tr4}")
print(f"tr(A^5) = {tr5}")
print(f"tr(A^6) = {tr6}")

# tr(A^4) = K^4 + f*R^4 + g*S^4 = 20736 + 24*16 + 15*256 = 20736+384+3840 = 24960
# 24960 = V * 624 = V * 624. 624 = 2^4 * 39 = 16*39. Hmm.
# More naturally: tr(A^4) = sum_i (A^4)_ii = sum_i (sum_j A^2_ij)^2 ... hmm no.
# tr(A^4) counts closed walks of length 4.
# = V*[K + K*(K-1)*LAM + K*(V-1-K)*MU - K ... ] complicated.
# Let me factor: 24960 / V = 624 = K*52 = K*4*13 = K*MU*PHI3
print(f"tr(A^4)/V = {tr4//V} = K*MU*PHI3 = {K*MU*PHI3}: {tr4//V==K*MU*PHI3}")

# tr(A^5):
print(f"tr(A^5) = {tr5}")
# = 12^5 + 24*32 + 15*(-1024) = 248832 + 768 - 15360 = 234240
# 234240 / V = 5856 = ... big number
# 234240 = E * 976 = E * 976
# 234240 / 6 = 39040 = ... not clean from that angle
# 234240 / (V*K) = 234240/480 = 488 (approx) = 488.0
print(f"tr(A^5)/(6*V) = {Fr(tr5, 6*V)}")

# tr(A^6):
# = 12^6 + 24*64 + 15*4096 = 2985984 + 1536 + 61440 = 3048960
# 3048960 / V = 76224 = K * 6352 = ... 
print(f"tr(A^6)/V = {tr6//V}")
# 76224 = 2^7 * 3 * 199? Let me factor
import math
n = tr6//V
factors = []
for p in [2,3,5,7,11,13]:
    while n%p==0: factors.append(p); n//=p
if n>1: factors.append(n)
print(f"  factors: {factors}")
# 76224 = 2^5 * 3 * ... let me just compute
print(f"  76224 = {76224} = K^2 * MU * PHI3 * ... hmm")
print(f"  76224 / K^2 = {76224 // K**2}")
# 76224/144 = 529.33... not integer
print(f"  76224 / (K*MU*PHI3) = {Fr(76224, K*MU*PHI3)}")
# 76224/624 = 122.15... also not integer
# Let me try: tr(A^4)/V = K*(K-1+LAM*K(K-1)/V + ...) ... too complex.

print()
print("=== ZETA FUNCTION SPECIAL VALUES ===")
# The reciprocal of Ihara zeta at u:
# Z(u)^{-1} = (1-u^2)^{E-V} * det(I - u*A + (K-1)*u^2*I)
# = (1-u^2)^200 * (1+11u^2-12u)*(1+11u^2-2u)^24*(1+11u^2+4u)^15

# At u=1: (1-1)^200 = 0. Always zero. Pole of Z(u).
# At u=-1: (1-1)^200 = 0. Also zero.
# At u=0: 1^200 * 1*1*1 = 1. Z(0) = 1. ✓

# The 'spectral determinant':
# D(u) = det(I - uA + (K-1)u^2 I)
# D(u) = prod (1 + (K-1)u^2 - lambda_j * u)
def D(u):
    return (1+(K-1)*u**2-K*u) * (1+(K-1)*u**2-R*u)**F * (1+(K-1)*u**2-S*u)**G

# D(0) = 1
print(f"D(0) = {D(Fr(0))}")
# D(1/(K-1)):
u = Fr(1, K-1)
print(f"D(1/(K-1)) = {D(u)}")
# 1+(K-1)/(K-1)^2 - K/(K-1) = 1+1/(K-1) - K/(K-1) = 1-(K-1)/(K-1) = 1-1 = 0? No:
# 1 + (K-1)*(1/(K-1))^2 - K/(K-1) = 1 + 1/(K-1) - K/(K-1) = 1 - (K-1)/(K-1) = 0
# So D(1/(K-1)) = 0. Makes sense since u=1/(K-1) is the Ihara pole from eigenvalue K.

# D(1/K):
u = Fr(1, K)
Dval = D(u)
print(f"D(1/K) = {Dval}")

# D at reciprocal of each eigenvalue:
# D(1/R) = ... contains factor (1+(K-1)/R^2 - R/R) = 1+(K-1)/4 - 1 = (K-1)/4 = 11/4
# multiplied by other factors. But the R-factor: 1+(K-1)/R^2 - R^2/R = 1+11/4-2 = -1+11/4 = 7/4
# Wait: D(1/R) factor for R: 1+(K-1)*(1/R)^2 - R*(1/R) = 1+(K-1)/R^2 - 1 = (K-1)/R^2
u = Fr(1, R)
Dval_R = D(u)
print(f"D(1/R) = {Dval_R}")
# Factor: R-factor = ((K-1)/R^2)^f = (11/4)^24
# K-factor = 1+11/4-12/2 = 1+2.75-6 = -2.25 = -9/4 = -Q^2/MU
# S-factor = 1+11/4+4/2 = 1+2.75+2 = 5.75 = 23/4 = (ALBERT-MU)/MU

print()
print("=== NEWTON IDENTITIES (power sums vs symmetric funcs) ===")
# For eigenvalues K, R, S with multiplicities 1, f, g:
# p_n = K^n + f*R^n + g*S^n (trace of A^n)
# e_1 = K + f*R + g*S = 0 (always)
# e_2 = sum of products of pairs of eigenvalues (with mult)
# For the elementary symmetric polynomials of the multiset:
# e_1 = trace = 0
# e_2 = (trace^2 - tr(A^2))/2 = (0 - 2E)/2 = -E = -240
# But this is the sum of products of pairs of eigenvalues
e2 = -E
print(f"e_2 = -E = {e2}")
# e_V = det(A) = p(0) = -Q*2^56
print(f"e_V = det(A) = -Q*2^(DIM_O*PHI6)")
