# Declared deviations (post-freeze, prereg-162-frozen)

Logged as they arise; the frozen files are not edited. Each item is reported with the results.

1. 2026-10-06: 2Wiki graph arm OpenIE is extracted with Claude Sonnet via `claude -p` (HippoRAG 2's verbatim NER and triple prompts; one-shot example embedded as text, no multi-turn few-shot). The shipped MuSiQue OpenIE was extracted by the HippoRAG 2 authors with gpt-4o-mini. Consequence: graph quality may differ between datasets for reasons other than the dataset; H1 (2Wiki) and H2 (MuSiQue) graph results are not directly comparable across datasets. Build: ~/research/graphrag-hybrid branch feat/2wiki-graph (6959afd); 50-passage sample $0.686 notional, 0 failures; agy audit APPROVE r1.
