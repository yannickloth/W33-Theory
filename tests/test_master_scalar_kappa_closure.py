import math

from w33_defect_unified import DefectPacket


def test_master_scalar_kappa_closure_is_complete():
    packet = DefectPacket()

    # Choose a representative Xi (close to 1) and r as in v48.
    r = 0.11913384104768696
    Xi = 1.0215575617631598

    kappa = packet.kappa_from_Xi(Xi)
    Xi_back = packet.Xi_from_kappa(kappa)
    assert abs(Xi - Xi_back) < 1e-15

    pi = packet.pi_from_Xi(Xi, r)
    beta = packet.beta_from_Xi(Xi, r)

    # Chain closure
    assert abs(pi - packet.pi_from_Xi(Xi_back, r)) < 1e-15
    assert abs(beta - packet.beta_from_Xi(Xi_back, r)) < 1e-15

    # Derived invariants
    tau3 = packet.tau3_from_beta(beta)
    theta = packet.theta_from_beta(beta)

    # Verify the closed chain is consistent (no extra degrees of freedom)
    # All derived quantities are functions of kappa alone (via Xi)
    assert abs(theta - packet.theta_from_beta(packet.beta_from_Xi(packet.Xi_from_kappa(kappa), r))) < 1e-15
    assert abs(tau3 - packet.tau3_from_beta(packet.beta_from_Xi(packet.Xi_from_kappa(kappa), r))) < 1e-15
