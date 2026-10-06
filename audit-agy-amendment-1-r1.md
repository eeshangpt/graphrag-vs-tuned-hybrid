# agy audit 1 of prereg amendment 1 (#162)
Auditor: gemini-3.1-pro-high via bin/agy-run, 2026-10-06 10:37 IST, on an anonymized copy (bin/anonymize --check passed).

VERDICT: CHANGES

1. **(High) P-hacking via post-hoc subsetting**
   - **Location:** Sec 1 (2Wiki handling) and Sec 2 (Amended H1).
   - **Issue:** Excluding `comparison` and `bridge_comparison` question types from H1 testing *after* seeing pilot data is a textbook forking path that artificially restricts the hypothesis to a subset favorable to one outcome.
   - **Fix:** Evaluate H1 on the full 1,000-question 2Wiki sample to maintain the original scope. Report the subset breakdown (compositional + inference) strictly as exploratory/secondary analysis.

2. **(High) Invented non-standard metric**
   - **Location:** Sec 5 (Scorer).
   - **Issue:** Removing all whitespace for a "secondary match" (e.g., treating "5 a.m." and "5am" as identical by stripping spaces) creates an invented, non-standard metric. SQuAD/MuSiQue EM/token-F1 do not strip all whitespace.
   - **Fix:** Remove the whitespace-stripping secondary match. Evaluate solely using the standard SQuAD normalizer for EM and token F1.

3. **(Medium) Mismatched confidence intervals in the Kill Rule**
   - **Location:** Sec 2 (Kill rule).
   - **Issue:** The rule mixes different alpha levels. It requires a 95% CI lower bound > 0 (alpha=0.025 one-sided) but also requires the H2 "graph-better" outcome, which is defined using a 90% CI (L > +4, alpha=0.05 one-sided). 
   - **Fix:** Standardize the statistical thresholds. Redefine the MuSiQue condition within the kill rule to use a 95% CI to match the other criteria, ensuring consistent statistical rigor.

