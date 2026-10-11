APPROVE

### Verification of Round 1 Fixes
1. **Supporting-passage recall calculation (Fixed)**:
   - In `analyze.py` (lines 66–68), `if v and v["sup_n"]: recs.append(v["sup_hit"] / v["sup_n"])` now executes before `if norm(g[0]) in ("yes", "no"): continue`. Recall is calculated across all 950 confirmatory rows.
   - Verified in `results.md` and `report.md` Section 2: 2Wiki supporting-passage recall for `dense` and `hybrid_rerank` correctly updated to `0.71` (from `0.69` and `0.70`).

2. **$V^*$ test condition and per-query cost prose (Fixed)**:
   - In `analyze.py` (line 98), `vstar` tests `if qg > qh:` (strict inequality matching "exceeds" from `prereg-amendment-2.md` A2.4).
   - In `report.md` Section 1, prose correctly states that per-query generator cost is 1.6% (MuSiQue) and 7% (2Wiki) lower for the graph arm rather than "equal", while correctly identifying that adding the estimated query-time triple filter causes graph per-query cost to exceed hybrid ($0.00055 vs $0.00015 on MuSiQue; $0.00052 vs $0.00013 on 2Wiki), making $V^*$ undefined.

---

### Audit Summary
- **Protocol Compliance**: Confirmatory slice positions 51–1,000 ($n=950$) complies with A2.1. Decision rules for H1 (2Wiki graph-better: $+19.0$ F1, $L_{95} = +16.1 > 0$), H2 (MuSiQue TOST equivalence with margin $\pm 4$ F1: inconclusive, $90\%$ CI $[+0.9, +6.0]$), and the Kill Rule ($>+5$ F1 with $L_{95} > 0$ on both datasets: false on MuSiQue) are evaluated according to `prereg-amendment-1.md` and `prereg-amendment-2.md`. The overall proposal **ITERATE** is sound.
- **Reporting Consistency**: All numerical values in `report.md` (main table F1/CIs, mean context tokens, recall, breakdown by 2Wiki question type, pilot exploratory slices, and gate scores) match `results.md` without discrepancies.
- **Leakage Gate**: F1 on non-gold context rows ($<0.10$, excluding yes/no golds) correctly passed for all arms (MuSiQue $0.022$–$0.033$, 2Wiki $0.004$–$0.019$).
- **Disclosures**: Unmet commitments (secondary guess-prompt run A2.2, $B=2000$ consistency check A2.3) and experimental caveats (Sonnet vs gpt-4o-mini extraction, absence of real-time triple filter, restart logs) are disclosed in `deviations.md` (items 1–11) and `report.md` Sections 3 and 4.

