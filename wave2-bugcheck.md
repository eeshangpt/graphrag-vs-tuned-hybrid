# Wave 2: amendment 0 (bug check after the 2Wiki sanity-gate failure), leakage test, reranker latency - #162

TL;DR: no pipeline bug found. The 2Wiki gate failed because 27 of 50 sampled 2Wiki questions (comparison and bridge_comparison) are choose-one or yes/no questions whose answer options are in the question text, so they score 0.67-1.0 with no context at all. The compositional 2Wiki questions behave like MuSiQue (no-context F1 0.30). The bigger finding: the generator prompt dominates. With the prereg prompt (refusal allowed) no-context F1 is exactly 0.00 on both datasets, and under it the ordering of methods changes relative to the guess prompt, and rerank and HippoRAG-2-lite separate from dense on MuSiQue (other orderings moved, consistent with noise at n=50). Those prereg-prompt runs are exploratory (run after seeing the pilot), n=50.
Data and code: files in this folder (`*prereg*.json`, `probe.json`, `latency_alone.json`, `probe.py`, `lat.py`, `report2.py`); the harness repo is `~/research/graphrag-hybrid`.

## 1. Bug check (what I checked)
- Alignment: question ids join to gold answers in the source file; 12 items (2Wiki, first in slice order) printed end to end with question, gold, no-context answer, dense answer: all consistent (e.g. "Where was the director of En Aasai Rasave born" gold Theni; dense answers Theni; no-context says Chennai).
- Gold: 2Wiki gold is a single string (no aliases); MuSiQue has aliases. Normalisation is SQuAD style. Containment check on every pilot row: 3-7 of 50 rows per arm have F1<1 but one string contains the other ("Southampton" vs "Southampton, Hampshire", "5 a.m." vs "5am" scores 0: the normaliser removes the dots, giving "5 am" vs "5am", so the mismatch is the space). The scorer is slightly strict, uniformly across arms. Not a bug.
- Prompt formatting: contexts are "title\ntext" blocks joined by blank lines; checked by printing one formatted prompt (2Wiki question 4: 3 passages, 790 tokens). Fine.
- Root cause of the gate failure, by 2Wiki question type (n in the slice; no-context F1 / dense F1, guess prompt): comparison 12 (1.00 / 1.00), bridge_comparison 15 (0.67 / 0.87), compositional 20 (0.30 / 0.50), inference 3 (0.33 / 0.67). Comparison questions give both candidates in the question, so a coin flip or knowledge (12 of 12 correct with no context points to knowledge) answers them.
- The 2Wiki slice is 54% comparison-type, so the 0.74 dense F1 is mostly those types. The gate range in the prereg (0.25-0.55) was a guess; it should be applied per type or on compositional questions only.

## 2. Leakage test with the prereg prompt (n=50 per dataset, B=1000, Sonnet 5.5, one generation each)
Prompt: the registered one ("reply unanswerable if the context lacks the answer"), not "give your best guess".
| | MuSiQue F1 [95% CI] | unanswerable | 2Wiki F1 [95% CI] | unanswerable |
|---|---|---|---|---|
| no context | 0.000 | 100% | 0.000 | 100% |
| dense | 0.228 [0.123, 0.344] | 62% | 0.390 [0.260, 0.520] | 60% |
| BM25 | 0.274 [0.160, 0.397] | 64% | 0.390 [0.260, 0.530] | 58% |
| hybrid RRF | 0.231 [0.125, 0.347] | 60% | 0.370 [0.240, 0.500] | 62% |
| hybrid + rerank | 0.372 [0.244, 0.504] | 54% | 0.430 [0.300, 0.560] | 54% |
| HippoRAG-2-lite | 0.351 [0.230, 0.483] | 52% | not run | |
Paired vs dense (MuSiQue): BM25 +0.046 [-0.066, +0.162]; hybrid +0.003 [-0.072, +0.080]; hybrid+rerank +0.144 [+0.061, +0.239]; HippoRAG-2-lite +0.123 [+0.011, +0.243]. HippoRAG-2-lite minus hybrid+rerank: -0.021 [-0.149, +0.112]. 2Wiki: BM25 0.000 [-0.060, +0.060]; hybrid -0.020 [-0.060, 0.000]; hybrid+rerank +0.040 [-0.040, +0.120].
Reading: (a) the leakage control with EMPTY context is zero by construction (the prompt makes the model refuse); that does not measure memory-fill when the retrieved context is partial, which section 5 estimates. The earlier 0.30 / 0.58 came from the model guessing from memory when told to guess. (b) The generator refuses on about 55-60% of questions, so the F1 here is gated by whether the retrieved 1000 tokens suffice; the refusal prompt is the one registered in prereg sec 5, so using it restores the registered design (the "best guess" prompt was the undisclosed deviation). Hybrid RRF vs dense went from +0.078 (guess) to +0.003 (refusal) and BM25 now beats RRF on MuSiQue: orderings among the cheap arms are not stable. (c) HippoRAG-2-lite ties the tuned baseline again, with a CI of about +/-13 F1. (d) The sizeable "unanswerable" share may be excess caution by the generator; I did not test a middle prompt. Exploratory, n=50, chosen after seeing the guess-prompt pilot, so it is not a confirmatory result.

## 3. Counterfactual probe (20 compositional questions per dataset, gold passages only)
The gold answer was replaced inside the supporting passages by another dataset answer chosen only by first-character type (digit or not) and length within 8 characters; so it is NOT type-matched (e.g. a birthplace replaced by a date, a nationality by a film title), which invites refusals. Question unchanged. If Sonnet reads the context it gives the substituted answer; if it uses memory it gives the original.
- MuSiQue: 20 questions, original context contains gold in 13; counterfactual context: 12 answered the substituted value, 1 answered the original (memory), 4 said unanswerable.
- 2Wiki: 20 questions; original context contains gold in 17; counterfactual: 14 substituted, 0 original, 4 unanswerable.
- Over all 20 per dataset (containment match): containment gives 12 substituted on MuSiQue and 14 on 2Wiki (two 2Wiki hits are generous: "489" inside a hedged list of dates, "August 1904 AD"); the F1>0.5 rule gives 12 and 12. Informative subset (the original context already yields the gold answer): MuSiQue 13 questions: 10 substituted, 1 original (memory; weak: gold "the 2010 election" was replaced by "Vito Corleone" and the model answered "2010"), 1 unanswerable; 2Wiki 17 questions: 14 substituted, 0 original, 2 unanswerable. 5 of 40 items were unanswerable even with the original context and are uninformative; two MuSiQue items share the same gold and substitute.
- Reading: with the full gold context supplied, Sonnet follows it over its memory in 24 of 30 informative answers (1 memory, 3 refusals, 2 other); this says nothing about partial or distractor-only context, which is the case where memory-fill would matter. See section 5. Containment matching (answers like "Kuwait American" count); a stricter F1>0.5 rule gives 12 and 12. Small sample (n=40 total), chosen questions are those whose gold string appears verbatim in a supporting passage.

## 4. Reranker latency alone
Median / p95 seconds per query, 50 queries, CPU, after warm-up, single process. Another unrelated single-thread job (about 100% of one core, the topic 4 judge run) was on the machine, so this is "alone as far as I could get", not an idle machine.
- hybrid + rerank (bge-reranker-base over top-30): MuSiQue 6.25 / 12.39 s, 2Wiki 8.27 / 10.31 s.
- dense 0.11 / 0.12 s (MuSiQue), 0.05 / 0.12 s (2Wiki); BM25 below 1 ms; hybrid RRF 0.11 / 0.13 s and 0.06 / 0.12 s.
- The earlier 16-19 s was contention; the true CPU cost is still 55-140x the hybrid without the reranker. A GPU or a smaller reranker/top-k is needed for any latency claim.

## 5. Retrieval recall and leakage estimate under partial context
Per arm at B=1000: supporting-passage recall, rate of the gold string appearing in the context, and F1 on rows where the gold string is NOT in the context (an upper bound on memory-fill: anything above 0 there is an answer not copied from the context). Script `recall.py`, output `recall.json`; numbers below.

| arm | supporting-passage recall | gold string in context | F1 (guess prompt) gold NOT in ctx (n) | F1 (guess) gold in ctx | F1 (refusal prompt) gold NOT in ctx (n) | F1 (refusal) gold in ctx |
|---|---|---|---|---|---|---|
| MuSiQue dense | 0.57 | 0.50 | 0.41 (25) | 0.61 | 0.00 (25) | 0.46 |
| MuSiQue BM25 | 0.53 | 0.38 | 0.47 (31) | 0.67 | 0.00 (31) | 0.72 |
| MuSiQue hybrid | 0.61 | 0.46 | 0.51 (27) | 0.68 | 0.00 (27) | 0.50 |
| MuSiQue hybrid+rerank | 0.67 | 0.58 | 0.53 (21) | 0.65 | 0.00 (21) | 0.64 |
| MuSiQue HippoRAG-2-lite | 0.67 | 0.66 | 0.38 (17) | 0.71 | 0.00 (17) | 0.53 |
| 2Wiki dense | 0.68 | 0.56 | 0.57 (22) | 0.88 | 0.14 (22) | 0.59 |
| 2Wiki BM25 | 0.69 | 0.58 | 0.46 (21) | 0.91 | 0.14 (21) | 0.57 |
| 2Wiki hybrid | 0.69 | 0.56 | 0.45 (22) | 0.88 | 0.14 (22) | 0.55 |
| 2Wiki hybrid+rerank | 0.71 | 0.60 | 0.49 (20) | 0.92 | 0.15 (20) | 0.62 |
Findings from this table (cells are 17-50 rows; the conditional cells (n=17-33) carry about +/-0.15-0.2, the rest +/-0.1; "gold in context" is a case-insensitive substring test):
- Consistent with memory-fill (the F1 is an upper bound, since partial-F1 credit and paraphrase misses also inflate it): with the guess prompt, MuSiQue rows whose context lacks the gold string still score F1 0.38-0.53, i.e. the model often answers from memory; with the refusal prompt the same rows score 0.00. On 2Wiki the 0.14 under the refusal prompt is a yes/no artifact (the "yes" golds never appear as a string in context; the 4 "no" golds per arm match the substring test spuriously, since "no" occurs inside "not", "known"; so gold-in-context is overstated by up to 0.08 on 2Wiki): excluding yes/no golds, F1 on gold-not-in-context rows is 0.00 under the refusal prompt for dense, BM25 and hybrid (n=16-17; `recall2.py`, `recall2.json`; guess prompt 0.35-0.44 on the same rows). Rerank and HippoRAG rows were not rechecked this way. Future flag: match on word boundaries.
- The budget is binding: at B=1000 only 0.53-0.71 of supporting passages are in context and the gold string is present in only 38-66% of rows. This mostly explains the 52-62% refusal rate, not entirely: refusals exceed the gold-not-in-context share by about 2-18 points (MuSiQue 12, 2, 6, 12, 18; 2Wiki 16, 16, 18, 14 before correcting the spurious "no" matches, about 6-10 after), and F1 on gold-in-context rows is only 0.46-0.72 under the refusal prompt (0.88-0.92 on 2Wiki with the guess prompt), so some of the refusal rate may be generator caution or incomplete chains (not isolated). B=2000 is the check on whether conclusions depend on a starved context.
- Supporting-passage recall at B=1000: MuSiQue rerank and HippoRAG-2-lite tie (0.67), dense 0.57, BM25 0.53; recall was computable for 2Wiki (via supporting_facts titles) after all, contrary to the prereg note.
- Limits: gold-in-context is a string test (paraphrases missed), n is small, hippo has no 2Wiki arm. The recall table comes from re-running retrieval (the rows did not log ids); for dense, BM25 and hybrid on 2Wiki only, I verified that the re-run fill reproduces the logged context token count on all 50 rows (equal token counts are evidence of, not proof of, identical passage ids); it was not verified for MuSiQue, nor for the rerank and HippoRAG arms. The full run logs retrieved ids.

## 6. Caveats on this whole note
Everything in sections 2, 3 and 5 is exploratory (n=50 or n=20, chosen after the pilot), the prereg-prompt runs reuse the pilot slice, and one generation per question was taken. NOTE for amendment: the pilot slice (seed 20261005) was used for design decisions here, so it must not be reused as a confirmatory sample (the full run uses the first 1,000 of the same permutation, which overlaps it; mark the first 50 as the exploratory subset and report the rest separately).
