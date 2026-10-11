import os
import config

# Langfuse is optional: tracing switches on only if keys are set.
try:
    from langfuse import observe
except Exception:  # pragma: no cover
    def observe(*a, **k):
        return (lambda f: f) if not (a and callable(a[0])) else a[0]

if os.getenv("LANGFUSE_PUBLIC_KEY"):
    from langfuse.openai import OpenAI  # auto-traces latency + token usage
else:
    from openai import OpenAI

_client = None

SYSTEM = f"""You answer questions using ONLY the numbered context passages.
Cite every claim like (Source: <file>, Page <n>).
If the passages do not contain the answer, reply exactly: {config.REFUSAL}
Never use outside knowledge."""


def client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url=config.GROQ_BASE_URL)
    return _client


@observe(name="retrieve")
def retrieve(index, query: str):
    """Returns (all_hits, relevant_hits). Guardrail: drop chunks below the rerank threshold."""
    hits = index.search(query)
    relevant = [(c, s) for c, s in hits if s >= config.MIN_RERANK_SCORE]
    return hits, relevant


def stream_answer(query: str, relevant):
    context = "\n\n".join(
        f"[{i+1}] (Source: {c.source}, Page {c.page})\n{c.text}"
        for i, (c, _) in enumerate(relevant)
    )
    stream = client().chat.completions.create(
        model=config.LLM_MODEL,
        temperature=0,
        stream=True,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    for event in stream:
        delta = event.choices[0].delta.content
        if delta:
            yield delta
