# Document Assistant

A production-ready RAG assistant featuring hybrid search, cross-encoder reranking, and hallucination guardrails.

![demo](docs/demo.gif)

## Quickstart
```bash
pip install -r requirements.txt
export GROQ_API_KEY=...        # free key from console.groq.com
streamlit run app.py
```
Optional: set `LANGFUSE_*` keys (see `.env.example`) to trace every query.

## Architecture
![architecture](docs/architecture.png)

Ingestion: PDF → page-aware chunker → bge-small embeddings → Qdrant (+ BM25 index)
Generation: Query → dense + BM25 → RRF fusion → cross-encoder rerank (top 10 → 3) → relevance guardrail → Llama 3.3 70B (streamed) → cited answer

## Engineering trade-offs
- **Chunk size (200 words, 40 overlap):** TODO – fill in with your measured hit-rate at 100 / 200 / 400 words.
- **Why rerank:** TODO – report hit-rate@3 with and without the cross-encoder.
- **Why hybrid:** dense search misses exact tokens (part numbers, clause IDs); BM25 catches them. RRF fuses without score calibration.
- **Guardrail threshold:** TODO – how you picked `MIN_RERANK_SCORE` from `eval/run_eval.py`.

## Evaluation
`python eval/run_eval.py doc.pdf` → hit-rate@3 and guardrail rejection rate.
