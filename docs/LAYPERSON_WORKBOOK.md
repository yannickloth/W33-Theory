# W33 Beginner Workbook

Hands-on companion to `docs/LAYPERSON_TEXTBOOK_GUIDE.md`.

This workbook is for learning by doing.
Each module has:

- objective
- short task
- evidence you should collect
- self-check

---

## How To Use This Workbook

1. Keep a notes file open while you work.
2. Do not skip "evidence" steps.
3. Treat each claim as valid only after you can point to script + output + test.

Recommended note format:

```text
Module:
What I ran:
What I observed:
What I still do not understand:
```

---

## Module 1: Orientation

Objective:

- know what this repo is and how to navigate it

Tasks:

1. Read `README.md`
2. Read `STANDARDIZATION.md`
3. Read `docs/LAYPERSON_ONE_PAGE_MAP.md`

Evidence to collect:

- one sentence describing the repo goal
- three file paths you now recognize and why each matters

Self-check:

- Can you explain "claim -> script -> artifact -> test" without notes?

---

## Module 2: First Reproducibility Pass

Objective:

- run one core path end-to-end

Tasks:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python scripts/w33_e8_correspondence_theorem.py
python -m pytest tests/test_e8_embedding.py -q
```

Evidence to collect:

- terminal output snippet that indicates successful script completion
- terminal output snippet that indicates passing tests

Self-check:

- Could you rerun this tomorrow without guessing commands?

---

## Module 3: Claim Audit Drill

Objective:

- separate computed facts from interpretation

Tasks:

1. Open `docs/NOVEL_CONNECTIONS_2026_02_10.md`
2. Pick one claim sentence.
3. Find:
   - script path
   - test path
   - artifact path

Use template:

- `docs/LAYPERSON_EVIDENCE_AUDIT_TEMPLATE.md`

Evidence to collect:

- one completed claim audit row

Self-check:

- Did you find all three links (`script`, `test`, `artifact`)?
  If not, label confidence lower.

---

## Module 4: Vocabulary In Context

Objective:

- build practical fluency in core terms

Tasks:

Define each in one sentence using repo context:

- `W(3,3)`
- `W33`
- `automorphism`
- `artifact`
- `smoke test`
- `UNSAT core`

Evidence to collect:

- your six one-sentence definitions

Self-check:

- Could another beginner understand your definitions without extra reading?

---

## Module 5: Evidence Strength Scoring

Objective:

- avoid over-reading strong language

Tasks:

For three claims, assign confidence score:

- `A` = reproducible now with script + test
- `B` = script present, test weak or missing
- `C` = interpretation-heavy, limited direct validation

Evidence to collect:

- table with 3 claims and scores

Self-check:

- Did you score based on reproducibility, not personal agreement?

---

## Module 6: The 30-Minute Reader Exercise

Objective:

- efficiently parse a dense research document

Tasks:

Pick any deep doc and do this order only:

1. headings
2. script paths
3. test paths
4. artifacts
5. then full prose

Evidence to collect:

- list of all script/test/artifact paths found

Self-check:

- Was understanding better than reading linearly from top to bottom?

---

## Module 7: Final Beginner Competency Test

Objective:

- confirm practical understanding of repo workflow

Tasks:

Write one page answering:

1. What is the strongest reproducible claim you verified?
2. What is one claim that still needs stronger evidence?
3. What command path would you give a new contributor first?

Evidence to collect:

- one-page summary file in your notes

Self-check:

- Can you defend each statement with file paths and command outputs?

---

## Optional Extension Modules

- Lean track: `proofs/lean/README.md`
- Heisenberg/qutrit track: `scripts/w33_heisenberg_qutrit.py` + `tests/test_heisenberg_qutrit_structure.py`
- Rigidity/certificate tracks: read relevant docs in `docs/` and apply the same audit method

---

## Completion Checklist

- [ ] I can explain repo purpose plainly.
- [ ] I ran at least one script and one test.
- [ ] I completed at least one claim audit.
- [ ] I can distinguish computed evidence from interpretation.
- [ ] I can give a newcomer a reliable first command path.
