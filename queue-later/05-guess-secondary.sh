set -e
.venv/bin/python harness.py --ds musique --n 1000 --B 1000 --methods dense,bm25,hybrid,hybrid_rerank,nocontext,hippo
.venv/bin/python harness.py --ds 2wiki --n 1000 --B 1000 --methods dense,bm25,hybrid,hybrid_rerank,nocontext
