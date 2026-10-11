"""Confirmatory (#162): re-run retrieval for the n=1000 slices (rows did not log ids), and PROVE it reproduces the generation run:
the rebuilt prompt hashes to an existing generator cache file whose answer equals the logged answer. Usage (cwd = experiment repo):
 PROMPT_VARIANT=prereg .venv/bin/python <this> <musique|2wiki> <out.json>"""
import sys, json, hashlib, os, pathlib
sys.path.insert(0, os.getcwd()); os.environ["PROMPT_VARIANT"] = "prereg"
from harness import *
ds, outp = sys.argv[1], sys.argv[2]
qs, docs = load(ds, 1000); ix = Index(ds, docs); D = {d: i for i, d in enumerate(docs)}
f = {"musique": "musique", "2wiki": "2wikimultihopqa"}[ds]; raw = {(q.get("id") or q.get("_id")): q for q in json.load(open(f"data/{f}.json"))}
title = {}
for i, d in enumerate(docs): title.setdefault(d.split("\n", 1)[0], []).append(i)
import hippo_adapter as H
h, _ = H.build(docs, ds); HR = dict(zip([q["q"] for q in qs], H.ranked_docs(h, docs, [q["q"] for q in qs])))
METHODS["hippo"] = lambda ix, q: HR[q]
import glob
logged = {}
for fn in glob.glob(f"out/{ds}_n1000_B1000prereg_*.json"):
    for r in json.load(open(fn))["rows"]: logged[(r["method"], r["id"])] = r
res = {}
for m in ("dense", "bm25", "hybrid", "hybrid_rerank", "hippo"):
    for q in qs:
        r = raw[q["id"]]
        if ds == "musique": sup = {D[p["title"] + "\n" + p["paragraph_text"]] for p in r["paragraphs"] if p["is_supporting"] and (p["title"] + "\n" + p["paragraph_text"]) in D}
        else: sup = {i for t in {t for t, _ in r["supporting_facts"]} for i in title.get(t, [])}
        ids, tot = fill(docs, METHODS[m](ix, q["q"]), 1000); ctx = "\n\n".join(docs[i] for i in ids)
        p = PROMPT_PREREG.format(c=ctx, q=q["q"]); hh = hashlib.sha256(("claude-sonnet-5-5" + p).encode()).hexdigest()[:24]; cf = ROOT / f"cache/gen_{hh}.json"
        lg = logged[(m, q["id"])]; hit = cf.exists(); same = hit and json.load(open(cf))["a"] == lg["ans"]
        res[f"{m}|{q['id']}"] = {"ids": [int(i) for i in ids], "tot": tot, "sup_n": len(sup), "sup_hit": len(sup & set(ids)), "ctx": ctx, "cache_hit": hit, "ans_same": bool(same), "tok_same": tot == lg["ctx_tok"], "prompt_tok": ntok(p)}
    print(ds, m, "done", flush=True)
json.dump(res, open(outp, "w"))
