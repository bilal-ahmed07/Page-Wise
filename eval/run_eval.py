"""Retrieval hit-rate@3 over a hand-labelled golden set.
Usage: python eval/run_eval.py path/to/doc.pdf
Also reports how many UNANSWERABLE questions the guardrail correctly rejects.
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from sentence_transformers import SentenceTransformer, CrossEncoder
import config
from ingest import load_pdf, chunk_pages
from retriever import HybridIndex

path = pathlib.Path(sys.argv[1])
index = HybridIndex(SentenceTransformer(config.EMBED_MODEL), CrossEncoder(config.RERANK_MODEL))
index.build(chunk_pages(load_pdf(path.read_bytes()), path.name))

golden = json.load(open(pathlib.Path(__file__).with_name("golden.json")))
hits = 0
for g in golden:
    pages = {c.page for c, _ in index.search(g["question"])}
    hits += g["expected_page"] in pages
print(f"Hit-rate@{config.FINAL_K}: {hits}/{len(golden)} = {hits/len(golden):.0%}")

# Guardrail check: questions the document cannot answer
offtopic = ["What is the capital of Australia?", "Who won the 2018 World Cup?"]
rejected = sum(all(s < config.MIN_RERANK_SCORE for _, s in index.search(q)) for q in offtopic)
print(f"Guardrail rejected {rejected}/{len(offtopic)} off-topic questions")
