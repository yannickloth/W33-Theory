# W33 Beginner Concept Map

This map compresses the repository into a single concept flow.

Use it as a navigation aid, not as a proof.

---

## Concept Flow (High Level)

1. Start object:
   - finite geometry `W(3,3)`
2. Graph representation:
   - point graph `W33`
3. Computed invariants:
   - counts, spectra, homology, symmetry structure
4. Comparison targets:
   - exceptional algebra structures (`E6`, `E7`, `E8`)
5. Evidence mechanism:
   - script execution + tests + artifacts
6. Interpretation layer:
   - potential physical-structure relevance

---

## Map By Repository Components

| Layer | Question | Where To Look |
|---|---|---|
| Definitions | What objects are we talking about? | `STANDARDIZATION.md` |
| Entry | What should I read first? | `README.md`, `docs/LAYPERSON_ONE_PAGE_MAP.md` |
| Beginner depth | How do I understand this without physics background? | `docs/LAYPERSON_TEXTBOOK_GUIDE.md` |
| Hands-on learning | How do I practice evaluating claims? | `docs/LAYPERSON_WORKBOOK.md` |
| Evidence auditing | How do I score claim strength? | `docs/LAYPERSON_EVIDENCE_AUDIT_TEMPLATE.md` |
| Technical tracks | Where are theorem pipelines documented? | `docs/INDEX.md` |
| Execution | Which files compute results? | `scripts/`, `tools/` |
| Validation | Which files test the computations? | `tests/` |
| Outputs | Where is machine output recorded? | `artifacts/`, `reports/` |

---

## Reading Lenses

Use one lens at a time.

### Lens A: Beginner understanding

- read conceptual docs first
- run only starter commands

### Lens B: Reproducibility

- focus on claim -> script -> test -> artifact chain

### Lens C: Research interpretation

- only after Lens A + B
- keep interpretation separate from raw computation

---

## Fast Self-Test

If you can answer these, you are oriented:

1. What is `W33` in one sentence?
2. Where do canonical definitions live?
3. How do you verify one claim without reading all docs?
4. What is the difference between computed verification and experimental validation?
