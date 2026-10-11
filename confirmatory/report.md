# #162 confirmatory analysis: GraphRAG (HippoRAG 2-lite) vs tuned hybrid, matched context budget B=1000

Protocol: `prereg.md` + `prereg-amendment-1.md` (tag `prereg-162-frozen`) + `prereg-amendment-2.md` (tag `prereg-162-amendment-2-frozen`), applied as frozen. Confirmatory sample = permutation positions 51-1000 (n=950 per dataset; the 50 pilot rows excluded, A2.1). One generation per question, Claude Sonnet 5.5, refusal prompt, B=1000. Full tables: `results.md`; code: `analyze.py`, `retrieval_rerun.py`; deviations: `../deviations.md` items 2-11.

## 1. Answer
**Proposal: ITERATE.** Not KILL (the kill rule needs graph > +5 F1 with L95 > 0 on BOTH datasets: 2Wiki yes, MuSiQue no, +3.5). Not SCALE (H2 is inconclusive; the hybrid does not close the 2Wiki gap, so "tuned hybrid is enough" is not supported). The result is the same under the original wording of H1/H2 and the amended wording.
- 2WikiMultiHopQA, graph minus tuned hybrid: **+19.0 F1** [95% CI +16.1, +22.0] (H1, amended: graph-better). Confidence high (85%) that the effect is positive and large in this setup; medium (60%) that it transfers (see caveats).
- MuSiQue, graph minus tuned hybrid: **+3.5 F1** [95% +0.4, +6.5; 90% +0.9, +6.0] (H2, margin +/-4 F1, TOST: inconclusive: the 90% CI upper bound 6.0 exceeds +4 and the 95% CI is not above +4). Confidence medium-high (75%) that graph >= hybrid by a small amount; BELOW THRESHOLD for any statement about the 2-4 F1 range.
- Tuned hybrid vs dense: MuSiQue +5.4 [+2.9, +7.9] F1 (reranker earns its keep); 2Wiki +0.9 [-0.7, +2.5] (no gain). Confidence high (80%).
- Cost (H3), as run: indexing premium $3.18 (MuSiQue, published tokens) / $4.47 (2Wiki, measured tokens, priced at the gpt-4o-mini reference) and a per-query generator cost that is 1.6% (MuSiQue) / 7% (2Wiki) lower for the graph arm (shorter contexts), so V* = 211,748 / 331,309 queries. With the estimated LLM triple filter the graph's per-query cost exceeds the hybrid's and V* is undefined. Confidence: as-run V* medium-high (70%); filter-inclusive conclusion BELOW THRESHOLD (50%): the filter was not run, its cost is an estimate and its effect on retrieval quality is untested.
- Kill/scale rule inputs: kill leg MuSiQue false, 2Wiki true; verdict confidence high (80%).

## 2. Main table (n=950, B=1000, F1 with percentile-bootstrap 95% CI)
| arm | MuSiQue F1 | 2Wiki F1 |
|---|---|---|
| no context | 0.005 [0.001, 0.009] | 0.000 |
| dense (bge-small) | 0.294 [0.267, 0.322] | 0.363 [0.333, 0.394] |
| BM25 | 0.218 [0.194, 0.244] | 0.341 [0.312, 0.371] |
| hybrid (RRF) | 0.296 [0.269, 0.324] | 0.379 [0.349, 0.410] |
| hybrid + rerank (tuned baseline) | 0.348 [0.319, 0.377] | 0.372 [0.342, 0.403] |
| HippoRAG 2-lite | 0.382 [0.353, 0.412] | 0.562 [0.532, 0.593] |

Mean context 755-923 tokens (all arms within 15% of each other on each dataset except 2Wiki graph 755 vs BM25 900: 16%, flagged; prereg sec 4 says reported not hidden). Supporting-passage recall within B: MuSiQue rerank 0.60, graph 0.61, dense 0.54; 2Wiki rerank 0.71, graph 0.87, dense 0.71 (recall over all 950 rows; the gold-string columns exclude yes/no golds). 2Wiki exploratory by type (graph minus hybrid+rerank): compositional +27.8, bridge_comparison +27.4, inference +25.0, comparison -6.5 (hybrid better; n=232).
Exploratory pilot slice (n=50, not confirmatory): graph - hybrid+rerank = -2 F1 (MuSiQue 0.351 vs 0.372), +23 F1 (2Wiki 0.661 vs 0.430) ; direction consistent with the confirmatory run.

## 3. Checks
- Integrity: 6 arms x 1000 rows per dataset equal the seeded permutation; 0 empty or error answers; F1 recomputed from answers and gold+aliases matches all rows (0 mismatches).
- Gate (amendment 1 sec 1: F1 on rows with no gold string in the context < 0.10, yes/no golds excluded): PASS for every arm (MuSiQue 0.022-0.033, 2Wiki 0.004-0.019). Positive control: the pilot measured 0.35-0.53 under the guess prompt, which this gate would fail; not re-run now (needs generation).
- Retrieval ids were not logged; re-run retrieval reproduced the generation run on 9,987 of 10,000 arm-rows (rebuilt prompt hash found in the generator cache with identical answer), the other 13 differ (ties/ordering); they do not enter the gate beyond those rows.
- Unmet commitments, disclosed: A2.2 guess-prompt leakage and A2.3 B=2000 rule not computed (`../deviations.md` 4, 5, 11). B=1000 is binding (gold string in context 37-56% MuSiQue, 59-86% 2Wiki), so every verdict is conditional on B=1000.

## 4. Caveats that matter
- Graph arm differs by dataset: MuSiQue graph from the authors' gpt-4o-mini OpenIE, 2Wiki graph from Claude Sonnet via claude -p (same family as the generator); cross-dataset comparison of graph effects is not clean. No LLM triple filter at query time (cost estimated only). bge-small instead of NV-Embed-v2 weakens dense/hybrid arms.
- Generator: one non-deterministic generation per question; 33-65% of answers are refusals, so F1 is retrieval-sufficiency-gated.
- Amendment 2 was frozen after the data existed (draft pre-data). A pre-commitment for A2.3 was written after the F1 preview was read.
- Cost inputs: MuSiQue indexing tokens are published numbers, 2Wiki measured; CPU rate $0.20/h and the triple-filter token counts are declared/estimated.

## 5. Metrics glossary
- Token F1 / EM: SQuAD v1.1 normalised token-overlap F1 = 2PR/(P+R), max over gold answer and aliases; EM = exact normalised match (Rajpurkar et al., 2016).
- Paired percentile bootstrap CI: 10,000 resamples of per-question differences, 2.5/97.5 (95%) and 5/95 (90%) percentiles (Efron 1979; Efron & Tibshirani 1993).
- Equivalence: TOST, 90% CI inside +/-margin (Schuirmann 1987); superiority/inferiority: 95% CI outside the margin.
- Supporting-passage recall = |supporting passages in context| / |supporting passages|, mean over questions (as in 2502.11371). p95 latency = 95th percentile of per-query retrieval seconds.
- V* (not a standard metric; the registered amendment-1 sec 4 summary): smallest query volume V where (graph indexing cost - hybrid indexing cost) < 10% of hybrid total cost indexing + V x per-query cost.

## 6. Audit changelog
- Round 1 (agy, content inlined): CHANGES, 2 findings, both valid and fixed: (1) supporting-passage recall had wrongly excluded yes/no-gold rows (the exclusion belongs to the gold-string columns and the gate only); recall now uses all 950 rows (2Wiki dense/rerank 0.69/0.70 -> 0.71/0.71, graph 0.87 unchanged); (2) V* 'undefined' test used >= where amendment 2 says 'exceeds'; changed to >, no number changed; prose said 'equal' per-query cost, corrected.
