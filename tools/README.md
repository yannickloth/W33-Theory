# Tools Directory

Analysis and verification tools for the W33 Theory of Everything project.

## Categories

### Spectral Analysis
- `spectral_connections.py` - W33/Triangle graph/E8 spectral cascade
- `spectral_eigenvector_analysis.py` - Eigenvector structure analysis

### E8/D4 Root Systems
- `d4_*.py` - D4 root system and triality
- `e8_*.py` - E8 root system analysis and partitions

### H27/Jordan Algebra
- `h27_*.py` - H27 structure, Heisenberg model, Jordan algebra

### H12 Structure
- `h12_*.py` - H12 neighborhood analysis

### Witting Polytope / PG(3,2)
- `witting_*.py` - Witting polytope and projective geometry analysis

### W33 Core
- `w33_*.py` - W33 graph construction and analysis

### Bundle Builders
- `build_*.py` - Generate data bundles for physics predictions

### Lift / φ Analysis
- `compute_phi_lift_subgroup.py` - classify stabiliser of canonical edge→root bijection
- `analyze_lift_subgroup.py` - summarise lift subgroup data and orbit structure
- `search_phi.py` - random heuristic search for improved bijections
- `compute_phi_sign_gauge.py` - solve sign-gauge equations to maximise lift group
- `extract_gl23_module.py` - build GF(3) matrices for GL(2,3) representation inside E8

### WE6 / E₆×A₂ decomposition
- `verify_orbit_decompositions.py` - confirm transitivity/intransitivity of 120 actions
- `classify_e8_roots_dotpair.py` - compute dot-pair classes used in the E6×A2 split
- `classify_w33_edges_by_rootclass.py` - tag W33 edges according to E8 root classes

### Representation theory / meatAxe
- `meataxe_decompose.py` - simple GF(3) MeatAxe-style module decomposition, used for GL(2,3) and other small modules

### Physics demonstrations
- `sector_physics.py` - toy CKM matrix and sector-specific invariant counts

### Verification
- `audit_*.py`, `verify_*.py` - Consistency checks
- `inspect_*.py` - Data inspection utilities
