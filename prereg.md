# Pre-registration: GraphRAG vs a tuned hybrid baseline at matched context budget, indexing cost included

Topic 5 of #139. Experiment issue: https://github.com/PixnetTechnosys/cos-os/issues/162. Learnings: #151.
Registered 2026-10-05, BEFORE any pilot number was produced (commit timestamp of this file is the proof). Harness: `~/research/graphrag-hybrid/` (local git, not pushed).
Sources read in full for this design: arXiv 2502.11371 (Han et al.; Appendix M token-matched RAG, Tables 31-35; rerank setup in Appendix F), arXiv 2502.14802 (HippoRAG 2; Sec 4.4, Appendix G, Table 12). Confidence in the design: medium; the pilot only tests the pipeline.

## 1. Question and hypotheses
Q: When every method hands the same generator the same number of context tokens, how much of a graph method's edge over a plain dense retriever remains once the vector side is a tuned hybrid (BM25 + dense + RRF + cross-encoder), and what does each method cost in total, indexing included?

- H1 (2Wiki): the tuned hybrid closes at least half of the F1 gap between dense-only and HippoRAG 2 (published gap vs NV-Embed-v2: +9.5 F1, Table 2 of 2502.11371's sibling paper 2502.14802).
- H2 (MuSiQue): the tuned hybrid is within 2 F1 of HippoRAG 2 (published gap +2.9).
- H3 (cost): per 1,000 queries including amortised indexing, the tuned hybrid costs at least 10x fewer tokens-or-dollars than either graph method.
- Null/alternative: HippoRAG 2 beats the tuned hybrid by more than 5 F1 on both sets at matched budget.

## 2. Data (public, seeded)
- Source: HuggingFace `osunlp/HippoRAG_2`, files `musique.json`, `musique_corpus.json`, `2wikimultihopqa.json`, `2wikimultihopqa_corpus.json` (the exact 1,000-question samples and pooled corpora of the HippoRAG 2 paper: 11,656 and 6,119 passages). Retrieval is over the full pooled corpus (open-domain), not per-question distractors.
- Slices: `random.Random(20261005).sample(range(1000), n)` over the question list, n = 50 (pilot) or 500 (full run). The pilot slice is the first 50 of the same permutation, so pilot is a subset of the full slice.
- Gold: `answer` plus `answer_aliases` (MuSiQue only). MuSiQue questions with `answerable=false`: none expected in this sample; if present they are dropped and counted.

## 3. Systems
Shared: corpus passage = `title + "\n" + text`, no chunking (passages are already short). Dense embedder `BAAI/bge-small-en-v1.5` (CPU), cosine, normalised. BM25: `bm25s` defaults on lower-cased word tokens. Cross-encoder: `BAAI/bge-reranker-base`.
1. DENSE: top by dense cosine.
2. BM25: top by BM25.
3. HYBRID: RRF (k=60) of dense top-50 and BM25 top-50, ranking by fused score.
4. HYBRID+RERANK: HYBRID top-30 reranked by the cross-encoder.
5. HippoRAG 2 (adapter): see section 7. Run only if feasible without paid APIs; otherwise reported as "not run" with what it needs.
6. LightRAG (adapter): same condition.
The tuned hybrid (4) is the "tuned baseline" for H1-H3. Its knobs (candidate depths 50/30, RRF k=60, reranker model) are fixed here and are NOT tuned on pilot or evaluation questions.

## 4. Matched context budget (precise)
- Budget B counts tokens of the exact context string given to the generator, using `tiktoken` `cl100k_base`, counting `title\ntext` of each passage joined by blank lines. The question and instructions are the same fixed template for every method and are not counted.
- Fill rule: take the method's ranked passages in order; add whole passages while the running total stays <= B; stop at the first passage that would overflow (no truncation, no skipping ahead). Primary B = 1000 tokens. Secondary (if time) B = 2000.
- Methods that natively return non-passage context (LightRAG entities/relations/text units): their context string is built from their own native output order and cut at the same B by the same fill rule, using their configured token caps set to B.
- "Matched" = same generator, same prompt template, same B, actual mean tokens reported per method; a comparison is invalid if a method's mean actual context differs from the others by more than 15% (reported, not hidden).
- Context-size confound control: dense-only is always run at the same B, so the graph edge is measured against a vector baseline at the same context size (the Appendix M design of 2502.11371), plus the tuned hybrid at the same B.

## 5. Generator and metrics
- Generator: `claude -p --model claude-sonnet-5-5` with lean flags, no tools, a fixed short-answer prompt (answer with a short phrase only, or the string `unanswerable`). One interface (`generate(question, context) -> answer, usage`) so a local model can be swapped in. Claude subscription only, no paid API. Temperature is not controllable in `claude -p`; answers are cached by hash of (question, context, prompt) so reruns cost nothing, and non-determinism is a stated caveat.
- Quality: token-F1 and EM using the SQuAD/MuSiQue normalisation (lower-case, strip articles and punctuation), max over gold answer and aliases. Also reported: retrieval recall of supporting passages is NOT computed (no gold passage ids mapped in the pooled corpus for 2Wiki); this is a limitation.
- Cost per method, three columns: (a) indexing tokens (embedding tokens for local models; LLM input/output tokens for graph extraction) and wall-clock seconds, (b) per-query context + generator tokens (from `usage`), (c) dollars-equivalent using a declared price table (gpt-4o-mini $0.15/M in, $0.60/M out as the "cheap API" reference; local embedding/rerank priced at $0 with seconds reported). Reported as total per 1,000 queries = indexing + 1,000 x query cost. Claude subscription costs are reported as notional `total_cost_usd` separately and never mixed into the matched-cost comparison.
- Latency: retrieval wall-clock per query (median, p95), CPU, single process. Generator latency reported separately.
- Statistics: percentile bootstrap (10,000 resamples) 95% CIs on mean F1/EM; paired bootstrap for method differences on the same questions. Rough power: per-question F1 SD about 0.4, so n=50 gives a CI of about +/-11 F1 on a difference of means and n=500 about +/-3.5.

## 6. Decision rules (apply to the n=500 run, NOT the pilot)
- The n=50 pilot is for pipeline validation and variance estimates only. No verdict, no scale/kill, from the pilot.
- KILL the "graph is overrated" angle: HippoRAG 2 beats HYBRID+RERANK by more than 5 F1 (paired CI lower bound above 0) on BOTH datasets at B=1000. Then pivot to update-drift (topic 3 of the deep-dive) or routing.
- SCALE (write up, add LightRAG and a docs corpus): H1 and H2 both hold with point estimates, and cost ratio H3 holds.
- ITERATE otherwise (mixed result): report as a partial result, add B=2000, and the third sample.
- Sanity gate for the pipeline before any claim: DENSE F1 on both slices must be in a plausible range versus published dense baselines (roughly 0.25-0.55 given a stronger generator and smaller embedder); a value outside that triggers a bug check, not a conclusion.

## 7. Graph methods: adapters and install path
- HippoRAG 2 (OSU-NLP-Group/HippoRAG, `pip install hipporag`): needs (i) OpenIE extraction over every passage (LLM calls: published cost 9.2M in / 3.0M out tokens and 99.5 min on 11,656 MuSiQue passages with Llama-3.3-70B on 4 H100s, Table 12), (ii) triple filtering LLM calls per query, (iii) an embedder (paper: NV-Embed-v2, 7B). The repo ships precomputed OpenIE results for its MuSiQue sample (`outputs/musique`), which allows an index with no extraction spend; 2Wiki has none. Today's attempt is time-boxed and its outcome is recorded in the report, not here. Whatever is run today uses the paper's cost numbers for indexing, flagged as published, not measured.
- LightRAG (HKUDS/LightRAG): needs an LLM for entity/relation extraction (published ~68.5M in / 18.3M out tokens on MuSiQue per 2502.14802 Table 12) and per-query keyword extraction. Not feasible today without paid API or a >10 hour subscription run; documented only.
- Both graph methods are evaluated with the same generator and B; their native answer generation is bypassed (only retrieved context is taken).

## 8. Known weaknesses (declared up front)
- bge-small is a weaker embedder than NV-Embed-v2, so dense baselines are lower than published; this affects all baselines equally but moves the size of any gap to a graph method.
- A Claude generator is far stronger than Llama-3.3-70B/GPT-4o-mini; ceiling effects shrink retrieval differences.
- MuSiQue/2Wiki are Wikipedia, which models have seen; closed-book leakage is not measured (a no-context control is run: any F1 above 0.1 there is reported as leakage).
- No supporting-passage recall; no help-center-style corpus yet.
