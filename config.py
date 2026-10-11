EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

CHUNK_WORDS = 200        # ~250-300 tokens: big enough for context, small enough to stay precise
CHUNK_OVERLAP = 40       # preserves sentences that straddle a boundary
CANDIDATES = 20          # fetched from each of dense + BM25
RERANK_POOL = 10         # fused candidates passed to the cross-encoder
FINAL_K = 3              # chunks sent to the LLM
MIN_RERANK_SCORE = -9.0   # guardrail threshold: TUNE with eval/run_eval.py

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
REFUSAL = "I don't have enough information in the provided documents to answer that."
