import re
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rank_bm25 import BM25Okapi
import config

COLLECTION = "docs"


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.lower())
    return [(t.lstrip("0") or "0") if t.isdigit() else t for t in tokens]

def normalize_query(q: str) -> str:
    # "question 01" -> "question 1", "Q007" stays distinct from "Q7" only by design; adjust if needed
    return re.sub(r"\b0+(\d)", r"\1", q)

def rrf(rank_lists: list[list[int]], k: int = 60) -> list[int]:
    """Reciprocal Rank Fusion: merges rankings without needing comparable scores."""
    scores: dict[int, float] = {}
    for ranks in rank_lists:
        for r, idx in enumerate(ranks):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + r + 1)
    return sorted(scores, key=scores.get, reverse=True)


class HybridIndex:
    def __init__(self, embedder, reranker):
        self.embedder, self.reranker = embedder, reranker
        self.client = QdrantClient(":memory:")
        self.chunks, self.bm25 = [], None

    def build(self, chunks):
        self.chunks = chunks
        vecs = self.embedder.encode(
            [c.text for c in chunks], normalize_embeddings=True, batch_size=32
        )
        if self.client.collection_exists(COLLECTION):
            self.client.delete_collection(COLLECTION)
        self.client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=vecs.shape[1], distance=Distance.COSINE),
        )
        self.client.upsert(
            COLLECTION,
            [PointStruct(id=i, vector=v.tolist()) for i, v in enumerate(vecs)],
        )
        self.bm25 = BM25Okapi([tokenize(c.text) for c in chunks])

    def search(self, query: str, top_k: int = config.FINAL_K):
        query = normalize_query(query)
        qv = self.embedder.encode(config.QUERY_PREFIX + query, normalize_embeddings=True)
        dense = self.client.query_points(
            COLLECTION, query=qv.tolist(), limit=config.CANDIDATES
        ).points
        dense_ids = [int(p.id) for p in dense]

        bm = self.bm25.get_scores(tokenize(query))
        sparse_ids = [int(i) for i in np.argsort(bm)[::-1][: config.CANDIDATES] if bm[i] > 0]

        pool = rrf([dense_ids, sparse_ids])[: config.RERANK_POOL]
        scores = self.reranker.predict([(query, self.chunks[i].text) for i in pool])
        ranked = sorted(zip(pool, scores), key=lambda x: -x[1])[:top_k]
        return [(self.chunks[i], float(s)) for i, s in ranked]
