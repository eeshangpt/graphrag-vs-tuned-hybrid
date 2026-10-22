# Data and licences

Code in this repo is Apache-2.0 (`LICENSE`), copyright Eeshan Gupta. Everything below is separate.

## Benchmarks (downloaded, not shipped)

| data | source | licence | how it is used here |
|---|---|---|---|
| MuSiQue (questions, paragraphs) | Trivedi et al., 2022, https://github.com/StonyBrookNLP/musique | CC BY 4.0, stated in the project README | downloaded; answers and gold strings appear in `out/` rows with attribution |
| 2WikiMultiHopQA | Ho et al., 2020, https://github.com/Alab-NII/2wikimultihop | the repo carries the Apache-2.0 licence file; the README does not state a separate data licence; the passages come from Wikipedia (CC BY-SA) | downloaded; gold answer strings appear in `out/` rows |
| the four files `musique`, `musique_corpus`, `2wikimultihopqa`, `2wikimultihopqa_corpus` | Hugging Face `osunlp/HippoRAG_2`, the 1,000-question samples and pooled corpora from the HippoRAG 2 paper | the dataset card declares no licence | not redistributed; `scripts/download_data.sh` fetches them and checks SHA-256 |

Because the Hugging Face packaging has no licence and the 2Wiki data licence is not explicit, I did not commit any of the four files. Files that contained passage text (`confirmatory/retrieval_*.json`, `out/openie_2wiki.json`) are shipped with that text removed. `scripts/restore_text.py` puts it back from the corpora you download and verifies the result against `SHA256SUMS.restored`.

I checked these licences on the projects' own pages on 2026-10-23. If you reuse the benchmarks, read their pages yourself.

## Third-party code

- HippoRAG (OSU NLP Group), MIT licence, https://github.com/OSU-NLP-Group/HippoRAG. Cloned by `scripts/download_data.sh` at commit `2bfd831417202b49cda9da7973e141a456e16872`, not copied here. `openie_2wiki.py` reuses its NER and triple-extraction prompts, one of them verbatim, which MIT allows with this notice: Copyright (c) 2025 OSU Natural Language Processing. The MuSiQue triples that the graph arm uses ship with that repo (extracted by its authors with gpt-4o-mini) and are not copied here.
- Models used and downloaded at run time: `BAAI/bge-small-en-v1.5` and `BAAI/bge-reranker-base` (both MIT on their Hugging Face model cards, checked 2026-10-23).

## Generated files (shipped)

- `out/*_n1000_*.json`, `*_n50_*.json`: per-question answers, F1 and EM, context sizes. The answers were produced by `claude-sonnet-5-5` through the `claude` CLI with a fixed short-answer prompt (`harness.py`). They contain gold answer strings from the benchmarks.
- `out/generator-cache.tar.gz`: the same generator's cached answers, keyed by prompt hash, with token counts and cost fields.
- `out/openie_2wiki.json`: entities and triples for the 6,119 2Wiki passages, extracted by `claude-sonnet-5-5` with `openie_2wiki.py`. Passage text is removed. The triples are facts taken from Wikipedia passages.
- `confirmatory/retrieval_*.json`: retrieved passage ids per arm and question (ids only).

I do not add a separate licence to these generated files. The benchmark attributions above apply to the gold answers inside them, and the terms of the model provider apply to the generated text.
