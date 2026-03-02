# Pillar 100: Unified Algebraic Summary

## The Tomotope Structure

{
  "pillar_100_unified_summary": true,
  "tomotope": {
    "rank": 4,
    "flags": 192,
    "monodromy_order": 18432,
    "automorphism_order": 96,
    "full_symmetry_order": 1769472
  },
  "regular_subgroup_N": {
    "order": 192,
    "centre_trivial": true,
    "num_generators": 2,
    "generator_orders": [
      4,
      6
    ],
    "derived_order": 48,
    "abelianisation_order": 4,
    "abelianisation_type": "Z_2 x Z_2",
    "sylow2_order": 64,
    "sylow2_normal": false,
    "sylow2_num_conjugates": 3,
    "sylow2_distribution": {
      "1": 1,
      "2": 27,
      "4": 36
    },
    "order3_subgroup_order": 48,
    "order3_subgroup_normal": true,
    "order3_equals_derived": true,
    "num_conjugacy_classes": 14,
    "class_sizes": [
      1,
      3,
      4,
      6,
      6,
      12,
      12,
      12,
      12,
      12,
      24,
      24,
      32,
      32
    ],
    "block_kernel_order": 2,
    "num_involutions": 43,
    "num_squares": 48,
    "num_cubes": 128
  },
  "transport_law": {
    "total_edges": 270,
    "num_generators": 5,
    "generators": [
      "g2",
      "g3",
      "g5",
      "g8",
      "g9"
    ],
    "involution_generators": [
      "g8",
      "g9"
    ],
    "order3_generators": [
      "g2",
      "g3",
      "g5"
    ],
    "involution_fixed_points": {
      "g8": 3,
      "g9": 3
    },
    "affine_matrices_all_det_1": true,
    "num_affine_matrices": 3,
    "cocycle_global": {
      "0": 201,
      "1": 33,
      "2": 36
    },
    "num_orient_strata": 10
  },
  "N_transport_connection": {
    "qid_preserving_count": 54,
    "num_blocks": 48,
    "flags_per_block": 4,
    "blocks_to_qids_ratio": 1.7778,
    "derived_transitive_on_blocks": true,
    "derived_num_block_orbits": 1
  },
  "clifford_embedding": {
    "N_embeds_in_Spin_dim": 4,
    "Spin4_F3_order": 576,
    "index_of_N": 3,
    "Cl2_F3_dimension": 4,
    "generators_anticommute": true
  },
  "direct_product": {
    "Gamma_order": 18432,
    "H_order": 96,
    "closure_order": 1769472,
    "is_direct_product": true
  },
  "identification_candidates": [
    "N could be (Z_4 x Z_4 x Z_3) : Z_4 or similar semidirect product",
    "14 conjugacy classes with class equation summing to 192",
    "|N/[N,N]| = 4 = Z_2 x Z_2 means two independent commuting involutions modulo [N,N]",
    "Sylow-2 (order 64) not normal => N is not a 2-group extension by Z_3",
    "[N,N] = order-3 closure = squares => strong constraint on N's isomorphism type",
    "N embeds in Spin(4, F_3) with index 3 => N is almost all of Spin(4, F_3)"
  ]
}