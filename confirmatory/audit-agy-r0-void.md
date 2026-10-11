CHANGES

### Finding 1: Post-Data Freeze Protocol Amendment (Invalidating Confirmatory Status)
- **Severity**: Critical
- **Evidence**: `prereg-amendment-2.md` (amendment timing vs. data collection timestamp); `deviations.md` (undisclosed timing relative to data unblinding).
- **Audit Detail**: Amendment 2 was drafted and frozen post-data collection/unblinding. In confirmatory empirical evaluation, modifying protocol definitions, analysis subsets, or decision criteria after inspecting data violates the confirmatory boundary and constitutes post-hoc alteration (HARKing / p-hacking). Any analysis modified or introduced under Amendment 2 must be classified as exploratory rather than confirmatory.

---

### Finding 2: Unrun Planned Confirmatory Analyses (Selective Outcome Reporting)
- **Severity**: Critical
- **Evidence**: `prereg-amendment-2.md` (specifications for analyses A2.2 and A2.3); `deviations.md`; `report.md`.
- **Audit Detail**: Protocol analyses A2.2 and A2.3 were planned and registered as part of the confirmatory battery but were left unrun. Omitting planned analyses without a pre-registered early stopping rule or explicit formal disclosure of failure constitutes selective reporting bias. The final report fails to account for how the omitted results of A2.2 and A2.3 would impact the overall assessment.

---

### Finding 3: Unjustified Decision Verdict (ITERATE) and Inflated Confidence Labels
- **Severity**: Critical
- **Evidence**: `report.md` (Verdict section: "ITERATE", confidence ratings); `prereg.md` (Kill rule and Gate criteria specifications).
- **Audit Detail**: The pre-registered protocol specifies strict Gate criteria and a Kill rule tied to target performance metric $V^*$ over the full confirmatory cohort ($n=950$). The empirical results failed to satisfy the pre-registered Gate/Kill boundary for continuation. Overriding the pre-registered Kill rule to declare an "ITERATE" verdict represents an unprincipled post-hoc modification of decision rules. Furthermore, assigning high or moderate confidence labels is unjustified given the presence of unrun analyses, post-data freeze amendments, and unfulfilled gate criteria.

---

### Finding 4: Silent Deviations from Frozen Protocol Sample Size ($n=950$), CIs, and H1/H2 Classification
- **Severity**: Major
- **Evidence**: `analyze.py`; `report.md`; `prereg.md` (Protocol specifications for $n=950$, Confidence Intervals, and primary H1 vs. secondary H2).
- **Audit Detail**: The confirmatory analysis fails to adhere strictly to the frozen protocol:
  1. **Sample Size ($n$)**: Dropping invalid or empty retrieval returns resulted in an effective sample size $n < 950$ without pre-specified exclusion rules, biasing the denominator.
  2. **Confidence Intervals**: CIs reported in `report.md` and calculated in `analyze.py` deviate from the pre-registered estimation method (e.g., standard normal asymptotics applied without accounting for paired/clustered variance across benchmark query distributions).
  3. **Hypothesis Classification**: Boundaries between primary confirmatory hypothesis H1 and secondary hypothesis H2 were blurred in `report.md`, treating secondary/exploratory signals as confirmatory support for hybrid retriever parity.

---

### Finding 5: Discrepancies and Inconsistencies Between `report.md` and `results.md`
- **Severity**: Major
- **Evidence**: `report.md` (Summary tables and narrative metrics) vs. `results.md` (Underlying raw run numbers).
- **Audit Detail**: Multiple numerical inconsistencies exist between `results.md` and the synthesized narrative in `report.md`. Point estimates in `report.md` reflect optimistic rounding and selective extraction from subset runs, masking variance and underperforming slices documented in `results.md`. Summary tables fail to reconcile discrepancy margins against raw logged outputs.

---

### Finding 6: Code Errors in Metric Definitions and Retrieval Aggregation in `analyze.py`
- **Severity**: Major
- **Evidence**: `analyze.py` (Metric computation functions, $V^*$ calculation, handling of zero-retrieval / empty returns); `retrieval_rerun.py`.
- **Audit Detail**: The metric computation logic in `analyze.py` exhibits key implementation flaws:
  1. **Zero-Division / Empty Result Handling**: Queries where the retriever fails to return relevant candidate chunks are excluded or improperly masked rather than assigned a score of 0.0, artificially inflating mean recall/precision and the target metric $V^*$.
  2. **Non-Standard Metric Formulation**: The implementation of rank-weighted evaluation deviates from standard IR metric formulations specified in `prereg.md`, introducing bias favoring the candidate retriever over the baseline.

---

### Finding 7: Incomplete and Non-Transparent Disclosure in `deviations.md`
- **Severity**: Major
- **Evidence**: `deviations.md` (Omission of Amendment 2 timing context and impact of unexecuted A2.2/A2.3).
- **Audit Detail**: `deviations.md` does not fulfill the requirement of full disclosure. It omits explicit documentation that Amendment 2 was drafted after viewing data trends, fails to disclose the non-execution of analyses A2.2 and A2.3, and fails to document the departure from the pre-registered kill threshold that should have triggered a termination rather than an "ITERATE" verdict.

