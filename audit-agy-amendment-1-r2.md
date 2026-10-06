# agy audit 2 of prereg amendment 1 (#162)
Auditor: gemini-3.1-pro-high via bin/agy-run, 2026-10-06 10:40 IST, anonymized copy.

VERDICT: CHANGES

The round-1 findings (2Wiki subsetting, SQuAD normalizer, and mixed alpha levels) have been properly addressed. However, clarifying the CIs introduced a definitional inconsistency, and the sanity gate has a string-matching edge case.

1. **High: Inconsistent definitions of statistical superiority**
   - **Location:** Section 2 (Amended H2 vs. Kill rule).
   - **Issue:** The amendment uses two conflicting frameworks for what it means to "beat" a baseline by a margin. H2 rigorously defines superiority by requiring the confidence interval lower bound to exceed the margin (`L95 > +4`). In contrast, the Kill rule defines beating the baseline by 5 points using a hybrid test (`point estimate > +5 and L95 > 0`). 
   - **Fix:** Unify the definition of superiority across the document. To match the strict margin testing of H2, update the Kill rule to require `L95 > +5`. 

2. **Medium: Leakage sanity gate is vulnerable to MuSiQue aliases**
   - **Location:** Section 1 (Sanity gate).
   - **Issue:** The leakage gate isolates rows "where the gold string is not in the retrieved context." Because MuSiQue uses `answer_aliases`, if the primary answer string is absent but a valid alias is present in the context, the model can correctly extract the alias. This would register as a false positive for "memory leakage" and artificially inflate the no-context F1 score.
   - **Fix:** Explicitly state that for MuSiQue, the sanity gate exclusion check must verify that *none* of the gold answer strings (primary or aliases) are present in the retrieved context.


## CoS response
- Finding 2 (aliases): accepted.
- Finding 1 (kill rule): disputed. The kill rule is the registered one from prereg.md; tightening it after the pilot is itself a post-hoc change (round-1 finding 1). Keep it, label it as a pre-registered practical-significance rule, distinct from H2's margin test.
