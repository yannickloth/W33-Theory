# Follow-up: Medium exhaustive minimal-certificate censuses

This follow-up PR will contain medium exhaustive runs for both `hessian` and `agl`
candidate spaces along with deterministic classified artifacts and a short
markdown summary of results.

Planned contents:

- artifacts/e6_f3_trilinear_min_cert_exhaustive_wrapper_hessian_full.json
- artifacts/e6_f3_trilinear_min_cert_exhaustive_wrapper_agl_full.json
- artifacts/*_with_geotypes.json (classified outputs)
- docs/MIN_CERT_CENSUS_[DATE].md (summary + figures)

Planned limits & knobs:

- `--max-exact-solutions` (cap exact solutions to avoid runaway runs)
- `--time-limit-sec` (total seconds to allow per candidate space)

Run plan (dry-run):

    py -3 tools/run_min_cert_census.py --dry-run --out-dir artifacts

Bounded run example (execute):

    py -3 tools/run_min_cert_census.py --execute --candidate-spaces hessian agl --max-exact-solutions 500 --time-limit-sec 600 --out-dir artifacts

Notes:
- This PR is intentionally separate from the stabilization PR to keep review focused
  and avoid mixing heavy artifacts with code-quality changes.
- Once the runs complete, I will add classified artifacts, the MD summary, and
  optional figures to this branch and link the PR back to the stabilization PR.
