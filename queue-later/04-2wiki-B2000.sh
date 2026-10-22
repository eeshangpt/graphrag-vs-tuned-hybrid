set -e
PROMPT_VARIANT=prereg .venv/bin/python harness.py --ds 2wiki --n 1000 --B 2000 --methods dense,bm25,hybrid,hybrid_rerank
