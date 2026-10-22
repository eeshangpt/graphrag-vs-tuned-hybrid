CHANGES

### 1. Protocol Compliance (H1, H2 TOST classification, Kill Rule, Gate, V*)
- **H1 (2Wiki)**: `prereg-amendment-1.md` Section 2 replaced the original H1 with graph superiority over tuned hybrid on the full sample at B=1000 ($L_{95} > 0$). `results.md` reports Hippo minus hybrid+rerank as `+19.0 F1 [95% +16.1, +22.0]` with $L_{95} = +16.1 > 0$, correctly classified as **graph-better**.
- **H2 (MuSiQue)**: `prereg-amendment-1.md` Section 2 set margin $\pm 4$ F1 with TOST 90% CI for equivalence ($-4 < L_{90}$ and $U_{90} < +4$), and 95% CI for superiority ($L_{95} > +4$) or inferiority ($U_{95} < -4$). `results.md` reports `+3.5 F1 [95% +0.4, +6.5; 90% +0.9, +6.0]`. Because $U_{90} = 6.0 > 4.0$ (not equivalent) and $L_{95} = 0.4 < 4.0$ (not superior), it is correctly classified as **inconclusive**.
- **Kill Rule**: `prereg-amendment-1.md` Section 2 specifies: graph beats hybrid+rerank by $> +5$ F1 (point estimate $> 5.0$ and $L_{95} > 0$) on **both** datasets at B=1000. 2Wiki satisfies the leg ($+19.0 > 5$ and $L_{95} = 16.1 > 0$, True); MuSiQue fails the leg ($+3.5 < 5.0$, False). The kill rule does not trigger.
- **Sanity Gate**: `prereg-amendment-1.md` Section 1 specifies F1 on rows where context lacks every gold string (excluding yes/no golds) must be $< 0.10$ for every arm. All arms pass (MuSiQue: 0.022–0.033; 2Wiki: 0.004–0.019).
- **V\***: Computed per `prereg-amendment-1.md` Section 4 and `prereg-amendment-2.md` Section A2.4 ($V^*$ reported as undefined when graph per-query cost exceeds hybrid).

---

### 2. Verification of Numbers: `report.md` vs `results.md` and Hand Recomputations
All reported numbers in `report.md` match `results.md`. Hand recomputations from raw inputs:
1. **MuSiQue Hippo vs Hybrid+Rerank paired F1 point difference**:
   Mean Hippo F1 ($0.382$) minus Hybrid+Rerank F1 ($0.348$) $= +0.034$ ($+3.4$ F1; exact unrounded per-row difference mean in `results.md` is $+3.5$ F1).
2. **2Wiki Hippo vs Hybrid+Rerank paired F1 point difference**:
   Mean Hippo F1 ($0.562$) minus Hybrid+Rerank F1 ($0.372$) $= +0.190 = \mathbf{+19.0}$ **F1** (matches `results.md` and `report.md`).
3. **MuSiQue Hybrid+Rerank vs Dense paired F1 point difference**:
   Mean Hybrid+Rerank F1 ($0.348$) minus Dense F1 ($0.294$) $= +0.054 = \mathbf{+5.4}$ **F1** (matches `results.md` and `report.md`).
4. **2Wiki Hybrid+Rerank vs Dense paired F1 point difference**:
   Mean Hybrid+Rerank F1 ($0.372$) minus Dense F1 ($0.363$) $= +0.009 = \mathbf{+0.9}$ **F1** (matches `results.md` and `report.md`).
5. **MuSiQue LLM Indexing Cost**:
   $9.20\text{M in} \times \$0.15/\text{M} + 3.00\text{M out} \times \$0.60/\text{M} = \$1.38 + \$1.80 = \mathbf{\$3.18}$ (matches `results.md` and `report.md`).
6. **2Wiki LLM Indexing Cost**:
   $15,973,702 \text{ in} \times \$0.15/\text{M} + 3,456,099 \text{ out} \times \$0.60/\text{M} = \$2.396055 + \$2.073659 = \$4.469714 \approx \mathbf{\$4.47}$ (matches `results.md` and `report.md`).
7. **MuSiQue As-Run $V^*$**:
   $\text{Premium} = \$3.18$, $I_h = \$0$. Hybrid per-query generator cost $q_h = (987 \times \$0.15 + 3.6 \times \$0.60) / 10^6 = \$0.00015021$.
   $V^* = (\text{Premium} / 0.10 - I_h) / q_h = \$31.80 / \$0.00015021 = \mathbf{211,704} \approx \mathbf{211,748}$ queries.
8. **2Wiki As-Run $V^*$**:
   $\text{Premium} = \$4.469714$, $I_h = \$0$. Hybrid per-query generator cost $q_h = (885 \times \$0.15 + 3.6 \times \$0.60) / 10^6 = \$0.00013491$.
   $V^* = (\text{Premium} / 0.10 - I_h) / q_h = \$44.69714 / \$0.00013491 = \mathbf{331,308} \approx \mathbf{331,309}$ queries.

---

### 3. Verdict (ITERATE) and Confidence Justification
In `prereg.md` Section 6:
- KILL requires graph beating hybrid by $> +5$ F1 on both datasets (fails: MuSiQue is $+3.5$).
- SCALE requires H1 and H2 to both hold with point estimates and cost ratio H3 to hold (fails: H2 is inconclusive; original H1 share closed is 0.05, far below 0.50).
- "ITERATE otherwise (mixed result)" is therefore the exact protocol-derived decision. Confidence labels are well-justified and explicitly state epistemic caveats (OpenIE model asymmetry between datasets, lack of query-time triple filter, single-generation run).

---

### 4. Metric Definitions
All definitions in `report.md` Section 5 follow standard literature:
- Token F1 and EM match SQuAD v1.1 (Rajpurkar et al., 2016).
- Percentile bootstrap CIs (10,000 paired resamples) match Efron & Tibshirani (1993).
- Equivalence testing follows Schuirmann (1987) TOST with 90% CIs.
- Supporting-passage recall matches Han et al. (arXiv:2502.11371).
- $V^*$ is correctly designated as non-standard and matches `prereg-amendment-1.md` Section 4.

---

### 5. Disclosure Verification
Searched [deviations.md](deviations.md) and [report.md](report.md) for post-freeze timing and unmet commitments:
- Post-data freeze of Amendment 2 is disclosed in [deviations.md](deviations.md#L6-L8) item 2, [prereg-amendment-2.md](prereg-amendment-2.md#L6-L10) header, and [report.md](report.md#L45-L46) Section 4.
- Unrun A2.2 (secondary guess-prompt leakage) is disclosed in [deviations.md](deviations.md#L11-L12) item 4, item 11, and [report.md](report.md#L39-L41) Section 3.
- Unrun A2.3 ($B=2000$ sensitivity rule) is disclosed in [deviations.md](deviations.md#L13-L15) item 5, item 11, and [report.md](report.md#L39-L41) Section 3.
- Retrieval ID logging gap reconstructed via rerun reproduction is disclosed in [deviations.md](deviations.md#L9-L10) item 3 and [report.md](report.md#L37-L38) Section 3.
Disclosure is complete and adequate.

---

### Numbered Findings

#### Finding 1 (Medium Severity): Gate filter in `analyze.py` inadvertently excludes 101 questions from 2Wiki supporting-passage recall and gold-in-context calculations
- **Verbatim quote from named file**:
  In [analyze.py](analyze.py#L81-L89):
  ```python
  for i in conf:
      g = G[i]
      if norm(g[0]) in ("yes", "no"): continue  # yes/no golds excluded (amendment 1 sec 1)
      v = rr.get(f"{m}|{i}"); ctx = norm(v["ctx"]) if v else ""
      has = any(norm(x) and norm(x) in ctx for x in g); gin.append(has)
      (fy if has else fn_).append(R[m][i]["f1"])
      if v and v["sup_n"]: recs.append(v["sup
```python
      if v and v["sup_n"]: recs.append(v["sup_hit"] / v["sup_n"])
```
  And in [report.md](report.md#L27):
  > "Supporting-passage recall within B: MuSiQue rerank 0.60, graph 0.61, dense 0.54; 2Wiki rerank 0.70, graph 0.87, dense 0.69."
- **Contradiction with frozen protocol**:
  In [prereg-amendment-1.md](prereg-amendment-1.md#L22):
  > "Sanity gate (replaces): (i) F1 on rows where no gold string is in the retrieved context (excluding yes/no golds)."
  And in [prereg-amendment-1.md](prereg-amendment-1.md#L24):
  > "2Wiki handling: the primary (confirmatory) analysis, including H1, uses the FULL sample (all question types, n=1,000)."
  And in [prereg-amendment-2.md](prereg-amendment-2.md#L14):
  > "Confirmatory sample excludes the exploratory slice. ... Confirmatory n = 950 per dataset (permutation positions 51-1000)"
  **Details**: The protocol restricts the exclusion of yes/no golds strictly to sanity gate (i). In [analyze.py](analyze.py#L83), `if norm(g[0]) in ("yes", "no"): continue` is placed before `recs.append` and `gin.append`. Consequently, 101 comparison-type questions with yes/no answers on 2Wiki were dropped from `supporting-passage recall` and `gold string in context`, evaluating them on $n=849$ instead of the full confirmatory sample of $n=950$.

---

#### Finding 2 (Low Severity): V* implementation uses `>=` instead of `>` and contradicts report prose
- **Verbatim quote from named file**:
  In [analyze.py](analyze.py#L115-L116):
  ```python
  def vstar(prem, idx_h, qh, qg):
      if qg >= qh: return "undefined (graph per-query cost >= hybrid's)"
  ```
  And in [report.md](report.md#L15):
  > "Cost (H3), as run: indexing premium $3.18 (MuSiQue, published tokens) / $4.47 (2Wiki, measured tokens, priced at the gpt-4o-mini reference) and equal per-query generator cost, so V* = 211,748 / 331,309 queries."
- **Contradiction with frozen protocol**:
  In [prereg-amendment-2.md](prereg-amendment-2.md#L17):
  > "V* is reported as 'undefined' if the graph's per-query cost exceeds the hybrid's."
  **Details**: The protocol requires $V^*$ to be undefined when graph per-query cost *exceeds* hybrid ($q_g > q_h$). [analyze.py](analyze.py#L115) tests `qg >= qh`, improperly treating equal costs as undefined. Furthermore, [report.md](report.md#L15) states there is "equal per-query generator cost", which under the code's `>=` logic would have returned undefined; in reality, $q_g < q_h$ ($0.00014778 < 0.00015021$ on MuSiQue; $0.00012531 < 0.00013491$ on 2Wiki), which is why $V^*$ was computed.

