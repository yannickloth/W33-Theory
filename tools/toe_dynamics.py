#!/usr/bin/env python3
"""
TOE dynamics core: 27-state Schläfli sector + firewall-bad edges.

This module is a *reproducible replacement* for the notebook-only "physics demos"
found in `More New Work/*v3p44..v3p46.zip`, which shipped as reports + stubs.

Model (canonical 27-line indexing):
  - "Good" edges  : Schläfli skew graph SRG(27,16,10,8) (216 edges)
  - "Bad" edges   : 27 extra edges, decomposing into 9 disjoint triangles
                   (loaded from `artifacts/firewall_bad_triads_mapping.json` in E6-id labeling)
  - Firewall knob : scales bad-edge weight by (1 - firewall_strength)

Dynamics:
  - Build a Hermitian "Hamiltonian" M with complex edge weights exp(i θ_ij)
  - Step operator U = exp(i * dt * M) via eigendecomposition (NumPy only)

Observables:
  - Triangle holonomy histogram/entropy on Schläfli triangles (Z24 bins)
  - Commutator norms ||[H, U]||_F for E6 Cartan generators H_i (true E6-on-27)
  - Optional random search for "most conserved" Cartan combination

Clock phase sources:
  - random: seeded Z6 phases per edge (toy model)
  - w33_clock: deterministic Z6 phases from `W33_holonomy_s3_gauge_bundle.zip`
    (edge potential A mod 3 + parity cocycle s mod 2 combined to k6 mod 6 via CRT),
    restricted to the canonical embedding H27 and transported to Schläfli(E6-id).
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import sys
import zipfile
from dataclasses import dataclass
from math import log
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

_CACHE_E6ID_TO_W33_H27: List[int] | None = None
_CACHE_W33_Q_EDGE_K6: Dict[Tuple[int, int], int] | None = None


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_compute_double_sixes():
    return _load_module(
        ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes"
    )


def _load_canonical_su3_solver():
    return _load_module(
        ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
        "solve_canonical_su3_gauge_and_cubic",
    )


def _ensure_schlafli_e6id_to_w33_mapping() -> Path:
    path = ROOT / "artifacts" / "schlafli_e6id_to_w33_h27.json"
    if path.exists():
        return path
    tool = _load_module(
        ROOT / "tools" / "build_schlafli_e6id_to_w33_h27_mapping.py",
        "build_schlafli_e6id_to_w33_h27_mapping",
    )
    tool.main()
    if not path.exists():
        raise RuntimeError(
            "Expected schlafli_e6id_to_w33_h27.json after generation, but file is missing"
        )
    return path


def _ensure_e6_27rep_generators() -> Path:
    out = ROOT / "artifacts" / "e6_27rep_minuscule_generators.npy"
    if out.exists():
        return out
    tool = _load_module(
        ROOT / "tools" / "build_e6_27rep_minuscule.py", "build_e6_27rep_minuscule"
    )
    tool.main([])
    if not out.exists():
        raise RuntimeError(
            "Expected E6 27-rep generators to be written but file missing"
        )
    return out


def load_e6_cartan() -> np.ndarray:
    """Return Cartan generators h as shape (6,27,27) int."""
    path = _ensure_e6_27rep_generators()
    payload = np.load(path, allow_pickle=True).item()
    h = np.array(payload["h"], dtype=int)
    if h.shape != (6, 27, 27):
        raise RuntimeError(f"Unexpected Cartan shape: {h.shape}")
    return h


def _load_reference_orbit_index() -> int:
    p = ROOT / "artifacts" / "we6_signed_action_on_27.json"
    data = _load_json(p)
    ref = data.get("reference_orbit", {})
    if not isinstance(ref, dict):
        raise RuntimeError(
            "Invalid we6_signed_action_on_27.json: missing reference_orbit"
        )
    return int(ref["orbit_index"])


def load_schlafli_graph(
    *, orbit_index: int | None = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return (skew_adj, meet_adj) for the canonical 27-orbit used by selection-rule artifacts,
    expressed in the canonical "E6-id" basis 0..26.
    """
    cds = _load_compute_double_sixes()
    canon = _load_canonical_su3_solver()
    if orbit_index is None:
        orbit_index = _load_reference_orbit_index()

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[int(orbit_index)]
    r = roots[o27]
    gram = np.rint(r @ r.T).astype(int)
    skew_pos = gram == 1
    meet_pos = gram == 0
    np.fill_diagonal(skew_pos, False)
    np.fill_diagonal(meet_pos, False)

    # Reindex orbit-local positions -> canonical E6-id using canonical_su3_gauge_and_cubic.json.
    canon_data = _load_json(ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json")
    e6_keys_27 = [tuple(int(x) for x in k) for k in canon_data["e6_keys_27_k2"]]
    key_to_e6id = {k: i for i, k in enumerate(e6_keys_27)}

    pos_to_e6id: List[int] = []
    for ridx in o27:
        kk = canon.e6_key(roots[int(ridx)])
        eid = key_to_e6id.get(tuple(int(x) for x in kk))
        if eid is None:
            raise RuntimeError("Failed to map orbit vertex to canonical E6 id")
        pos_to_e6id.append(int(eid))
    if sorted(pos_to_e6id) != list(range(27)):
        raise RuntimeError("Orbit->E6-id mapping is not a permutation")

    pos_of_e6id = [0] * 27
    for pos, eid in enumerate(pos_to_e6id):
        pos_of_e6id[eid] = pos

    skew = np.zeros((27, 27), dtype=bool)
    meet = np.zeros((27, 27), dtype=bool)
    for a in range(27):
        pa = pos_of_e6id[a]
        for b in range(27):
            pb = pos_of_e6id[b]
            skew[a, b] = bool(skew_pos[pa, pb])
            meet[a, b] = bool(meet_pos[pa, pb])
    np.fill_diagonal(skew, False)
    np.fill_diagonal(meet, False)
    return skew, meet


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schlafli_e6id_to_w33_h27() -> List[int]:
    """Return the length-27 map e6id -> W33 vertex id (in H27) for the canonical embedding."""
    global _CACHE_E6ID_TO_W33_H27
    if _CACHE_E6ID_TO_W33_H27 is not None:
        return list(_CACHE_E6ID_TO_W33_H27)
    path = _ensure_schlafli_e6id_to_w33_mapping()
    data = _load_json(path)
    maps = data.get("maps")
    if not isinstance(maps, dict):
        raise RuntimeError("Invalid schlafli_e6id_to_w33_h27.json: missing maps")
    # Prefer the bundle labeling used by the holonomy/clock bundles, but fall back to legacy.
    e6id_to_w33 = maps.get("e6id_to_w33_bundle")
    if e6id_to_w33 is None:
        e6id_to_w33 = maps.get("e6id_to_w33")
    if not (isinstance(e6id_to_w33, list) and len(e6id_to_w33) == 27):
        raise RuntimeError(
            "Invalid schlafli_e6id_to_w33_h27.json: missing e6id_to_w33 list"
        )
    out = [int(x) for x in e6id_to_w33]
    if len(set(out)) != 27:
        raise RuntimeError(
            "Invalid schlafli_e6id_to_w33_h27.json: e6id_to_w33 is not a bijection"
        )
    _CACHE_E6ID_TO_W33_H27 = list(out)
    return out


def _read_csv_from_zip(zip_path: Path, inner_path: str) -> List[Dict[str, str]]:
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(inner_path) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8")
            return list(csv.DictReader(text))


def _load_w33_q_edge_clock_k6() -> Dict[Tuple[int, int], int]:
    """
    Deterministic Z6 phase labels on the 40-vertex quotient graph Q.

    Bundle inputs (W33_holonomy_s3_gauge_bundle.zip):
      - edge_potential_A_540.csv: A(p,q) in Z3
      - edge_transport_permutations_540.csv: parity_s(p,q) in Z2

    Combine via CRT into k6 in Z6:
      k6 ≡ A (mod 3) and k6 ≡ s (mod 2)
    One closed form: k6 = (4*A + 3*s) mod 6.

    Returns dict keyed by undirected edge (min(p,q), max(p,q)).
    """
    global _CACHE_W33_Q_EDGE_K6
    if _CACHE_W33_Q_EDGE_K6 is not None:
        return dict(_CACHE_W33_Q_EDGE_K6)

    bundle = ROOT / "W33_holonomy_s3_gauge_bundle.zip"
    if not bundle.exists():
        raise RuntimeError(f"Missing required bundle: {bundle}")

    a_rows = _read_csv_from_zip(bundle, "edge_potential_A_540.csv")
    s_rows = _read_csv_from_zip(bundle, "edge_transport_permutations_540.csv")

    a_map: Dict[Tuple[int, int], int] = {}
    for r in a_rows:
        p = int(r["p"])
        q = int(r["q"])
        a = int(r["A"]) % 3
        u, v = (p, q) if p < q else (q, p)
        a_map[(u, v)] = a

    k6_map: Dict[Tuple[int, int], int] = {}
    for r in s_rows:
        p = int(r["p"])
        q = int(r["q"])
        s = int(r["parity_s"]) % 2
        u, v = (p, q) if p < q else (q, p)
        a = a_map.get((u, v))
        if a is None:
            raise RuntimeError(
                "Clock bundle mismatch: parity row missing A for an edge"
            )
        k6_map[(u, v)] = int((4 * int(a) + 3 * int(s)) % 6)

    if len(k6_map) != 540:
        raise RuntimeError(f"Expected 540 quotient edges, got {len(k6_map)}")
    _CACHE_W33_Q_EDGE_K6 = dict(k6_map)
    return k6_map


def schlafli_edge_clock_k6(i: int, j: int) -> int | None:
    """
    Return the induced Z6 edge phase label k6 for the Schläfli vertex pair (i,j),
    using the canonical embedding map into W33's H27 and the Q-edge clock bundle.
    """
    ii = int(i)
    jj = int(j)
    if ii == jj or not (0 <= ii < 27 and 0 <= jj < 27):
        raise ValueError("Expected distinct i,j in 0..26")

    e6_to_w33 = load_schlafli_e6id_to_w33_h27()
    p = int(e6_to_w33[ii])
    q = int(e6_to_w33[jj])
    k6 = _load_w33_q_edge_clock_k6().get((min(p, q), max(p, q)))
    if k6 is None:
        return None
    # Orient to match i->j: reverse orientation negates k6 in additive Z6.
    if p < q:
        return int(k6)
    return int((-int(k6)) % 6)


@dataclass(frozen=True)
class FirewallEdges:
    bad_edges: Set[Tuple[int, int]]  # undirected (u<v)
    triangles: List[Tuple[int, int, int]]  # disjoint 3-cycles, covers all 27 vertices


def load_firewall_bad_edges() -> FirewallEdges:
    """
    Load the canonical 27 bad edges (9 triangles) in **E6-id** labeling.

    Source of truth is `artifacts/firewall_bad_triads_mapping.json`, which maps the
    W33-derived firewall triangles into the same Schläfli 27 used by the selection
    rules + cubic gauge.
    """
    mapping_path = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    if not mapping_path.exists():
        tool = _load_module(
            ROOT / "tools" / "map_firewall_bad_triangles_to_cubic_triads.py",
            "map_firewall_bad_triangles_to_cubic_triads",
        )
        tool.main()
    mapping = _load_json(mapping_path)
    tri_list_raw = mapping.get("bad_triangles_Schlafli_e6id")
    if not isinstance(tri_list_raw, list) or len(tri_list_raw) != 9:
        raise RuntimeError(
            "Invalid firewall_bad_triads_mapping.json: expected 9 bad triangles"
        )
    tri_list: List[Tuple[int, int, int]] = []
    for t in tri_list_raw:
        if not (isinstance(t, list) and len(t) == 3):
            raise RuntimeError("Bad triangle entry is not length-3 list")
        a, b, c = (int(t[0]), int(t[1]), int(t[2]))
        tri_list.append((a, b, c))

    bad_edges: Set[Tuple[int, int]] = set()
    for u, v, w in tri_list:
        for x, y in ((u, v), (v, w), (w, u)):
            a_, b_ = (x, y) if x < y else (y, x)
            bad_edges.add((a_, b_))

    if len(bad_edges) != 27:
        raise RuntimeError(f"Expected 27 bad edges, got {len(bad_edges)}")

    deg = [0] * 27
    for u, v in bad_edges:
        deg[u] += 1
        deg[v] += 1
    if set(deg) != {2}:
        raise RuntimeError(f"Bad-edge degree set != {{2}}: {sorted(set(deg))}")

    if len({v for tri in tri_list for v in tri}) != 27:
        raise RuntimeError(
            "Bad-edge triangles do not cover all 27 vertices exactly once"
        )

    return FirewallEdges(bad_edges=bad_edges, triangles=tri_list)


def edge_list_from_adj(adj: np.ndarray) -> List[Tuple[int, int]]:
    n = adj.shape[0]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if bool(adj[i, j])]


def build_edge_phases(
    edges: Sequence[Tuple[int, int]],
    *,
    phase_mod: int = 6,
    seed: int = 0,
    noise_sigma: float = 0.0,
    source: str = "random",
) -> np.ndarray:
    """Return antisymmetric theta matrix (27,27) for oriented edges, 0 on non-edges."""
    if phase_mod <= 0:
        raise ValueError("phase_mod must be positive")
    if source not in {"random", "w33_clock"}:
        raise ValueError("source must be one of: random, w33_clock")
    n = 27
    theta = np.zeros((n, n), dtype=float)
    edges_sorted = sorted((int(i), int(j)) for i, j in edges)

    two_pi = float(2.0 * np.pi)
    rng = np.random.default_rng(seed)
    noises = (
        rng.normal(0.0, float(noise_sigma), size=len(edges_sorted))
        if noise_sigma
        else np.zeros(len(edges_sorted))
    )

    if source == "random":
        ks = rng.integers(0, phase_mod, size=len(edges_sorted), endpoint=False)
        for (i, j), k, eps in zip(edges_sorted, ks, noises, strict=True):
            ang = two_pi * (int(k) / phase_mod) + float(eps)
            theta[i, j] = ang
            theta[j, i] = -ang
        return theta

    # source == "w33_clock"
    if phase_mod != 6:
        raise ValueError("w33_clock source requires phase_mod=6")
    for (i, j), eps in zip(edges_sorted, noises, strict=True):
        k6 = schlafli_edge_clock_k6(i, j)
        if k6 is None:
            continue
        ang = two_pi * (int(k6) / 6) + float(eps)
        theta[i, j] = ang
        theta[j, i] = -ang

    return theta


def build_hamiltonian(
    *,
    good_adj: np.ndarray,
    bad_edges: Set[Tuple[int, int]],
    theta: np.ndarray,
    firewall_strength: float,
    good_weight: float = 1.0,
) -> np.ndarray:
    """Build Hermitian complex Hamiltonian M."""
    if good_adj.shape != (27, 27):
        raise ValueError("Expected 27x27 good_adj")
    if theta.shape != (27, 27):
        raise ValueError("Expected 27x27 theta")
    fw = float(firewall_strength)
    if not (0.0 <= fw <= 1.0):
        raise ValueError("firewall_strength must be in [0,1]")
    bad_weight = 1.0 - fw

    m = np.zeros((27, 27), dtype=np.complex128)

    # Good edges (Schläfli skew).
    good_edges = edge_list_from_adj(good_adj)
    for i, j in good_edges:
        z = complex(np.cos(theta[i, j]), np.sin(theta[i, j]))
        m[i, j] = complex(good_weight) * z
        m[j, i] = complex(good_weight) * np.conjugate(z)

    # Bad edges (firewalled).
    if bad_weight:
        for i, j in bad_edges:
            z = complex(np.cos(theta[i, j]), np.sin(theta[i, j]))
            m[i, j] += complex(bad_weight) * z
            m[j, i] += complex(bad_weight) * np.conjugate(z)

    # Numerical Hermitian symmetrization for safety.
    m = 0.5 * (m + m.conj().T)
    np.fill_diagonal(m, 0.0)
    return m


def unitary_from_hermitian(m: np.ndarray, *, dt: float) -> np.ndarray:
    """Compute U = exp(i dt M) with M Hermitian."""
    if m.shape != (27, 27):
        raise ValueError("Expected 27x27 matrix")
    evals, evecs = np.linalg.eigh(m)
    phases = np.exp(1j * float(dt) * evals)
    return (evecs * phases) @ evecs.conj().T


def frob(m: np.ndarray) -> float:
    return float(np.linalg.norm(m))


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def triangles_in_graph(adj: np.ndarray) -> List[Tuple[int, int, int]]:
    n = adj.shape[0]
    out: List[Tuple[int, int, int]] = []
    for i in range(n):
        js = np.nonzero(adj[i])[0]
        for jj in range(len(js)):
            j = int(js[jj])
            if j <= i:
                continue
            for kk in range(jj + 1, len(js)):
                k = int(js[kk])
                if k <= j:
                    continue
                if bool(adj[j, k]):
                    out.append((i, j, k))
    return out


def holonomy_histogram(
    *,
    triangles: Sequence[Tuple[int, int, int]],
    theta: np.ndarray,
    bins: int = 24,
) -> Tuple[Dict[int, int], float]:
    """Return (hist, entropy_nats) of triangle holonomy values in Z_bins."""
    two_pi = float(2.0 * np.pi)
    hist: Dict[int, int] = {i: 0 for i in range(int(bins))}
    for i, j, k in triangles:
        # oriented sum around (i->j->k->i)
        ang = float(theta[i, j] + theta[j, k] + theta[k, i])
        x = (ang / two_pi) * bins
        # nearest bin
        b = int(np.floor(x + 0.5)) % int(bins)
        hist[b] += 1
    total = sum(hist.values())
    if total == 0:
        return hist, 0.0
    ent = 0.0
    for c in hist.values():
        if c:
            p = c / total
            ent -= p * log(p)
    return hist, float(ent)


@dataclass(frozen=True)
class ChargeEval:
    coeffs: List[float]
    score: float
    comm_norm: float
    mean_drift: float
    max_drift: float
    dims: Dict[str, int]


def _normalize_coeffs(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n == 0.0:
        return v
    return v / n


def _eval_charge_drift(
    u: np.ndarray,
    h_diag: np.ndarray,
    *,
    psi0: np.ndarray,
    steps: int,
) -> Tuple[float, float]:
    psi = psi0
    exps: List[float] = []
    for _ in range(steps + 1):
        exps.append(float(np.vdot(psi, h_diag * psi).real))
        psi = u @ psi
    deltas = [abs(exps[t + 1] - exps[t]) for t in range(steps)]
    return float(np.mean(deltas)), float(np.max(deltas))


def best_conserved_charge(
    *,
    u: np.ndarray,
    cartan: np.ndarray,
    n_samples: int,
    seed: int,
    steps: int,
    comm_weight: float = 0.05,
) -> ChargeEval:
    """Random-search the best conserved Cartan combination H = Σ c_i h_i."""
    if cartan.shape != (6, 27, 27):
        raise ValueError("Expected cartan shape (6,27,27)")
    rng = np.random.default_rng(seed)

    # Use one fixed initial state for fair comparison across candidates.
    psi0 = rng.normal(size=27) + 1j * rng.normal(size=27)
    psi0 = psi0 / np.linalg.norm(psi0)

    # Pre-extract diagonals (Cartan should be diagonal in the canonical weight basis).
    cartan_diag = np.array(
        [np.real(np.diag(cartan[i])).astype(float) for i in range(6)], dtype=float
    )

    # Precompute trajectory probabilities once; drift for diagonal H depends only on |psi_t|^2.
    probs = np.zeros((int(steps) + 1, 27), dtype=float)
    psi = psi0
    probs[0] = np.abs(psi) ** 2
    for t in range(1, int(steps) + 1):
        psi = u @ psi
        probs[t] = np.abs(psi) ** 2

    abs_u2 = np.abs(u) ** 2

    best: ChargeEval | None = None
    for _ in range(int(n_samples)):
        coeffs = _normalize_coeffs(rng.normal(size=6)).astype(float)
        h_diag = coeffs @ cartan_diag  # shape (27,)

        # commutator norm: [diag(h), U] = (h_i - h_j) U_ij
        # Compute directly without forming the commutator matrix.
        diff = h_diag[:, None] - h_diag[None, :]
        comm_norm = float(np.sqrt(np.sum((diff * diff) * abs_u2)))

        exps = probs @ h_diag
        deltas = np.abs(np.diff(exps))
        mean_drift = float(np.mean(deltas)) if deltas.size else 0.0
        max_drift = float(np.max(deltas)) if deltas.size else 0.0
        score = float(mean_drift + float(comm_weight) * comm_norm)

        dims = {
            "plus": int(np.sum(h_diag > 1e-9)),
            "minus": int(np.sum(h_diag < -1e-9)),
            "zero": int(np.sum(np.abs(h_diag) <= 1e-9)),
        }
        cand = ChargeEval(
            coeffs=[float(x) for x in coeffs.tolist()],
            score=score,
            comm_norm=comm_norm,
            mean_drift=mean_drift,
            max_drift=max_drift,
            dims=dims,
        )
        if best is None or cand.score < best.score:
            best = cand

    if best is None:
        raise RuntimeError("No samples evaluated")
    return best


def run_demo(
    *,
    firewall_strength: float,
    phase_noise: float,
    seed: int,
    dt: float,
    optimize_charge: bool,
    charge_samples: int,
    charge_steps: int,
) -> Dict[str, object]:
    skew, meet = load_schlafli_graph()
    fw = load_firewall_bad_edges()

    # Sanity: bad edges must be meet edges, and disjoint from skew.
    for u, v in fw.bad_edges:
        if not bool(meet[u, v]):
            raise RuntimeError(
                "Bad edge not in meet graph (expected intersecting pair)"
            )
        if bool(skew[u, v]):
            raise RuntimeError("Bad edge unexpectedly in skew graph")

    good_edges = edge_list_from_adj(skew)
    all_edges = good_edges + sorted(fw.bad_edges)
    theta = build_edge_phases(all_edges, seed=int(seed), noise_sigma=float(phase_noise))
    m = build_hamiltonian(
        good_adj=skew,
        bad_edges=fw.bad_edges,
        theta=theta,
        firewall_strength=float(firewall_strength),
    )
    u = unitary_from_hermitian(m, dt=float(dt))

    tris = triangles_in_graph(skew)
    hist24, ent = holonomy_histogram(triangles=tris, theta=theta, bins=24)

    cartan = load_e6_cartan()
    comm_norms = [frob(comm(cartan[i].astype(np.complex128), u)) for i in range(6)]

    out: Dict[str, object] = {
        "graph": {
            "good_edges": len(good_edges),
            "bad_edges": len(fw.bad_edges),
            "bad_triangles": len(fw.triangles),
            "schlafli_triangles": len(tris),
        },
        "params": {
            "firewall_strength": float(firewall_strength),
            "phase_noise": float(phase_noise),
            "seed": int(seed),
            "dt": float(dt),
        },
        "holonomy": {
            "bins": 24,
            "hist": {str(k): int(v) for k, v in sorted(hist24.items())},
            "entropy_nats": float(ent),
        },
        "cartan": {"commutator_norms": [float(x) for x in comm_norms]},
    }

    if optimize_charge:
        best = best_conserved_charge(
            u=u,
            cartan=cartan,
            n_samples=int(charge_samples),
            seed=int(seed) + 1,
            steps=int(charge_steps),
        )
        out["best_charge"] = {
            "score": best.score,
            "comm_norm": best.comm_norm,
            "mean_drift": best.mean_drift,
            "max_drift": best.max_drift,
            "coeffs": best.coeffs,
            "dims": best.dims,
        }
    return out


def main(argv: Sequence[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--firewall-strength", type=float, default=1.0)
    p.add_argument(
        "--phase-noise",
        type=float,
        default=0.0,
        help="Gaussian noise σ added to edge phases",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--dt", type=float, default=0.35)
    p.add_argument("--optimize-charge", action="store_true")
    p.add_argument("--charge-samples", type=int, default=400)
    p.add_argument("--charge-steps", type=int, default=30)
    p.add_argument(
        "--out", type=Path, default=ROOT / "artifacts" / "toe_dynamics_demo.json"
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    data = run_demo(
        firewall_strength=float(args.firewall_strength),
        phase_noise=float(args.phase_noise),
        seed=int(args.seed),
        dt=float(args.dt),
        optimize_charge=bool(args.optimize_charge),
        charge_samples=int(args.charge_samples),
        charge_steps=int(args.charge_steps),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
