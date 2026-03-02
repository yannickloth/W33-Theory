# extended analysis script for delta formulas
import itertools

# data from report
c0_data = [
    (((0,1),(2,0)),(0,2,0)),
    (((0,2),(1,0)),(0,1,0)),
    (((1,0),(2,1)),(1,0,1)),
    (((1,0),(1,1)),(1,2,2)),
    (((2,0),(0,2)),(0,0,0)),
    (((2,0),(2,2)),(1,1,2)),
    (((2,0),(1,2)),(1,0,1)),
]
# associated ΔE matrices for t=1 and t=2
deltaE_data={
    ((0,1),(2,0)):{1: ((2,1,0),(2,2,2),(2,1,0)),2: ((1,0,2),(2,0,1),(1,2,0))},
    ((0,2),(1,0)):{1: ((2,2,1),(2,0,0),(2,0,0)),2: ((1,1,2),(2,0,0),(1,0,0))},
    ((1,0),(2,1)):{1: ((2,1,0),(1,2,2),(2,0,0)),2: ((1,0,1),(1,1,1),(1,0,0))},
    ((1,0),(1,1)):{1: ((0,2,0),(0,1,0),(0,1,0)),2: ((0,2,0),(0,0,0),(0,2,0))},
    ((2,0),(0,2)):{1: ((2,0,2),(2,2,2),(0,1,0)),2: ((0,1,0),(1,0,1),(0,2,0))},
    ((2,0),(2,2)):{1: ((2,1,0),(1,0,0),(0,0,0)),2: ((0,2,0),(2,0,0),(0,0,0))},
    ((2,0),(1,2)):{1: ((2,0,2),(1,0,0),(2,1,0)),2: ((1,2,1),(1,1,0),(1,2,0))},
}

# monomials with degree <=2 in p,q,r,s
monomials = [(i,j,k,l) for i in range(3) for j in range(3) for k in range(3) for l in range(3) if (i+j+k+l)<=2]

# gaussian elimination mod3

def solve(A,b):
    A=[row[:] for row in A]; b=b[:]
    n=len(A); m=len(A[0])
    rank=0
    sol=[0]*m
    for col in range(m):
        pivot=None
        for r in range(rank,n):
            if A[r][col]%3!=0:
                pivot=r; break
        if pivot is None: continue
        A[rank],A[pivot]=A[pivot],A[rank]
        b[rank],b[pivot]=b[pivot],b[rank]
        inv={1:1,2:2}[A[rank][col]%3]
        A[rank]=[(inv*x)%3 for x in A[rank]]
        b[rank]=(inv*b[rank])%3
        for r in range(n):
            if r!=rank and A[r][col]!=0:
                factor=A[r][col]
                A[r]=[(A[r][c]-factor*A[rank][c])%3 for c in range(m)]
                b[r]=(b[r]-factor*b[rank])%3
        rank+=1
    for r in range(rank):
        for c in range(m):
            if A[r][c]!=0:
                sol[c]=b[r]
                break
    return sol

# fit c0 coefficients
def fit_c0():
    A_mat=[]
    b0=[]
    b1=[]
    b2=[]
    for B,coeff in c0_data:
        (p,q),(r,s)=B
        row=[(p**i)*(q**j)*(r**k)*(s**l)%3 for (i,j,k,l) in monomials]
        A_mat.append(row)
        b0.append(coeff[0])
        b1.append(coeff[1])
        b2.append(coeff[2])
    sol0=solve(A_mat,b0)
    sol1=solve(A_mat,b1)
    sol2=solve(A_mat,b2)
    for name,sol in [('alpha0',sol0),('alpha1',sol1),('alpha2',sol2)]:
        exprs=[f"{coeff}*p^{i}q^{j}r^{k}s^{l}" for coeff,(i,j,k,l) in zip(sol,monomials) if coeff!=0]
        print(name,exprs)

# fit E coefficients with t variable

def fit_E():
    mon2=[]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    for m_ in range(3):
                        if i+j+k+l<=2:
                            mon2.append((i,j,k,l,m_))
    samples=[]
    for B,_ in c0_data:
        (p,q),(r,s)=B
        for t in (1,2):
            samples.append((p,q,r,s,t,deltaE_data[B][t]))
    coeff_formulas={}
    for a in range(3):
        for b in range(3):
            A_mat=[]
            bvec=[]
            for p,q,r,s,t,mat in samples:
                row=[(p**i)*(q**j)*(r**k)*(s**l)*(t**m_)%3 for (i,j,k,l,m_) in mon2]
                A_mat.append(row)
                bvec.append(mat[a][b])
            sol=solve(A_mat,bvec)
            exprs=[f"{coeff}*p^{i}q^{j}r^{k}s^{l}t^{m_}" for coeff,(i,j,k,l,m_) in zip(sol,mon2) if coeff!=0]
            coeff_formulas[(a,b)]=exprs
    print("\nDelta E coefficient formulas:")
    for (a,b),exprs in coeff_formulas.items():
        print(f"E[{a},{b}] = {exprs}")

if __name__=='__main__':
    fit_c0()
    fit_E()
