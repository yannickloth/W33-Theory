# V27 (Pilot) — Bucketed δL8 → l9 (Stats Only)

**Date**: 2026-03-05  
**Status**: COMPLETE — exact on first 5,000,000 l8 entries (no full JSONL written)

## What this pilot is

This runs the bucketed out-of-core pipeline for

- `l9 = -δ l8`

but only on the first **5,000,000** rows of the full l8 table, and with `--no-write-jsonl` to keep disk usage small. The goal is to estimate scale and confirm qualitative patterns (support, multi-term behavior, coefficient growth).

## Inputs

- l8 table: `V26_output_v13_full/l8_patch_octuples_full.jsonl` (full file; pilot reads first 5,000,000 lines)
- Structure constants / metadata / firewall couplings as in V26/V25

## Pilot results (first 5,000,000 l8 rows)

From `V27_output_pilot_5M_stats/v27_bucketed_deltaL8_to_l9_report.json`:

- records read: **118,593,782**
- unique 9-tuples seen: **86,610,785**
- **nonzero l9 entries**: **86,320,530**
  - single-term: **82,012,914**
  - multi-term: **4,307,616** (4.99%)
- **support size**: **86** (full `g0 = e6 ⊕ sl3` component)
- multi-term sizes observed: 2–8 terms (dominated by 8-term and 7-term Cartan vectors)
- **max |coeff| observed** (any component): **149**

## Outlook for full l9

Even on this small pilot, l9 is already ~**17.3× larger** than the input l8 slice, which strongly suggests that a full exact l9 table would be **billions of entries** and far too large to store as JSONL on this machine. If we go further, the practical options are:

1) compute **stats-only** exactly (no table), or  
2) compute and store a **compressed/binary** representation, or  
3) work from **sampling + symmetry/orbit compression**.

