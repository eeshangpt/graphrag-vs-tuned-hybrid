"""Rebuild the files that were shipped without third-party passage text.
Run after scripts/download_data.sh, from the repo root:  python scripts/restore_text.py
It fills 'ctx' in confirmatory/retrieval_*.json and 'text'/'passage' in out/openie_2wiki.json from data/*_corpus.json,
then checks each result against SHA256SUMS.restored (the hashes of the files as they were when the analysis ran)."""
import json, hashlib, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
def corpus(f):
    return json.load(open(ROOT / f"data/{f}_corpus.json"))
for ds, f in (("musique", "musique"), ("2wiki", "2wikimultihopqa")):
    docs = [p["title"] + "\n" + p["text"] for p in corpus(f)]
    path = ROOT / f"confirmatory/retrieval_{ds}.json"; rr = json.load(open(path))
    for k, v in rr.items():  # same key order as when the file was written, so the hash matches
        rr[k] = {"ids": v["ids"], "tot": v["tot"], "sup_n": v["sup_n"], "sup_hit": v["sup_hit"], "ctx": "\n\n".join(docs[i] for i in v["ids"]),
                 "cache_hit": v["cache_hit"], "ans_same": v["ans_same"], "tok_same": v["tok_same"], "prompt_tok": v["prompt_tok"]}
    json.dump(rr, open(path, "w"))
c = corpus("2wikimultihopqa"); path = ROOT / "out/openie_2wiki.json"; o = json.load(open(path))
assert len(o["docs"]) == len(c)
for i, (d, p) in enumerate(zip(o["docs"], c)):
    passage = p["title"] + "\n" + p["text"]
    assert d["title"] == p["title"] and d["idx"] == "chunk-" + hashlib.md5(passage.encode()).hexdigest(), "row does not match corpus passage " + d["idx"]
    o["docs"][i] = {"idx": d["idx"], "title": d["title"], "text": p["text"], "passage": passage,
                    "extracted_entities": d["extracted_entities"], "extracted_triples": d["extracted_triples"]}
json.dump(o, open(path, "w"), ensure_ascii=False)
bad = 0
for line in open(ROOT / "SHA256SUMS.restored"):
    h, name = line.split(maxsplit=1); name = name.strip()
    ok = hashlib.sha256(open(ROOT / name, "rb").read()).hexdigest() == h; bad += not ok; print("OK  " if ok else "BAD ", name)
sys.exit(1 if bad else 0)
