# graphrag-hybrid harness (see cos-os reports/research/graphrag-hybrid/prereg.md)
Setup: `uv venv .venv; uv pip install -p .venv/bin/python bm25s sentence-transformers tiktoken numpy torch --extra-index-url https://download.pytorch.org/whl/cpu`
Data: 4 json files from HF `osunlp/HippoRAG_2` into data/ (musique, musique_corpus, 2wikimultihopqa, 2wikimultihopqa_corpus).
Run: `python harness.py --ds musique|2wiki --n 50 --B 1000 --methods dense,bm25,hybrid,hybrid_rerank,nocontext[,hippo]`; `python report.py`.
Generator: `claude -p` (subscription), cached in cache/gen_*.json; swap by adding to GENERATORS in harness.py.
HippoRAG 2 (MuSiQue only): git clone https://github.com/OSU-NLP-Group/HippoRAG graph/HippoRAG; uv pip install python_igraph networkx litellm openai tenacity pydantic nest_asyncio scipy pandas pyarrow filelock httpx einops boto3; uses shipped gpt-4o-mini OpenIE. See hippo_adapter.py for declared deviations.
LightRAG: not run (needs LLM extraction over the corpus; ~68.5M in/18.3M out tokens published for MuSiQue).
