
## musique
integrity: 6 arms x 1000 ids = permutation; F1 recomputed from ans+gold(+aliases) mismatches: 0

| arm | n | F1 [95% CI] | EM | 'unanswerable' share | mean ctx tok | retrieval s/q median (p95) |
|---|---|---|---|---|---|---|
| nocontext | 950 | 0.005 [0.001, 0.009] | 0.004 | 0.99 | 0 | n/a |
| dense | 950 | 0.294 [0.267, 0.322] | 0.240 | 0.59 | 922 | 0.057 (0.114) |
| bm25 | 950 | 0.218 [0.194, 0.244] | 0.179 | 0.65 | 923 | 0.000 (0.000) |
| hybrid | 950 | 0.296 [0.269, 0.324] | 0.240 | 0.56 | 922 | 0.045 (0.114) |
| hybrid_rerank | 950 | 0.348 [0.319, 0.377] | 0.288 | 0.50 | 920 | 3.471 (4.605) |
| hippo | 950 | 0.382 [0.353, 0.412] | 0.331 | 0.48 | 903 | lookup (batched; mean 0.18 s/q) |

Exploratory slice (positions 1-50, n=50; used for design, NOT confirmatory): F1 nocontext 0.000, dense 0.228, bm25 0.274, hybrid 0.231, hybrid_rerank 0.372, hippo 0.351

Paired differences on the 950 (F1 points; percentile bootstrap 10,000, seed 0):
- bm25 - dense: -7.6 F1 [95% -10.4, -4.8; 90% -10.0, -5.3]
- hybrid - dense: +0.2 F1 [95% -2.3, +2.7; 90% -1.9, +2.3]
- hybrid_rerank - dense: +5.4 F1 [95% +2.9, +7.9; 90% +3.3, +7.4]
- hippo - dense: +8.8 F1 [95% +6.1, +11.6; 90% +6.6, +11.1]
- dense - hybrid_rerank: -5.4 F1 [95% -7.9, -2.9; 90% -7.4, -3.3]
- bm25 - hybrid_rerank: -12.9 F1 [95% -15.7, -10.3; 90% -15.2, -10.7]
- hybrid - hybrid_rerank: -5.2 F1 [95% -7.7, -2.6; 90% -7.3, -3.0]
- hippo - hybrid_rerank: +3.5 F1 [95% +0.4, +6.5; 90% +0.9, +6.0]

Graph (HippoRAG 2-lite) minus tuned hybrid (hybrid+rerank): +3.5 F1 [95% +0.4, +6.5; 90% +0.9, +6.0]; paired SD 0.473
H2 (amendment 1 sec 2, margin +/-4 F1; TOST 90% CI): **inconclusive**
Kill-rule leg (point > +5 F1 and L95 > 0): False
Superseded original forms (descriptive only): graph - hybrid+rerank = +3.5 F1; share of the dense-to-graph gap closed by the hybrid = 0.61 (original H1 asked >= 0.5; gap +8.8 F1)

Retrieval re-run reproduces the generation run (rebuilt prompt hash exists in generator cache with identical answer; ctx token count equal): {'cache_hit': 4989, 'ans_same': 4989, 'tok_same': 4991} of 5000 arm-rows

| arm | supporting-passage recall (all 950) | gold string in context (excl. yes/no golds) | F1 on rows with no gold string in ctx (n) [GATE < 0.10] | F1 on rows with gold in ctx |
|---|---|---|---|---|
| nocontext | n/a | 0.00 | 0.005 (950) PASS | nan (0) |
| dense | 0.54 | 0.45 | 0.029 (524) PASS | 0.621 (426) |
| bm25 | 0.47 | 0.37 | 0.022 (597) PASS | 0.550 (353) |
| hybrid | 0.56 | 0.45 | 0.033 (522) PASS | 0.617 (428) |
| hybrid_rerank | 0.60 | 0.52 | 0.028 (453) PASS | 0.639 (497) |
| hippo | 0.61 | 0.56 | 0.024 (421) PASS | 0.668 (529) |

H3 cost inputs (musique): reference price $0.15/$0.6 per M in/out tokens; generator prompt tokens/answer tokens per query: hybrid+rerank 987/3.6, graph 970/3.8
graph indexing LLM tokens 9.20M in / 3.00M out (published, 2502.14802 Table 12 (Llama-3.3-70B)) = $3.18 at the reference price; CPU: embedding 597 s (shared), graph build 2173 s (pilot-measured); retrieval s/q hybrid+rerank 3.47 (CPU reranker), graph 0.18
estimated LLM triple-filter cost per graph query (not run; ESTIMATE from the paper's filter prompt): 2424 in / 60 out tokens = $0.00040

| scenario | indexing premium (graph - hybrid) $ | hybrid per-query $ | graph per-query $ | V* (graph premium < 10% of hybrid total) | graph/hybrid total cost at V=1000 |
|---|---|---|---|---|---|
| as run: no filter, local compute $0 | 3.18 | 0.00015 | 0.00015 | 211,748 | 22.2x |
| A2.4a: + estimated LLM triple filter | 3.18 | 0.00015 | 0.00055 | undefined (graph per-query cost exceeds hybrid's) | 24.8x |
| A2.4b: local compute priced at $0.20/h (declared), no filter | 3.30 | 0.00034 | 0.00016 | 96,219 | 9.3x |
| A2.4a+b: filter and CPU priced | 3.30 | 0.00034 | 0.00056 | undefined (graph per-query cost exceeds hybrid's) | 10.4x |

## 2wiki
integrity: 6 arms x 1000 ids = permutation; F1 recomputed from ans+gold(+aliases) mismatches: 0

| arm | n | F1 [95% CI] | EM | 'unanswerable' share | mean ctx tok | retrieval s/q median (p95) |
|---|---|---|---|---|---|---|
| nocontext | 950 | 0.000 [0.000, 0.000] | 0.000 | 1.00 | 0 | n/a |
| dense | 950 | 0.363 [0.333, 0.394] | 0.341 | 0.58 | 851 | 0.048 (0.113) |
| bm25 | 950 | 0.341 [0.312, 0.371] | 0.319 | 0.59 | 900 | 0.000 (0.000) |
| hybrid | 950 | 0.379 [0.349, 0.410] | 0.355 | 0.56 | 866 | 0.052 (0.114) |
| hybrid_rerank | 950 | 0.372 [0.342, 0.403] | 0.344 | 0.57 | 821 | 4.616 (5.032) |
| hippo | 950 | 0.562 [0.532, 0.593] | 0.509 | 0.33 | 755 | lookup (batched; mean 0.12 s/q) |

Exploratory slice (positions 1-50, n=50; used for design, NOT confirmatory): F1 nocontext 0.000, dense 0.390, bm25 0.390, hybrid 0.370, hybrid_rerank 0.430, hippo 0.661

Paired differences on the 950 (F1 points; percentile bootstrap 10,000, seed 0):
- bm25 - dense: -2.2 F1 [95% -4.2, -0.2; 90% -3.9, -0.5]
- hybrid - dense: +1.6 F1 [95% +0.0, +3.3; 90% +0.3, +3.0]
- hybrid_rerank - dense: +0.9 F1 [95% -0.7, +2.5; 90% -0.5, +2.3]
- hippo - dense: +19.9 F1 [95% +17.0, +22.9; 90% +17.5, +22.4]
- dense - hybrid_rerank: -0.9 F1 [95% -2.5, +0.7; 90% -2.3, +0.5]
- bm25 - hybrid_rerank: -3.1 F1 [95% -5.1, -1.1; 90% -4.8, -1.3]
- hybrid - hybrid_rerank: +0.7 F1 [95% -1.1, +2.6; 90% -0.8, +2.3]
- hippo - hybrid_rerank: +19.0 F1 [95% +16.1, +22.0; 90% +16.6, +21.5]

Graph (HippoRAG 2-lite) minus tuned hybrid (hybrid+rerank): +19.0 F1 [95% +16.1, +22.0; 90% +16.6, +21.5]; paired SD 0.461
H1 (amended: graph superior to tuned hybrid on the full sample, L95 > 0): **graph-better**
Kill-rule leg (point > +5 F1 and L95 > 0): True
Superseded original forms (descriptive only): graph - hybrid+rerank = +19.0 F1; share of the dense-to-graph gap closed by the hybrid = 0.05 (original H1 asked >= 0.5; gap +19.9 F1)

Retrieval re-run reproduces the generation run (rebuilt prompt hash exists in generator cache with identical answer; ctx token count equal): {'cache_hit': 4998, 'ans_same': 4998, 'tok_same': 4998} of 5000 arm-rows

| arm | supporting-passage recall (all 950) | gold string in context (excl. yes/no golds) | F1 on rows with no gold string in ctx (n) [GATE < 0.10] | F1 on rows with gold in ctx |
|---|---|---|---|---|
| nocontext | n/a | 0.00 | 0.000 (849) PASS | nan (0) |
| dense | 0.71 | 0.63 | 0.007 (316) PASS | 0.509 (533) |
| bm25 | 0.68 | 0.59 | 0.013 (349) PASS | 0.503 (500) |
| hybrid | 0.71 | 0.63 | 0.007 (314) PASS | 0.524 (535) |
| hybrid_rerank | 0.71 | 0.62 | 0.019 (319) PASS | 0.514 (530) |
| hippo | 0.87 | 0.86 | 0.004 (115) PASS | 0.630 (734) |

Exploratory (A1 sec 1): by 2Wiki question type on the 950; graph minus hybrid+rerank and arm F1
- bridge_comparison (n=220): dense 0.08, hybrid+rerank 0.09, graph 0.36; graph-hybrid +27.4 F1 [95% +20.9, +34.2; 90% +21.8, +33.2]
- comparison (n=232): dense 0.94, hybrid+rerank 0.96, graph 0.89; graph-hybrid -6.5 F1 [95% -10.3, -3.0; 90% -9.5, -3.4]
- compositional (n=393): dense 0.16, hybrid+rerank 0.17, graph 0.45; graph-hybrid +27.8 F1 [95% +23.3, +32.4; 90% +24.1, +31.6]
- inference (n=105): dense 0.45, hybrid+rerank 0.42, graph 0.67; graph-hybrid +25.0 F1 [95% +15.9, +34.5; 90% +17.3, +32.9]

H3 cost inputs (2wiki): reference price $0.15/$0.6 per M in/out tokens; generator prompt tokens/answer tokens per query: hybrid+rerank 885/3.6, graph 819/4.1
graph indexing LLM tokens 15.97M in / 3.46M out (measured here, Claude Sonnet via claude -p (06-2wiki-openie.log), priced at the reference table) = $4.47 at the reference price; CPU: embedding 376 s (shared), graph build 807 s (confirmatory run); retrieval s/q hybrid+rerank 4.42 (CPU reranker), graph 0.12
estimated LLM triple-filter cost per graph query (not run; ESTIMATE from the paper's filter prompt): 2424 in / 60 out tokens = $0.00040

| scenario | indexing premium (graph - hybrid) $ | hybrid per-query $ | graph per-query $ | V* (graph premium < 10% of hybrid total) | graph/hybrid total cost at V=1000 |
|---|---|---|---|---|---|
| as run: no filter, local compute $0 | 4.47 | 0.00013 | 0.00013 | 331,309 | 34.1x |
| A2.4a: + estimated LLM triple filter | 4.47 | 0.00013 | 0.00052 | undefined (graph per-query cost exceeds hybrid's) | 37.0x |
| A2.4b: local compute priced at $0.20/h (declared), no filter | 4.51 | 0.00038 | 0.00013 | 118,554 | 11.6x |
| A2.4a+b: filter and CPU priced | 4.51 | 0.00038 | 0.00053 | undefined (graph per-query cost exceeds hybrid's) | 12.6x |