# temporary analysis script
import itertools

# from report data
stuff=[
    (((0,1),(2,0)),(0,2,0)),
    (((0,2),(1,0)),(0,1,0)),
    (((1,0),(2,1)),(1,0,1)),
    (((1,0),(1,1)),(1,2,2)),
    (((2,0),(0,2)),(0,0,0)),
    (((2,0),(2,2)),(1,1,2)),
    (((2,0),(1,2)),(1,0,1)),
]
# monomials with degree <=2
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
        if pivot is None:
            continue
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

# build matrix
A=[]
b0=[]
b1=[]
b2=[]
for B,coeff in stuff:
    (p,q),(r,s)=B
    row=[(p**i)*(q**j)*(r**k)*(s**l)%3 for (i,j,k,l) in monomials]
    A.append(row)
    b0.append(coeff[0])
    b1.append(coeff[1])
    b2.append(coeff[2])

sol0=solve(A,b0)
sol1=solve(A,b1)
sol2=solve(A,b2)

for name,sol in [('alpha0',sol0),('alpha1',sol1),('alpha2',sol2)]:
    exprs=[]
    for coeff,(i,j,k,l) in zip(sol,monomials):
        if coeff!=0:
            exprs.append(f"{coeff}*p^{i}q^{j}r^{k}s^{l}")
    print(name,exprs)
