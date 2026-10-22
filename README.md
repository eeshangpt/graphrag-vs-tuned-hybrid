# GraphRAG vs a tuned hybrid retriever

This repo has the code, the pre-registration and the outputs of a small experiment. If a graph retriever and a tuned hybrid retriever (BM25 plus dense search, rank fusion, a cross-encoder reranker) give the generator the same 1,000 tokens of context, how much of the graph's advantage is left?

The write-up is at https://eeshangpt.github.io/writing/graphrag-vs-tuned-hybrid/. This README is for checking the numbers.

## Result

The confirmatory sample is 950 questions per dataset. Scores are token F1, and the intervals come from a paired percentile bootstrap (10,000 resamples, seed 0). The numbers are copied from `confirmatory/results.md`.

| graph (HippoRAG 2-lite) minus tuned hybrid | F1 difference | 95% CI |
|---|---|---|
| 2WikiMultiHopQA | +19.0 | +16.1 to +22.0 |
| MuSiQue | +3.5 | +0.4 to +6.5 |

On MuSiQue the registered equivalence test (TOST, margin plus or minus 4 F1) is inconclusive: the 90% interval is +0.9 to +6.0. The registered verdict is iterate. The kill rule asked for a gain above 5 F1 with a positive lower bound on both datasets, and MuSiQue misses it. `confirmatory/report.md` has the full table, the checks and the caveats.

## Reproduce the analysis

This step makes no API calls and needs no GPU. It recomputes every number above from the shipped answers.

```bash
git clone https://github.com/eeshangpt/graphrag-vs-tuned-hybrid && cd graphrag-vs-tuned-hybrid
./scripts/download_data.sh          # four benchmark files (about 28 MB) and the HippoRAG repo, hash-checked
python3 scripts/restore_text.py     # puts passage text back into three shipped files, hash-checked
uv venv .venv && uv pip install -p .venv/bin/python numpy tiktoken
.venv/bin/python confirmatory/analyze.py    # run from the repo root; rewrites confirmatory/results.json and results.md
git diff --stat confirmatory/results.json confirmatory/results.md    # empty when everything matches
```

I ran these steps in a fresh copy of the repo, and `results.json` and `results.md` came out byte-identical to the shipped ones.

I did not want to redistribute passage text from datasets whose packaging has no licence (`DATA.md`). The shipped files hold document ids and generated outputs, and `scripts/restore_text.py` rebuilds the rest from the corpora you download.

## Reproduce the whole run

I have not done this end to end from a clean clone, so treat it as untested.

- Install with `uv pip install -p .venv/bin/python bm25s sentence-transformers tiktoken numpy torch --extra-index-url https://download.pytorch.org/whl/cpu` plus the HippoRAG dependencies in `HARNESS-NOTES.md`. Everything ran on CPU.
- Generation calls the `claude` CLI with `claude-sonnet-5-5`, one call per question and arm. `out/generator-cache.tar.gz` holds all 12,557 cached answers, pilot and confirmatory. Unpack it into `cache/` and the harness replays the answers without calling the model.
- Without the cache, the CLI's list-price cost in my runs was about $106 for the answers and $98 for the 2Wiki triple extraction (12,238 calls, 15.97M tokens in, 3.46M out). Both ran on a Claude subscription, so no cash left my account.
- `RUN.md` and `queue/` give the job order.

## Repo map

| path | contents |
|---|---|
| `prereg.md`, `prereg-amendment-1.md`, `prereg-amendment-2.md` | the registered protocol and its two amendments, frozen text |
| `deviations.md` | every departure from the protocol, including the ones that hurt |
| `harness.py`, `hippo_adapter.py`, `openie_2wiki.py` | retrieval arms and generator calls, the HippoRAG 2 adapter, triple extraction for 2Wiki |
| `confirmatory/` | `analyze.py`, `results.json`, `results.md`, `report.md`, retrieval ids, audit records of the final analysis |
| `out/` | n=1000 rows per arm and dataset, the 2Wiki triples, the generator cache |
| `*_n50_*.json`, `pilot-results.md`, `wave2-bugcheck.md`, `probe.json`, recall and latency scripts | the pilot (n=50) and the bug check after it |
| `audit-*.md` | reviews of the pilot and of amendment 1 by another model, called through a command line tool named `agy` |
| `queue/`, `queue-later/` | job scripts that ran, and some I wrote and never ran |
| `scripts/`, `SHA256SUMS.*` | data download, text restore, and the hashes they check |
| `HISTORY.md` | how this history was extracted, what changed, and the full timeline |
| `DATA.md` | licences |

## Pre-registration timeline

All times are IST. `HISTORY.md` has the full table with sources, and for each row whether a server record exists or only my local files.

| when | what |
|---|---|
| 2026-10-05 13:04 | `prereg.md` committed, before the harness ran (commit `680d0f7`) |
| 2026-10-05 13:36 | first pilot result file written |
| 2026-10-05 13:55 | the same commit rebased and pushed, which is the first GitHub record of it |
| 2026-10-06 13:01 | prereg and amendment 1 frozen, tag `prereg-162-frozen`, on GitHub at 13:01 |
| 2026-10-06 19:46 | amendment 2 draft pushed (the n=950 split) |
| 2026-10-07 02:36 | first confirmatory answer generated |
| 2026-10-11 16:59 | amendment 2 frozen, tag `prereg-162-amendment-2-frozen`, after the confirmatory rows existed |
| 2026-10-11 19:50 | confirmatory analysis committed |

Two caveats come with this table. The 13:04 time of `prereg.md` rests on my local git record. Git author dates can be set by hand, and the first record from GitHub (13:55) is later than the first pilot output (13:36). A copy of the original commit that I kept locally has the same file, but it was never pushed. The pilot is exploratory and does not feed the headline numbers. For the confirmatory run the order holds on the server's clock: the protocol and amendment 1 were on GitHub at 13:01 on 10-06, and the first confirmatory answer came 13.5 hours later.

Amendment 2 was drafted before the confirmatory run, but I froze it after the data existed, and I had looked at the F1 preview before writing the pre-commitment for the B=2000 rule. `deviations.md` items 2 and 11 say so.

## Limits

- One generator (Claude Sonnet 5.5) and one non-deterministic generation per question. Between 33% and 65% of answers are refusals, so F1 depends heavily on whether retrieval put the answer in the context.
- The budget is 1,000 tokens. A gold answer string appears in the context for 37% to 56% of MuSiQue rows and 59% to 86% of 2Wiki rows, so every verdict holds at that budget only. The B=2000 check I registered never ran.
- The graph arm is a lite version of HippoRAG 2. It skips the LLM triple filter at query time and uses `bge-small` instead of NV-Embed-v2. The cost analysis that includes the filter is an estimate.
- The two graph arms are built differently. MuSiQue uses the authors' gpt-4o-mini triples. 2Wiki uses triples I extracted with Claude Sonnet 5.5, the same model family as the generator.
- I set the equivalence margin (4 F1) after the pilot, in amendment 1, because 2 F1 could not be tested at n=950.
- `deviations.md` lists the registered checks I did not run.

## License

Code is Apache-2.0 (`LICENSE`). Data, third-party code and generated files fall under other licences, described in `DATA.md`.
