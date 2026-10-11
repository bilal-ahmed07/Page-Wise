"""Retrieval evaluation.

Usage:  python eval/run_eval.py path/to/document.pdf

golden.json entries:
  {"question": "...", "expected_page": 3}          answerable (page number, or a list of pages)
  {"question": "...", "expected_page": null}       unanswerable: the guardrail should refuse
Page numbers are the PDF viewer's page index (1 = first page), the same numbers the app cites.
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from sentence_transformers import CrossEncoder, SentenceTransformer

import config
import retriever
from ingest import chunk_pages, load_pdf
from retriever import COLLECTION, HybridIndex, rrf, tokenize

K = config.FINAL_K
path = pathlib.Path(sys.argv[1])
index = HybridIndex(SentenceTransformer(config.EMBED_MODEL), CrossEncoder(config.RERANK_MODEL))
chunks = chunk_pages(load_pdf(path.read_bytes()), path.name)
index.build(chunks)
print(f"{path.name}: {len(chunks)} chunks (CHUNK_WORDS={config.CHUNK_WORDS}, overlap={config.CHUNK_OVERLAP})\n")

golden = json.load(open(pathlib.Path(__file__).with_name("golden.json")))
answerable = [g for g in golden if g.get("expected_page") is not None]
unanswerable = [g for g in golden if g.get("expected_page") is None]
norm = getattr(retriever, "normalize_query", lambda q: q)


def expected(g):
    p = g["expected_page"]
    return set(p if isinstance(p, list) else [p])


def dense_ids(q):
    qv = index.embedder.encode(config.QUERY_PREFIX + q, normalize_embeddings=True)
    pts = index.client.query_points(COLLECTION, query=qv.tolist(), limit=config.CANDIDATES).points
    return [int(p.id) for p in pts]


def sparse_ids(q):
    bm = index.bm25.get_scores(tokenize(q))
    return [int(i) for i in np.argsort(bm)[::-1][: config.CANDIDATES] if bm[i] > 0]


def pages(ids):
    return [index.chunks[i].page for i in ids[:K]]


methods = {
    "Dense only": lambda q: pages(dense_ids(q)),
    "BM25 only": lambda q: pages(sparse_ids(q)),
    "Hybrid (dense + BM25, RRF)": lambda q: pages(rrf([dense_ids(q), sparse_ids(q)])),
    "Hybrid + reranker": lambda q: [c.page for c, _ in index.search(q)],
}

n = len(answerable)
print(f"Hit-rate@{K} on {n} answerable questions (paste into the README table)\n")
print("| Configuration | Hit-rate@%d |\n|---|---|" % K)
for name, fn in methods.items():
    hits = sum(bool(set(fn(norm(g["question"]))) & expected(g)) for g in answerable)
    print(f"| {name} | {hits}/{n} = {hits / n:.0%} |")

floor = config.MIN_RERANK_SCORE


def best_score(q):
    hits = index.search(q)
    return hits[0][1] if hits else float("-inf")


wrong_refusals = sum(best_score(g["question"]) < floor for g in answerable)
correct_refusals = sum(best_score(g["question"]) < floor for g in unanswerable)
print(f"\nGuardrail floor = {floor}")
print(f"Answerable questions wrongly blocked: {wrong_refusals}/{n}")
print(f"Unanswerable questions blocked:       {correct_refusals}/{len(unanswerable)}")
print("(Anything not blocked here still gets a second check from the LLM's refusal instruction.)")