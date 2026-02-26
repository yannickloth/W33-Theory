from scripts.ce2_global_cocycle import (
    _heisenberg_vec_maps, all_symplectic_matrices,
    apply_matrix, compute_phase, _f3_dot, _f3_omega, _f3_chi,
    _SIMPLE_FAMILY_WEIL_E_COEFF, _SIMPLE_FAMILY_WEIL_C0_COEFF, _eval_f3_poly_sw,
    matinv
)
import numpy as np

key=(0,1,15)
vec,_ = _heisenberg_vec_maps()
uc=vec[key[0]]
um=vec[key[1]]
u_o=vec[key[2]]
print('u_c',uc,'u_m',um,'u_o',u_o)
uc_u=(uc[0],uc[1])
um_u=(um[0],um[1])
u_o_u=(u_o[0],u_o[1])

d = ((um[0]-uc[0])%3,(um[1]-uc[1])%3)
print('direction',d)
A=None
for M in all_symplectic_matrices():
    if apply_matrix(M,d)==(1,0):
        A=M; break
print('chosen A',A)
B = np.array(matinv(A),dtype=int)
print('B = inv A',B)
mu = compute_phase(B)
mu[(0,0)]=0
print('mu_B',mu)
# lift
u_m_p=apply_matrix(B,(um[0],um[1]))
z_m_p = (um[2]+mu.get((um[0],um[1]),0))%3
u_o_p=apply_matrix(B,(u_o[0],u_o[1]))
z_o_p = (u_o[2]+mu.get((u_o[0],u_o[1]),0))%3
u_c_p=apply_matrix(B,(uc[0],uc[1]))
z_c_p = (uc[2]+mu.get((uc[0],uc[1]),0))%3
print('transported uc',u_c_p,z_c_p)
print('transported um',u_m_p,z_m_p)
print('transported uo',u_o_p,z_o_p)
s_p=_f3_dot(u_c_p,(1,0)); w_p=_f3_omega(u_c_p,(1,0))
print('s\'',s_p,'w\'',w_p)
seed_e=_eval_f3_poly_sw(s_p,w_p,_SIMPLE_FAMILY_WEIL_E_COEFF[1][(1,0)])
seed_c0=_eval_f3_poly_sw(s_p,w_p,_SIMPLE_FAMILY_WEIL_C0_COEFF[1][(1,0)])
print('seed_e,seed_c0',seed_e,seed_c0)
eps=_f3_chi(seed_e)
zsum_p=(z_m_p+z_o_p)%3
print('eps',eps,'zsum_p',zsum_p)
sign=eps*_f3_chi((zsum_p+seed_c0)%3)
print('reconstructed sign',sign)
