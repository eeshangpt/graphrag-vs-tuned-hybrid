# Pre-registration amendment 1 (DRAFT for the full run) - #162

Status: draft, not yet binding. It becomes binding when Eeshan decides the items in section 6 and the file is committed before the full run starts. Replaces nothing in `prereg.md` except where it says "replaces". Evidence: `wave2-bugcheck.md` (bug check, prompt test, counterfactual probe, latency).

## 1. Generator and prompt (replaces prereg sec 5 prompt, sec 6 sanity gate)
Options considered:
- A. Weaker generator (local 3-4B, e.g. Qwen3-4B-Instruct-2507, already in the HF cache). Needs the GPU (busy with #146 until tonight) or CPU at roughly 10-20 s per call (about 1,000 calls per method-dataset pair at n=1000: hours per arm). A weak reader is also a different confound: it fails multi-hop reading, so retrieval differences get compressed by reader errors.
- B. Counterfactual corpus (substitute gold answers inside the corpus). Cheap for the vector arms, but HippoRAG's shipped OpenIE triples still contain the original answers, so the graph arm would be inconsistent unless re-extracted. Rejected for the main run.
- C. Keep Sonnet and use the registered refusal prompt ("unanswerable" if the context lacks the answer). Measured: no-context F1 is 0.00 on both datasets (no-context F1 is zero because the prompt makes the model refuse; this does not measure memory-fill under partial context, see wave2-bugcheck.md sec 5), and a counterfactual probe with full gold context (type-unmatched substitutes, so a weak test) shows Sonnet follows the supplied context over its memory in 24 of 30 informative answers (1 memory answer); partial-context behaviour is not tested by it.
Recommendation: C as the single headline generator and prompt. Secondary (reported, never headline): the "best guess" prompt, to show how much memory-fill changes the picture. Skip weak-model and counterfactual-corpus arms. Reason: this restores the prompt that prereg sec 5 already registered (the pilot's "best guess" line was the deviation), needs no new model, and is already measured. It does not remove memory-fill under partial context; the full run therefore logs retrieved ids and a gold-in-context flag per row and reports F1 on rows where the gold string is not in the context as the leakage estimate. Caveat to carry: about 55-60% of answers are "unanswerable" at B=1000, so the metric is retrieval-sufficiency-gated; the effect of the prompt on the ranking of methods is itself a finding (guess prompt: no method separates; refusal prompt: rerank beats dense by +0.14 on MuSiQue at n=50, exploratory).
Sanity gate (replaces): (i) F1 on rows where the gold string is not in the retrieved context (excluding yes/no golds) must be below 0.10 for every arm (measured in the pilot: 0.00 on MuSiQue under the refusal prompt, 0.38-0.57 under the guess prompt) (this can detect memory-fill; the empty-context check alone passes trivially under this prompt); (ii) dense F1 is reported per question type; (iii) the 0.25-0.55 range is dropped (it was a guess and 2Wiki's choose-one types break it).
2Wiki handling: report headline on compositional + inference questions (23 of 50 in the pilot slice); comparison and bridge_comparison types reported separately and excluded from H1 (they are two-choice questions answerable without retrieval of the answer).

## 2. Sample size and the H2 framing (replaces prereg sec 1 H2, sec 5 power note)
- Hard limit: the HippoRAG_2 samples contain 1,000 questions per dataset. n=3,000 is not available without rebuilding both corpora from the full MuSiQue/2Wiki dev sets and re-extracting any graph. The maximum is n=1,000 per dataset (all of it), the permutation order stays from seed 20261005.
- Power for the equivalence test (TOST, two one-sided tests, 90% CI of the paired mean F1 difference inside +/- margin; formula: power at true difference 0 = 2*Phi(margin/se - 1.645) - 1, se = SD/sqrt(n)). Pilot paired SDs (refusal prompt): 0.14-0.47 depending on arm and dataset (HippoRAG-2-lite minus hybrid+rerank, the H2 comparison, is 0.47; an SD from n=50 is itself about +/-20% uncertain). Table uses 0.45 and 0.35; at 0.47 and margin 4 the power at n=1,000 is 0.70.
| n | SD | margin 2 F1 | 3 F1 | 4 F1 | 5 F1 |
|---|---|---|---|---|---|
| 500 | 0.45 | 0.00 | 0.00 | 0.27 | 0.60 |
| 500 | 0.35 | 0.00 | 0.21 | 0.64 | 0.88 |
| 1000 | 0.45 | 0.00 | 0.36 | 0.76 | 0.94 |
| 1000 | 0.35 | 0.13 | 0.71 | 0.95 | 1.00 |
- n needed for 80% power at margin 2 F1: 4,300 (SD 0.45) or 2,600 (SD 0.35); at margin 3 F1: 1,900 or 1,170; at margin 4 F1: about 1,100 or 650. So "within 2 F1" is not testable with the available data; the old text "n=500" was also wrong on power.
- Amended H2 (MuSiQue): HippoRAG 2 vs tuned hybrid at B=1000 is declared equivalent if the 90% paired-bootstrap CI of the F1 difference lies inside +/-4 F1; declared graph-better if the CI lower bound exceeds +4; otherwise inconclusive. n=1,000. Power 0.70-0.95 for the equivalence outcome. This margin is a post hoc weakening chosen for feasibility: the published HippoRAG 2 gap on MuSiQue (+2.9 F1) lies inside it, so an "equivalent" verdict cannot rule out the published effect. The three thresholds are distinct claims: equivalence (CI inside +/-4), graph-better (lower bound above +4), kill (graph beats hybrid by more than 5 F1 with lower bound above 0; the 4-5 band is reported as inconclusive).
- Amended H1 (2Wiki) REPLACES the registered H1 ("hybrid closes at least half of the dense-to-graph gap"), which needs a graph-vs-dense gap estimate and is too complex to power: needs HippoRAG 2 on 2Wiki, which needs OpenIE extraction for 6,119 passages (see decisions). Stated as superiority of graph over tuned hybrid: graph-better if the paired 95% CI lower bound exceeds 0. The headline 2Wiki subset (compositional + inference) is about 46% of 1,000, about 460 questions, so power for a superiority claim is lower than for MuSiQue (not computed; SD for this subset in the pilot was 0.28 for rerank minus dense). If graph is not run on 2Wiki, H1 is dropped and the 2Wiki arm reports the baselines only.
- Kill rule unchanged in spirit: graph beats tuned hybrid by more than 5 F1 (CI lower bound above 0) on every dataset where it was run.

## 3. Context budget B (replaces prereg sec 4 "Secondary")
- Primary B=1000 for all hypotheses. Secondary B=2000 on the same questions for every arm, reported as a sensitivity table without its own hypothesis tests or multiplicity correction; its purpose is the context-size confound seen in 2502.11371 App. M (a graph edge that disappears at larger budget is flagged "budget-sensitive"). Also record the share of "unanswerable" per arm at each B. Optional B=500 not run.
- The wave-2 recall table shows B=1000 is binding (supporting recall 0.53-0.71, gold in context for 38-66% of rows), so B=2000 is the necessary check that conclusions do not depend on a starved context, not an optional extra.
- Fill rule unchanged. Note that at B=1000 a method sees only 3-7 passages; the rule stops at the first overflow, so mean context is 80-93% of B.

## 4. Cost and the H3 curve (replaces prereg sec 5 cost note and H3 wording)
- Per method report: indexing tokens (embedding and LLM), indexing seconds on a stated CPU, per-query retrieval seconds, per-query generator tokens counted by tiktoken on the prompt (not `usage.in`, which includes about 2.5k tokens of Claude Code overhead).
- Priced with one declared table (gpt-4o-mini reference $0.15 / $0.60 per million in/out), local compute at $0 but always shown in seconds; Llama-70B or Claude token counts priced at that reference are labelled approximations.
- H3 as a curve: total cost(V) = indexing + V x per-query cost, for V from 10^2 to 10^6 queries. Summary statistic: the volume V* at which the graph's indexing premium falls below 10% of the hybrid's total cost. Pilot arithmetic (not a result): graph premium about $3.2 (published OpenIE tokens, reference price), per-query generator cost at B=1000 about $0.00015 at the reference price, so V* is about 210,000 queries; the premium also excludes 2,173 s of CPU graph build and the omitted LLM triple filter at query time.
- Reranker: report separately with its latency (6-8 s median per query on CPU, pilot); the hybrid + rerank arm is only a fair "tuned baseline" in cost if that latency is stated.

## 5. Other fixes carried from the audit
- Prompt text is registered here exactly (`PROMPT_PREREG` in `harness.py`).
- Scorer (future work, not yet implemented): the normaliser leaves "5 a.m." as "5 am" vs gold "5am"; collapse single-letter dotted abbreviations before normalising and recompute all arms.
- Report latency median and p95 and generator latency; report the number of dropped unanswerable questions and the n actually scored.
- Slice reading fixed: permutation of all indices, first n.
- Supporting-passage recall: add for both datasets (MuSiQue via is_supporting, 2Wiki via supporting_facts titles); first numbers are in wave2-bugcheck.md sec 5-6.

## 6. Decisions Eeshan must make
1. Graph on 2Wiki (needed for H1): run OpenIE extraction for 6,119 passages with `claude -p` (about 6,100 passages; the pilot note said about 12k calls if NER and triple steps are separate calls, so budget 6-12k calls; 2-3 hours with 4 workers, notional about $60, subscription only, uses a lot of weekly usage; extraction quality differs from the gpt-4o-mini file MuSiQue uses), or drop H1 and run graph on MuSiQue only. Recommendation: do it, after the 22:30 reset, because 2Wiki is where the paper's graph gain is largest (+9.5 F1).
2. Headline prompt: refusal prompt with the guess prompt as secondary (recommended), versus guess prompt headline.
3. H2 margin +/-4 F1 at n=1,000 (recommended), versus staying at 2 F1 and accepting an underpowered or unmeasurable result.
4. Whether the full run also includes the secondary B=2000 (recommended: yes, cached retrieval, about the same generation cost again).
5. LightRAG: needs LLM extraction over the whole corpus (published about 68.5M in / 18.3M out tokens); not feasible on subscription in any reasonable time. Keep as documented-only (recommended) or fund an API run (needs explicit OK).
