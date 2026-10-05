"""GraphRAG vs tuned hybrid at matched context budget. See prereg.md in cos-os reports/research/graphrag-hybrid."""
import json, random, re, string, subprocess, sys, time, hashlib, collections, pathlib, argparse
import numpy as np, tiktoken, bm25s
from sentence_transformers import SentenceTransformer, CrossEncoder

ROOT = pathlib.Path(__file__).parent
SEED = 20261005
ENC = tiktoken.get_encoding("cl100k_base")
ntok = lambda s: len(ENC.encode(s))
PRICE = (0.15, 0.60)  # $/M in,out: declared reference price (gpt-4o-mini), not paid

# ---------- data ----------
def load(ds, n):
    f = {"musique": "musique", "2wiki": "2wikimultihopqa"}[ds]
    qs = json.load(open(ROOT / f"data/{f}.json")); corp = json.load(open(ROOT / f"data/{f}_corpus.json"))
    idx = random.Random(SEED).sample(range(len(qs)), len(qs))[:n]
    out = []
    for i in idx:
        q = qs[i]
        if ds == "musique":
            if not q.get("answerable", True): continue
            out.append({"id": q["id"], "q": q["question"], "gold": [q["answer"]] + list(q.get("answer_aliases") or [])})
        else:
            out.append({"id": q["_id"], "q": q["question"], "gold": [q["answer"]]})
    return out, [p["title"] + "\n" + p["text"] for p in corp]

# ---------- retrieval ----------
class Index:
    def __init__(self, ds, docs):
        self.docs = docs; self.t = {}
        cache = ROOT / f"cache/{ds}"; cache.mkdir(exist_ok=True)
        self.emb_model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
        t0 = time.time()
        if (cache / "emb.npy").exists(): self.E = np.load(cache / "emb.npy"); self.t["index_emb_s"] = json.load(open(cache / "t.json"))["emb"]
        else:
            self.E = self.emb_model.encode(docs, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
            np.save(cache / "emb.npy", self.E); self.t["index_emb_s"] = time.time() - t0; json.dump({"emb": self.t["index_emb_s"]}, open(cache / "t.json", "w"))
        self.index_tokens = sum(ntok(d) for d in docs)  # embedding tokens (cl100k proxy)
        self.bm = bm25s.BM25(); self.bm.index(bm25s.tokenize(docs, stopwords=None, show_progress=False), show_progress=False)
        self.ce = None

    def dense(self, q, k):
        v = self.emb_model.encode(["Represent this sentence for searching relevant passages: " + q], normalize_embeddings=True)[0]
        s = self.E @ v; return list(np.argsort(-s)[:k])
    def bm25(self, q, k):
        r, s = self.bm.retrieve(bm25s.tokenize([q], stopwords=None, show_progress=False), k=k, show_progress=False)
        return [int(i) for i in r[0]]
    def hybrid(self, q, k=50, rrf=60):
        sc = collections.Counter()
        for lst in (self.dense(q, k), self.bm25(q, k)):
            for r, i in enumerate(lst): sc[int(i)] += 1 / (rrf + r + 1)
        return [i for i, _ in sc.most_common()]
    def rerank(self, q, k=30):
        if self.ce is None: self.ce = CrossEncoder("BAAI/bge-reranker-base", device="cpu")
        c = self.hybrid(q)[:k]; s = self.ce.predict([(q, self.docs[i]) for i in c], batch_size=16, show_progress_bar=False)
        return [c[i] for i in np.argsort(-s)]

METHODS = {"dense": lambda ix, q: ix.dense(q, 50), "bm25": lambda ix, q: ix.bm25(q, 50),
           "hybrid": lambda ix, q: ix.hybrid(q), "hybrid_rerank": lambda ix, q: ix.rerank(q)}

def fill(docs, ranked, B):
    """prereg sec 4: whole passages in rank order while total <= B; stop at first overflow."""
    out, tot = [], 0
    for i in ranked:
        n = ntok(docs[i]) + (1 if out else 0)
        if tot + n > B: break
        out.append(i); tot += n
    return out, tot

# ---------- generator (single interface) ----------
PROMPT = ("Answer the question using only the context. Reply with the shortest possible answer phrase (an entity, date or number), "
          "no explanation. If the context is insufficient, give your best guess.\n\nContext:\n{c}\n\nQuestion: {q}\nAnswer:")
LEAN = ["--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--disable-slash-commands", "--setting-sources", "project", "--tools", ""]

def gen_claude(q, ctx, model="claude-sonnet-5-5"):
    """returns (answer, usage dict). Cached by hash; cache hits cost nothing."""
    p = PROMPT.format(c=ctx, q=q); h = hashlib.sha256((model + p).encode()).hexdigest()[:24]; f = ROOT / f"cache/gen_{h}.json"
    if f.exists(): d = json.load(open(f)); d["usage"]["cached"] = True; return d["a"], d["usage"]
    t0 = time.time()
    r = subprocess.run(["claude", "-p", "--model", model, *LEAN, "--output-format", "json", p], capture_output=True, text=True, timeout=180, cwd="/tmp")
    j = json.loads(r.stdout); u = j.get("usage", {})
    usage = {"in": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0), "out": u.get("output_tokens", 0),
             "cost": j.get("total_cost_usd", 0), "s": time.time() - t0, "cached": False}
    a = (j.get("result") or "").strip(); json.dump({"a": a, "usage": usage}, open(f, "w")); return a, usage

GENERATORS = {"claude": gen_claude}

# ---------- eval ----------
def norm(s):
    s = s.lower(); s = "".join(c for c in s if c not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())
def f1(p, g):
    p, g = norm(p).split(), norm(g).split()
    c = sum((collections.Counter(p) & collections.Counter(g)).values())
    if not p or not g or c == 0: return float(p == g)
    pr, rc = c / len(p), c / len(g); return 2 * pr * rc / (pr + rc)
def score(pred, golds): return max(f1(pred, g) for g in golds), float(max(norm(pred) == norm(g) for g in golds))

def boot(x, n=10000, seed=0):
    x = np.asarray(x); r = np.random.default_rng(seed); m = r.choice(x, (n, len(x))).mean(1); return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--ds", required=True); ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--B", type=int, default=1000); ap.add_argument("--gen", default="claude"); ap.add_argument("--methods", default=",".join(METHODS) + ",nocontext")
    ap.add_argument("--workers", type=int, default=4); a = ap.parse_args()
    from concurrent.futures import ThreadPoolExecutor
    qs, docs = load(a.ds, a.n); ix = Index(a.ds, docs); G = GENERATORS[a.gen]
    rows = []; extra = {}
    if "hippo" in a.methods.split(","):
        import hippo_adapter as H
        h, extra["hippo_index_s"] = H.build(docs, a.ds); HR = dict(zip([q["q"] for q in qs], H.ranked_docs(h, docs, [q["q"] for q in qs])))
        METHODS["hippo"] = lambda ix, q: HR[q]
    for m in a.methods.split(","):
        jobs = []
        for q in qs:
            t0 = time.time(); ranked = METHODS[m](ix, q["q"]) if m != "nocontext" else []; rl = time.time() - t0
            ids, tot = fill(docs, ranked, a.B); jobs.append((q, ids, tot, rl, "\n\n".join(docs[i] for i in ids)))
        with ThreadPoolExecutor(a.workers) as ex: res = list(ex.map(lambda j: G(j[0]["q"], j[4]), jobs))
        for (q, ids, tot, rl, ctx), (ans, u) in zip(jobs, res):
            f, e = score(ans, q["gold"]); rows.append({"ds": a.ds, "B": a.B, "method": m, "id": q["id"], "f1": f, "em": e, "ctx_tok": tot, "n_pass": len(ids), "ret_s": rl, "gen": u, "ans": ans, "gold": q["gold"][0]})
        print(m, "done", flush=True)
    json.dump({"index_emb_s": ix.t["index_emb_s"], "index_tokens": ix.index_tokens, "n_docs": len(docs), **extra, "rows": rows}, open(ROOT / f"out/{a.ds}_n{a.n}_B{a.B}_{a.methods.replace(',','-')[:30]}.json", "w"))
