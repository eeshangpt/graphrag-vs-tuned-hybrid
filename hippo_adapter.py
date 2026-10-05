"""HippoRAG 2 retrieval-only adapter (MuSiQue only: precomputed gpt-4o-mini OpenIE ships with the repo).
Deviations from the paper (declared): bge-small embedder instead of NV-Embed-v2; NO LLM triple filter (recognition memory)
-> candidate facts pass through by score. Indexing LLM cost is NOT measured here: uses the shipped OpenIE file.
Install: git clone https://github.com/OSU-NLP-Group/HippoRAG graph/HippoRAG ; uv pip install python_igraph networkx litellm openai ... ; PYTHONPATH=graph/HippoRAG/src"""
import os, sys, shutil, json, time, pathlib
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "graph/HippoRAG/src")); os.environ.setdefault("OPENAI_API_KEY", "unused-no-llm-calls")
from hipporag import HippoRAG

def build(docs, ds="musique"):
    sd = ROOT / f"cache/hippo_{ds}"; sd.mkdir(exist_ok=True)
    h = HippoRAG(save_dir=str(sd), llm_model_name="gpt-4o-mini", embedding_model_name="Transformers/BAAI/bge-small-en-v1.5")
    p = json.load(open(ROOT / "graph/HippoRAG/outputs/musique/openie_results_ner_gpt-4o-mini.json"))
    p["provenance"] = h._current_openie_provenance()  # shipped file predates the provenance check; declared deviation
    json.dump(p, open(h.openie_results_path, "w"))
    # no-LLM recognition memory: keep top candidates by dense score
    def passthrough(query, cand_facts, cand_idx, len_after_rerank=5): return list(cand_idx)[:len_after_rerank], list(cand_facts)[:len_after_rerank], {}
    h.rerank_filter = passthrough
    t0 = time.time(); h.index(docs); return h, time.time() - t0

def ranked_docs(h, docs, queries, k=50):
    idx = {d: i for i, d in enumerate(docs)}
    return [[idx[d] for d in r.docs[:k]] for r in h.retrieve(queries, num_to_retrieve=k)]
