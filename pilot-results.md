# Pilot results (n=50 per dataset, B=1000 tokens) - topic 5, #162

TL;DR: the pipeline works end to end and the pilot cannot tell the methods apart. All paired CIs include 0, and the sanity gate in the pre-registration FAILED (closed-book leakage, see 3). No verdict, no scale/kill, by the pre-registered rule (prereg section 6).
Pre-registration: `prereg.md` (committed before any number; commit fbbd082 in cos-os history). Harness: `~/research/graphrag-hybrid/` (local git). Generator: `claude -p` claude-sonnet-5-5, subscription (548 uncached calls, notional $4.42). Raw rows: the `*.json` files here.

## 1. Quality, matched budget B=1000 (whole passages, cl100k tokens)
Bootstrap 95% CI (10k resamples), n=50 questions each, one generation per question.

MuSiQue (corpus 11,656 passages):
| method | F1 [95% CI] | EM | mean ctx tokens |
|---|---|---|---|
| no context (control) | 0.299 [0.186, 0.418] | 0.22 | 0 |
| dense (bge-small) | 0.512 [0.385, 0.636] | 0.40 | 931 |
| BM25 | 0.543 [0.420, 0.663] | 0.40 | 911 |
| hybrid RRF | 0.590 [0.468, 0.709] | 0.46 | 931 |
| hybrid + rerank (bge-reranker-base) | 0.602 [0.479, 0.724] | 0.46 | 911 |
| HippoRAG 2 (adapted, see 4) | 0.596 [0.472, 0.717] | 0.46 | 919 |
Paired vs dense: BM25 +0.031 [-0.078, +0.142]; hybrid +0.078 [-0.020, +0.182]; hybrid+rerank +0.090 [-0.026, +0.211]; HippoRAG 2 +0.085 [-0.006, +0.184]. HippoRAG 2 minus hybrid+rerank: -0.006 [-0.129, +0.116].

2WikiMultiHopQA (corpus 6,119 passages):
| method | F1 [95% CI] | EM | mean ctx tokens |
|---|---|---|---|
| no context (control) | 0.580 [0.448, 0.706] | 0.54 | 0 |
| dense | 0.739 [0.616, 0.850] | 0.70 | 826 |
| BM25 | 0.722 [0.599, 0.835] | 0.68 | 900 |
| hybrid RRF | 0.689 [0.563, 0.806] | 0.64 | 877 |
| hybrid + rerank | 0.746 [0.627, 0.855] | 0.70 | 803 |
| HippoRAG 2 | not run (no precomputed OpenIE for 2Wiki) | | |
Paired vs dense: BM25 -0.018 [-0.100, +0.062]; hybrid -0.050 [-0.120, +0.000]; hybrid+rerank +0.007 [-0.056, +0.080].

Matched check (prereg 4): mean actual context differs by up to 14% on 2Wiki (803 vs 900) and 2% on MuSiQue, inside the 15% tolerance, but 2Wiki is close to the line. Same slice for all methods (seed 20261005).

## 2. Cost (not a full comparison yet)
- Dense/BM25/hybrid/rerank indexing: 1,348,035 embedding tokens (MuSiQue corpus, cl100k count), 597 s on CPU (two jobs sharing the machine, so inflated; 2Wiki 376 s). Dollars: $0 (local).
- HippoRAG 2 indexing was NOT re-run: the repo ships gpt-4o-mini OpenIE for the MuSiQue corpus. Published cost of that step with Llama-3.3-70B: 9.2M input + 3.0M output tokens, 99.5 min (2502.14802 Table 12). Output-token check on the shipped file: about 2.75M tokens (tiktoken on the stored entity/triple lists), consistent with 3.0M. At the declared reference price (gpt-4o-mini $0.15/M in, $0.60/M out; price assumption, not a bill) that is about $3.2 once. Our own graph build (fact and entity embeddings, igraph) took 2,173 s on CPU. Query-time: 50 queries retrieved in about 9 s.
- Per 1,000 queries at B~1000: generator input about 1M tokens, about $0.15 at the reference price for every method. So at 1,000 queries the HippoRAG 2 total is roughly 20x the hybrid's, dominated by indexing; the ratio shrinks as query volume grows (H3 is a statement about volume, to be reported as a curve in the full run).
- Latency: hybrid retrieval 0.13 s/q; the reranker took 16-19 s/q here, inflated by CPU contention with HippoRAG indexing running at the same time; rerun alone before quoting.
- Claude generation (not part of the matched cost): 548 uncached calls, notional $4.42, subscription; every call carries about 2.5k tokens of Claude Code overhead, so `usage.in` is not the context size.

## 3. Sanity gate and honest caveats
- Gate FAILED. Pre-registered: dense F1 should be 0.25-0.55; MuSiQue dense is 0.51 (in range) but 2Wiki dense is 0.74 (out of range). The no-context control is far above the 0.1 leakage threshold (0.30 and 0.58). 2Wiki has many yes/no and comparison questions (50% guess) and Wikipedia is in the model's training data. The generator is too strong and too knowledgeable to measure retrieval differences well; on 2Wiki, retrieval adds only +0.16 F1 over no context. This is a design problem for the full run, not a result.
- n=50: all CIs are about +/-12 F1 on single means; no paired difference is distinguishable from zero. The pilot's only use is variance and pipeline validation.
- MuSiQue ordering (dense < BM25 < hybrid ~ rerank ~ HippoRAG 2) is suggestive and in the direction of the hypothesis, nothing more. On 2Wiki the fusion arm is lower than dense alone (-0.05, CI touching 0) and rerank restores it; do not read this as a finding.
- One generation per question, no temperature control in `claude -p`; run-to-run noise is unmeasured.
- Different embedder (bge-small) from the HippoRAG 2 paper (NV-Embed-v2), HippoRAG 2 without the LLM triple filter, shipped OpenIE has no provenance field so the adapter injects one: HippoRAG 2 here is a degraded variant ("graph retrieval without recognition memory"), not a faithful reproduction.
- Recall of supporting passages not computed.

## 4. HippoRAG 2 and LightRAG status
- HippoRAG 2: ran on MuSiQue only, retrieval-only, using the shipped OpenIE. Documented in `hippo_adapter.py` and `README.md`. 2Wiki needs a full OpenIE pass (about 6.1k passages; LLM calls) - not feasible today without paid API; with `claude -p` it is about 12k calls and was not attempted.
- LightRAG: not run. Needs LLM extraction over the whole corpus (published about 68.5M in / 18.3M out tokens on MuSiQue) and keyword extraction per query. Install path: `pip install lightrag-hku`, an LLM function, embedding function, token caps set to B.

## 5. What the full run must change before it starts (proposed amendments, to be pre-registered separately)
1. Replace or add a weaker/less knowledgeable generator (local small model; the GPU is #146's) or an entity-substituted/counterfactual variant, so the no-context control is near 0.
2. Drop 2Wiki yes/no and comparison questions from F1 headline, or report them separately.
3. Rerun the reranker timing alone.
4. n=500 for 80% power on a +/-3.5 F1 difference.
