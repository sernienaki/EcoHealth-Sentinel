"""RAG for EcoHealth Sentinel: ingest official documents, hybrid search with abstention, cited answers, evaluation.

Documents are listed in each country pack under "documents". The index is built inside the running app
(Streamlit Cloud has internet), or from PDFs uploaded in the app.
"""
import io
import os
import re
import json
import math
from collections import Counter, defaultdict
import numpy as np
from packs import HERE

CHUNK_WORDS, OVERLAP = 180, 40
STOP = set("""the a an of to in on for and or is are was were be been it this that with as by at from what which who how can does do not no may must shall any
ya na wa kwa ni la za katika kuwa cha kama hii huu hizo kwamba pia au sana nini gani ni ipi""".split())


# ------------------------------------------------------------------ ingestion
def clean_text(t):
    t = t.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\u00ad", "")
    t = t.replace("\ufffd", "ti")  # some PDFs lose the "ti" ligature; this is a best guess repair
    t = re.sub(r"-\n(?=[a-z])", "", t)
    return re.sub(r"\s+", " ", t).strip()


def pdf_pages(data):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return [(i + 1, clean_text(p.extract_text() or "")) for i, p in enumerate(reader.pages)]


def fetch_pages(url, max_mb=60):
    import requests
    r = requests.get(url, timeout=90, headers={"User-Agent": "EcoHealthSentinel/1.0"})
    r.raise_for_status()
    if len(r.content) > max_mb * 1024 * 1024:
        raise ValueError("file too large")
    if not r.content[:5].startswith(b"%PDF"):
        raise ValueError("the link did not return a PDF")
    return pdf_pages(r.content)


def text_pages(text, words=400):
    w = clean_text(text).split()
    return [(i // words + 1, " ".join(w[i:i + words])) for i in range(0, len(w), words)]


def chunk_pages(meta, pages):
    """Split each page into overlapping windows. Chunks never cross a page, so every citation has a page number."""
    out = []
    for page, text in pages:
        w = text.split()
        if len(w) < 15:
            continue
        for j, s in enumerate(range(0, max(1, len(w) - OVERLAP), CHUNK_WORDS - OVERLAP)):
            out.append({"id": f"{meta['id']}-{page}-{j}", "doc": meta["id"], "title": meta["title"], "page": page,
                        "status": meta.get("status", ""), "text": " ".join(w[s:s + CHUNK_WORDS])})
    return out


# ------------------------------------------------------------------ index
class Index:
    """Hybrid search: BM25 plus character n-gram TF-IDF (handles Kiswahili word forms), optional dense embeddings,
    fused by reciprocal rank. Abstains when the best passages cover too few query terms."""

    def __init__(self, chunks, min_coverage=0.5, embedding_model=None):
        self.chunks, self.min_coverage, self.embedding_model, self.last = chunks, min_coverage, embedding_model, {}
        self._tok = [self._tokens(c["text"]) for c in chunks]
        self.N = len(chunks)
        self.dl = np.array([len(t) for t in self._tok]) if self.N else np.zeros(0)
        self.avg = float(self.dl.mean()) if self.N else 1.0
        self.inv = defaultdict(list)
        for i, t in enumerate(self._tok):
            for term, tf in Counter(t).items():
                self.inv[term].append((i, tf))
        self.vec = self.mat = self.dense = None
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
            self.mat = self.vec.fit_transform([c["text"] for c in chunks])
        except Exception:
            self.vec = None
        if embedding_model:
            try:
                from fastembed import TextEmbedding
                m = TextEmbedding(model_name=embedding_model)
                e = np.array(list(m.embed([c["text"] for c in chunks])), dtype=float)
                self.dense = (m, e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-9))
            except Exception:
                self.dense = None

    @staticmethod
    def _tokens(text):
        return re.findall(r"[a-z0-9\u00c0-\u024f]+", text.lower())

    @property
    def method(self):
        parts = ["BM25"] + (["character n-gram TF-IDF"] if self.vec is not None else []) + ([f"dense embeddings ({self.embedding_model})"] if self.dense else [])
        return " + ".join(parts) + ", reciprocal rank fusion"

    def stats(self):
        docs = Counter(c["doc"] for c in self.chunks)
        return {"chunks": self.N, "documents": dict(docs)}

    def _bm25(self, q_terms):
        s = np.zeros(self.N)
        for term in set(q_terms):
            post = self.inv.get(term)
            if not post:
                continue
            idf = math.log(1 + (self.N - len(post) + 0.5) / (len(post) + 0.5))
            for i, tf in post:
                s[i] += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * self.dl[i] / self.avg))
        return s

    def search(self, query, k=4):
        if not self.N:
            self.last = {"abstained": True, "coverage": 0.0}
            return []
        qt = self._tokens(query)
        scores = [self._bm25(qt)]
        if self.vec is not None:
            scores.append((self.mat @ self.vec.transform([query]).T).toarray().ravel())
        if self.dense:
            m, e = self.dense
            qv = np.array(next(iter(m.embed([query]))), dtype=float)
            scores.append(e @ (qv / (np.linalg.norm(qv) + 1e-9)))
        fused = np.zeros(self.N)
        for s in scores:
            for r, i in enumerate(np.argsort(-s)[:50]):
                if s[i] > 0:
                    fused[i] += 1 / (60 + r + 1)
        top = [int(i) for i in np.argsort(-fused)[:k] if fused[i] > 0]
        top = [i for i in top if fused[i] >= 0.5 * fused[top[0]]]  # drop weak tail matches
        q_stems = {w[:5] for w in qt if w not in STOP and len(w) > 2}
        cov = max((len(q_stems & {w[:5] for w in self._tok[i]}) / len(q_stems) for i in top), default=0.0) if q_stems else 0.0
        self.last = {"abstained": cov < self.min_coverage, "coverage": round(cov, 2)}
        if not top or cov < self.min_coverage:
            return []
        return [{"id": self.chunks[i]["id"], "source": f"{self.chunks[i]['title']}, page {self.chunks[i]['page']}", "text": self.chunks[i]["text"],
                 "score": round(float(fused[i]) * 60, 2), "doc": self.chunks[i]["doc"], "page": self.chunks[i]["page"], "topic": ""} for i in top]

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"chunks": self.chunks, "min_coverage": self.min_coverage, "embedding_model": self.embedding_model}, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        d = json.load(open(path, encoding="utf-8"))
        return cls(d["chunks"], d.get("min_coverage", 0.5), d.get("embedding_model"))


def index_path(code):
    return os.path.join(HERE, f"rag_index_{code}.json")


def get_index(code):
    """Session scoped index. Loads a saved index file if one exists."""
    import streamlit as st
    key = f"rag_{code}"
    if key not in st.session_state:
        p = index_path(code)
        try:
            st.session_state[key] = Index.load(p) if os.path.exists(p) else None
        except Exception:
            st.session_state[key] = None
    return st.session_state[key]


# ------------------------------------------------------------------ cited answers
def answer(question, hits, lang, api_key, model="claude-sonnet-5-5"):
    """Answer only from retrieved passages, with citations. Untested against the live API in the build environment."""
    msg = {"en": "I cannot find this in the indexed documents.", "sw": "Sijapata jibu hili kwenye nyaraka zilizoorodheshwa."}[lang]
    if not hits:
        return {"answer": msg, "cited": [], "abstained": True}
    import anthropic
    ids = {h["id"] for h in hits}
    passages = "\n\n".join(f"[{h['id']}] ({h['source']}) {h['text'][:1200]}" for h in hits)
    system = ("Answer the question using only the passages. Cite passage ids in square brackets after each claim. Paraphrase, quote at most a few words. "
              f"If the passages do not support an answer, reply exactly: {msg} Reply in the language of the question.")
    r = anthropic.Anthropic(api_key=api_key).messages.create(model=model, max_tokens=600, system=system,
                                                             messages=[{"role": "user", "content": f"Passages:\n{passages}\n\nQuestion: {question}"}])
    text = "".join(b.text for b in r.content if b.type == "text").strip()
    cited = [c for c in dict.fromkeys(re.findall(r"\[([^\]]+)\]", text)) if c in ids]
    if not cited and msg not in text:
        return {"answer": msg, "cited": [], "abstained": True}
    return {"answer": text, "cited": cited, "abstained": msg in text}


# ------------------------------------------------------------------ evaluation (starter cases: verify the gold phrases against the real text)
RAG_CASES = [
    {"q": "Which body supervises personal data protection in Tanzania?", "type": "answerable", "doc": "pdpa2022", "gold": ["personal data protection commission"], "min_page": 3},
    {"q": "Can personal data be transferred outside Tanzania?", "type": "answerable", "doc": "pdpa2022", "gold": ["transfer of personal data"], "min_page": 3},
    {"q": "What must a data collector do about the security of personal data?", "type": "answerable", "doc": "pdpa2022", "gold": ["security of personal data"], "min_page": 3},
    {"q": "How do I complain about a violation of personal data protection principles?", "type": "answerable", "doc": "pdpa2022", "gold": ["complaints against violation", "complaint"], "min_page": 3},
    {"q": "Strategic outcomes for epidemics and disaster preparedness", "type": "answerable", "doc": "hssp5", "gold": ["epidemic"], "min_page": 8},
    {"q": "What is the capital of France?", "type": "out_of_scope"},
    {"q": "Write a poem about football", "type": "out_of_scope"},
    {"q": "Bei ya mkate leo ni kiasi gani?", "type": "out_of_scope"},
]


def run_rag_eval(index, k=4):
    present = set(index.stats()["documents"])
    rows = []
    for c in RAG_CASES:
        if c["type"] == "answerable" and c["doc"] not in present:
            continue
        hits = index.search(c["q"], k)
        if c["type"] == "answerable":
            rank = next((i + 1 for i, h in enumerate(hits) if h["page"] >= c.get("min_page", 1) and any(g in h["text"].lower() for g in c["gold"])), None)
            rows.append({"question": c["q"], "type": c["type"], "result": f"found at rank {rank}" if rank else ("abstained" if not hits else "missed"),
                         "pass": rank is not None, "rr": 1 / rank if rank else 0.0})
        else:
            rows.append({"question": c["q"], "type": c["type"], "result": "abstained" if not hits else "answered anyway", "pass": not hits, "rr": 0.0})
    ans = [r for r in rows if r["type"] == "answerable"]
    oos = [r for r in rows if r["type"] != "answerable"]
    summary = {"Hit rate %": round(100 * sum(r["pass"] for r in ans) / len(ans)) if ans else None,
               "MRR": round(sum(r["rr"] for r in ans) / len(ans), 2) if ans else None,
               "Correct abstention %": round(100 * sum(r["pass"] for r in oos) / len(oos)) if oos else None,
               "Cases run": len(rows)}
    return rows, summary


# ------------------------------------------------------------------ UI
TXT = {
    "en": {"h": "Policy documents (RAG)", "docs": "Documents in this country pack", "build": "Build index from official links", "up": "Add your own PDFs or text files",
           "add": "Add uploaded files to the index", "test": "Search the documents", "ask": "Ask a question", "no_index": "No index yet. Build one from the links or upload files.",
           "abst": "No passage covers enough of the question, so the system abstains.", "stats": "Index", "eval": "Run retrieval evaluation", "dl": "Download index",
           "key": "Answer with a language model (key found in secrets)", "cap": "Answers are built only from indexed text and always cite document and page."},
    "sw": {"h": "Nyaraka za sera (RAG)", "docs": "Nyaraka katika kifurushi hiki cha nchi", "build": "Jenga faharasa kutoka viungo rasmi", "up": "Ongeza PDF au faili za maandishi",
           "add": "Ongeza faili ulizopakia kwenye faharasa", "test": "Tafuta kwenye nyaraka", "ask": "Uliza swali", "no_index": "Hakuna faharasa bado. Jenga kutoka viungo au pakia faili.",
           "abst": "Hakuna kifungu kinachotosha swali, kwa hiyo mfumo unajizuia kujibu.", "stats": "Faharasa", "eval": "Endesha tathmini ya utafutaji", "dl": "Pakua faharasa",
           "key": "Jibu kwa modeli ya lugha (ufunguo umepatikana)", "cap": "Majibu hutoka kwenye maandishi yaliyoorodheshwa tu na hutaja nyaraka na ukurasa."},
}


def render_policy_library(pack, lang):
    import streamlit as st
    import pandas as pd
    x = TXT[lang]
    st.header(f"📚 {x['h']}")
    st.caption(x["cap"])
    if not pack:
        st.info("No country pack.")
        return
    code, docs = pack["code"], pack.get("documents", [])
    store = st.session_state.setdefault(f"rag_pages_{code}", {})
    if docs:
        st.write(f"**{x['docs']}**")
        st.dataframe(pd.DataFrame([{"id": d["id"], "title": d["title"], "type": d["type"], "status": d["status"], "link": d.get("url") or "upload needed"} for d in docs]),
                     use_container_width=True, hide_index=True)
        for d in docs:
            if d.get("note"):
                st.caption(f"{d['id']}: {d['note']}")
    cfg = dict(min_coverage=pack.get("rag_min_coverage", 0.5), embedding_model=pack.get("embedding_model"))

    def rebuild():
        chunks = []
        for meta, pages in store.values():
            chunks += chunk_pages(meta, pages)
        idx = Index(chunks, **cfg)
        st.session_state[f"rag_{code}"] = idx
        try:
            idx.save(index_path(code))
        except Exception:
            pass
        return idx

    if st.button(x["build"], use_container_width=True, key=f"rag_build_{code}"):
        todo = [d for d in docs if d.get("url") and d["type"] != "data"]
        bar = st.progress(0.0)
        for n, d in enumerate(todo):
            try:
                store[d["id"]] = (d, fetch_pages(d["url"]))
            except Exception as e:
                st.error(f"{d['id']}: {e}")
            bar.progress((n + 1) / max(1, len(todo)))
        if store:
            rebuild()
    ups = st.file_uploader(x["up"], type=["pdf", "txt", "md"], accept_multiple_files=True, key=f"rag_up_{code}")
    if ups and st.button(x["add"], use_container_width=True, key=f"rag_add_{code}"):
        for f in ups:
            stem = re.sub(r"\W+", "_", os.path.splitext(f.name)[0]).lower()
            try:
                pages = pdf_pages(f.read()) if f.name.lower().endswith(".pdf") else text_pages(f.read().decode("utf-8", "ignore"))
                store[f"up_{stem}"] = ({"id": f"up_{stem}", "title": f.name, "status": "uploaded"}, pages)
            except Exception as e:
                st.error(f"{f.name}: {e}")
        if store:
            rebuild()
    idx = st.session_state.get(f"rag_{code}")
    if not idx:
        st.info(x["no_index"])
        return
    s = idx.stats()
    st.success(f"{x['stats']}: {s['chunks']} chunks | " + ", ".join(f"{k}: {v}" for k, v in s["documents"].items()))
    st.caption(idx.method)
    q = st.text_input(x["test"], key=f"rag_q_{code}")
    if q:
        hits = idx.search(q, 4)
        if not hits:
            st.warning(x["abst"] + f" (coverage {idx.last.get('coverage')})")
        key = None
        try:
            key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
        if key and hits:
            a = answer(q, hits, lang, key)
            st.write(a["answer"])
            st.caption("Cited: " + ", ".join(a["cited"]))
        for h in hits:
            with st.expander(f"{h['source']}  |  {h['id']}"):
                st.write(h["text"])
    if st.button(x["eval"], use_container_width=True, key=f"rag_eval_{code}"):
        rows, summ = run_rag_eval(idx)
        cols = st.columns(len(summ))
        for c, (k, v) in zip(cols, summ.items()):
            c.metric(k, "n/a" if v is None else v)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.download_button(x["dl"], open(index_path(code), "rb").read() if os.path.exists(index_path(code)) else b"{}", file_name=f"rag_index_{code}.json", key=f"rag_dl_{code}")
