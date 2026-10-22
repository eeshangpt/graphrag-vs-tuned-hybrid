"""HippoRAG 2 OpenIE for the 2Wiki corpus via `claude -p` (no shipped file exists for 2Wiki).
Prompts: copied verbatim from OSU-NLP-Group/HippoRAG src/hipporag/prompts/templates/{ner.py,triple_extraction.py} (the prompts the repo's
OpenIE uses: stage 1 NER, stage 2 triples conditioned on the entity list). Deviation (declared): `claude -p` has no multi-turn few-shot, so the
one-shot example is embedded as text in the user message. Generator = claude sonnet (not gpt-4o-mini). Output schema = shipped MuSiQue file.
Usage: python openie_2wiki.py [--limit N | --sample N] [--out PATH] [--workers 4]   (resumable: per-passage cache cache/openie_2wiki/)"""
import sys, os, re, json, time, hashlib, pathlib, argparse, subprocess, ast
from concurrent.futures import ThreadPoolExecutor
ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT / "graph/HippoRAG/src"))
from hipporag.utils.misc_utils import compute_mdhash_id
sys.path.insert(0, str(ROOT / "graph/HippoRAG/src/hipporag/prompts/templates"))
import importlib.util
def _load(n):
    s = importlib.util.spec_from_file_location(n, ROOT / f"graph/HippoRAG/src/hipporag/prompts/templates/{n}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
ner = _load("ner")
NER_SYS = ner.ner_system
TRI_SYS = ("Your task is to construct an RDF (Resource Description Framework) graph from the given passages and named entity lists. \n"
           "Respond with a JSON list of triples, with each triple representing a relationship in the RDF graph. \n\n"
           "Pay attention to the following requirements:\n- Each triple should contain at least one, but preferably two, of the named entities in the list for each passage.\n"
           "- Clearly resolve pronouns to their specific names to maintain clarity.\n\n")  # verbatim from triple_extraction.py (the module needs the package's relative imports)
FRAME = "Convert the paragraph into a JSON dict, it has a named entity list and a triple list.\nParagraph:\n```\n{passage}\n```\n\n{named_entity_json}\n"
TRI_EX_OUT = open(ROOT / "graph/HippoRAG/src/hipporag/prompts/templates/triple_extraction.py").read().split('ner_conditioned_re_output = """')[1].split('"""')[0]
MODEL = "claude-sonnet-5-5"
LEAN = ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--disable-slash-commands", "--setting-sources", "project", "--tools", ""]
CACHE = ROOT / "cache/openie_2wiki"; CACHE.mkdir(parents=True, exist_ok=True)
FAILS = ROOT / "out/openie_2wiki_failures.jsonl"

def stage1(p): return NER_SYS, f"Example paragraph:\n{ner.one_shot_ner_paragraph}\n\nExample output:\n{ner.one_shot_ner_output}\n\nNow the real paragraph. Reply with the JSON only.\n\n{p}"
def stage2(p, ents):
    ex = FRAME.format(passage=ner.one_shot_ner_paragraph, named_entity_json=ner.one_shot_ner_output)
    return TRI_SYS, f"Example input:\n{ex}\nExample output:\n{TRI_EX_OUT}\n\nNow the real input. Reply with the JSON only.\n\n" + FRAME.format(passage=p, named_entity_json=json.dumps({"named_entities": ents}, ensure_ascii=False))

def parse(txt, key):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt.strip())  # claude wraps JSON in fences
    if not t.startswith("{"): t = t[t.find("{"): t.rfind("}") + 1]
    v = json.loads(t)[key]; assert isinstance(v, list); return v

def call(sysp, user):
    t0 = time.time()
    r = subprocess.run(["claude", "-p", "--model", MODEL, *LEAN, "--system-prompt", sysp, "--output-format", "json", user], capture_output=True, text=True, timeout=240, cwd="/tmp")
    j = json.loads(r.stdout); u = j.get("usage", {})
    return (j.get("result") or ""), {"in": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
            "out": u.get("output_tokens", 0), "cost": j.get("total_cost_usd", 0), "s": time.time() - t0}

def stage(name, sysp, user, key, cid):
    for att in range(3):
        try:
            txt, u = call(sysp, user); return parse(txt, key), u
        except Exception as e:
            with open(FAILS, "a") as f: f.write(json.dumps({"ts": time.time(), "chunk": cid, "stage": name, "attempt": att, "err": repr(e)[:200]}) + "\n")
    raise RuntimeError(f"{name} failed 3x for {cid}")

def extract(doc):
    cid = compute_mdhash_id(doc, prefix="chunk-")
    f = CACHE / f"{hashlib.sha256((MODEL + doc).encode()).hexdigest()[:24]}.json"
    if f.exists(): return json.load(open(f))
    try:
        ents, u1 = stage("ner", *stage1(doc), "named_entities", cid)
        tri, u2 = stage("triples", *stage2(doc, ents), "triples", cid)
    except RuntimeError as e: return {"idx": cid, "failed": str(e)}
    d = {"idx": cid, "extracted_entities": ents, "extracted_triples": tri, "usage": {"in": u1["in"] + u2["in"], "out": u1["out"] + u2["out"], "cost": u1["cost"] + u2["cost"], "s": u1["s"] + u2["s"], "calls": 2}}
    json.dump(d, open(f, "w"), ensure_ascii=False); return d

def corpus():
    return json.load(open(ROOT / "data/2wikimultihopqa_corpus.json"))

def sample_titles(n_q=5, n=50):
    """passages supporting the first n_q harness questions, filled with corpus-order passages up to n (deterministic)."""
    sys.path.insert(0, str(ROOT)); import random
    qs = json.load(open(ROOT / "data/2wikimultihopqa.json")); idx = random.Random(20261005).sample(range(len(qs)), len(qs))[:n_q]
    want = []
    for i in idx:
        for t, _ in ast.literal_eval(qs[i]["supporting_facts"]) if isinstance(qs[i]["supporting_facts"], str) else qs[i]["supporting_facts"]: want.append(t)
    c = corpus(); sel = [p for p in c if p["title"] in set(want)]
    for p in c:
        if len(sel) >= n: break
        if p not in sel: sel.append(p)
    return sel[:n]

def run(passages, out, workers=4):
    docs = [p["title"] + "\n" + p["text"] for p in passages]
    with ThreadPoolExecutor(workers) as ex: res = list(ex.map(extract, docs))  # map keeps corpus order
    ok = [(p, d) for p, d in zip(passages, res) if "failed" not in d]
    rows = [{"idx": d["idx"], "title": p["title"], "text": p["text"], "passage": p["title"] + "\n" + p["text"], "extracted_entities": d["extracted_entities"], "extracted_triples": d["extracted_triples"]} for p, d in ok]
    ents = [e for r in rows for e in r["extracted_entities"]]
    js = {"docs": rows, "avg_ent_chars": round(sum(map(len, ents)) / max(len(ents), 1), 4), "avg_ent_words": round(sum(len(e.split()) for e in ents) / max(len(ents), 1), 4)}
    json.dump(js, open(out, "w"), ensure_ascii=False)
    us = [d["usage"] for _, d in ok]
    stats = {"model": MODEL, "n_requested": len(docs), "n_ok": len(ok), "n_failed": len(docs) - len(ok), "in_tokens": sum(u["in"] for u in us), "out_tokens": sum(u["out"] for u in us),
             "cost_usd": sum(u["cost"] for u in us), "calls": sum(u["calls"] for u in us), "note": "cost counts only calls cached in the per-passage cache (cache hits from earlier runs included)"}
    json.dump(stats, open(str(out) + ".stats.json", "w"), indent=1); print(json.dumps(stats)); return js

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int); ap.add_argument("--sample", type=int); ap.add_argument("--out", default=str(ROOT / "out/openie_2wiki.json")); ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    ps = sample_titles(5, a.sample) if a.sample else corpus()[: a.limit] if a.limit else corpus()
    run(ps, a.out, a.workers)
