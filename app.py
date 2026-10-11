import base64
import html
import pathlib
import time

import streamlit as st

USE_MOCK = False   # True = test the UI with no models or API key
SHOW_DEBUG = True  # show retrieval scores when the guardrail refuses

ICON_PATH = pathlib.Path(__file__).parent / "icon.png"
ICON_B64 = base64.b64encode(ICON_PATH.read_bytes()).decode() if ICON_PATH.exists() else None

st.set_page_config(
    page_title="Page Wise",
    page_icon=str(ICON_PATH) if ICON_PATH.exists() else "📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#F4F5F7;--surface:#fff;--surface-2:#FAFBFC;--hover:#F1F3F7;--ink:#161A22;--muted:#626B7A;
--line:#E3E6EB;--accent:#1F3FD1;--accent-strong:#1A35B0;--accent-soft:#E8ECFD;--on-accent:#fff;
--danger:#B42318;--danger-soft:#FEF3F2;--danger-line:#F9D3CF;--shadow:rgba(22,26,34,.06)}
@media (prefers-color-scheme:dark){:root{--bg:#0F1218;--surface:#171B24;--surface-2:#1C212C;--hover:#222836;
--ink:#E8EAF0;--muted:#98A1B2;--line:#2A303C;--accent:#7C97FF;--accent-strong:#9AB0FF;--accent-soft:#1F2850;
--on-accent:#0F1218;--danger:#FF8A80;--danger-soft:#2A1716;--danger-line:#4A2421;--shadow:rgba(0,0,0,.35)}}

.stApp,button,input,textarea{font-family:'Hanken Grotesk',-apple-system,'Segoe UI',sans-serif}
html body .stApp{background:var(--bg);color:var(--ink)}
html body .stApp :is(p,li,h1,h2,h3,h4,strong,em,label,td,th){color:inherit}

/* chrome */
html body #MainMenu,html body footer,html body [data-testid="stDecoration"],
html body [data-testid="stMainMenu"],html body [data-testid="stAppDeployButton"],
html body [data-testid="stToolbarActions"],html body [data-testid="stStatusWidget"]{display:none!important}
html body [data-testid="stToolbar"]{background:transparent}
html body [data-testid="stExpandSidebarButton"],html body [data-testid="stSidebarCollapsedControl"],
html body [data-testid="collapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important}
html body [data-testid="stExpandSidebarButton"],html body [data-testid="stSidebarCollapsedControl"] button,
html body [data-testid="collapsedControl"] button{background:var(--surface);border:1px solid var(--line);border-radius:9px}
html body [data-testid="stExpandSidebarButton"] *,html body [data-testid="stSidebarCollapsedControl"] *,
html body [data-testid="stSidebarCollapseButton"] *{color:var(--ink)}
html body header[data-testid="stHeader"]{background:transparent}
.block-container{padding:2.4rem 2.5rem 8rem;max-width:960px}

/* sidebar */
html body [data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--line);color:var(--ink)}
[data-testid="stSidebar"] .block-container,[data-testid="stSidebarUserContent"]{padding-top:1.4rem}
.brand{display:flex;align-items:center;gap:.85rem;margin-bottom:1.6rem}
html body .stApp a.brand{display:inline-flex;text-decoration:none;color:inherit;cursor:pointer}
.brand-text{display:flex;flex-direction:column;min-width:0}
html body [data-testid="stSidebarHeader"]{height:auto;min-height:0;padding:.7rem 1rem .2rem}
html body [data-testid="stSidebarUserContent"]{padding-top:.4rem}
html body .stApp a.brand:hover .brand-name{color:var(--accent)}
.brand-mark{flex:none;width:52px;height:52px;border-radius:12px;background:var(--accent);color:var(--on-accent);
display:grid;place-items:center;font-weight:700;font-size:1.05rem}
.brand-img{flex:none;width:52px;height:52px;border-radius:12px;object-fit:contain}
html body .stApp .brand-name{font-weight:700;font-size:1.3rem;letter-spacing:-.01em;line-height:1.2;color:var(--ink)}
html body .stApp .brand-sub{font-size:.8rem;line-height:1.3;margin-top:.1rem;color:var(--muted)}
html body .stApp .side-label{font-size:.8rem;font-weight:600;color:var(--muted);margin:1.2rem 0 .4rem}

/* uploader */
html body [data-testid="stFileUploader"] section{border:1.5px dashed var(--line);border-radius:12px;
background:var(--surface-2);padding:1rem;display:flex;flex-direction:column;align-items:center;
justify-content:center;text-align:center;gap:.7rem;min-height:160px}
html body [data-testid="stFileUploader"] section:hover{border-color:var(--accent);background:var(--accent-soft)}
[data-testid="stFileUploader"] section>div{display:flex;flex-direction:column;align-items:center;
justify-content:center;text-align:center;gap:.4rem}
html body [data-testid="stFileUploader"] section :is(small,span,p,div){color:var(--muted)}
html body [data-testid="stFileUploader"] section button,html body [data-testid="stFileUploader"] section button:focus{
background:var(--accent)!important;color:var(--on-accent)!important;border:0!important;margin:0 auto;
opacity:1!important;box-shadow:none!important;transition:background .15s ease}
html body [data-testid="stFileUploader"] section button:hover,html body [data-testid="stFileUploader"] section button:active{
background:var(--accent-strong)!important;color:var(--on-accent)!important;opacity:1!important}
html body [data-testid="stFileUploader"] section button *{color:var(--on-accent)!important}
html body [data-testid="stFileUploaderFile"],html body [data-testid="stFileUploaderFile"] *{color:var(--ink)}

.doc-card{border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;
padding:.7rem .85rem;margin-top:.8rem;background:var(--surface-2)}
html body .stApp .doc-name{font-weight:600;font-size:.9rem;word-break:break-all;color:var(--ink)}
html body .stApp .doc-meta{font-size:.78rem;color:var(--muted);margin-top:.15rem}

/* buttons */
html body .stButton>button{border-radius:9px;border:1px solid var(--line);background:var(--surface);color:var(--ink);
font-weight:600;padding:.5rem .9rem;transition:all .15s ease}
html body .stButton>button:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
html body .st-key-clear button{color:var(--danger);background:var(--danger-soft);border:1px solid var(--danger-line)}
html body .st-key-clear button:hover{color:var(--danger);border-color:var(--danger)}
html body .st-key-clear button:disabled{opacity:.45}

/* chat */
[data-testid="stChatMessageAvatarUser"],[data-testid="stChatMessageAvatarAssistant"]{display:none}
html body [data-testid="stChatMessage"]{background:transparent;border:0;padding:.55rem 0;color:var(--ink)}
html body [data-testid="stChatMessage"]:has(.role-user){background:var(--surface);border:1px solid var(--line);
border-radius:14px;padding:.8rem 1rem;margin-left:auto;width:fit-content;max-width:75%}
html body [data-testid="stChatMessage"]:has(.role-assistant){border-left:2px solid var(--accent);
border-radius:0;padding-left:1rem;margin-right:6%}
.role-user,.role-assistant{display:none}
[data-testid="stChatMessage"] p{line-height:1.65}
html body [data-testid="stBottom"]>div,html body [data-testid="stBottomBlockContainer"]{background:var(--bg)}
html body [data-testid="stChatInput"]>div{border-radius:14px;border:1px solid var(--line);background:var(--surface);
box-shadow:0 2px 10px var(--shadow);transition:border-color .15s,box-shadow .15s}
html body [data-testid="stChatInput"]>div:focus-within{border-color:var(--accent)}
html body [data-testid="stChatInput"] textarea{background:transparent;font-size:.98rem;color:var(--ink)!important;
-webkit-text-fill-color:var(--ink)}
html body [data-testid="stChatInput"] textarea::placeholder{color:var(--muted)!important;
-webkit-text-fill-color:var(--muted);opacity:1}
html body [data-testid="stChatInput"] button{background:var(--accent);color:var(--on-accent)}

/* sources + status */
html body [data-testid="stExpander"]{border:1px solid var(--line);border-radius:10px;background:var(--surface);margin-top:.5rem}
html body [data-testid="stExpander"] details,html body [data-testid="stExpander"] summary,
html body [data-testid="stExpanderDetails"]{background:var(--surface);color:var(--ink);border-radius:10px}
html body [data-testid="stExpander"] summary:hover{background:var(--hover)}
html body [data-testid="stExpander"] summary *{color:var(--ink)}
html body [data-testid="stExpander"] summary{font-weight:600;font-size:.9rem}
.src{border-top:1px solid var(--line);padding:.7rem 0}
.src:first-child{border-top:0;padding-top:.2rem}
html body .stApp .src-head{display:flex;gap:.5rem;align-items:center;font-size:.82rem;color:var(--muted);margin-bottom:.35rem}
html body .stApp .src-page{background:var(--accent-soft);color:var(--accent);font-weight:700;border-radius:6px;padding:.1rem .5rem}
html body .stApp .src-text{font-size:.86rem;line-height:1.55;color:var(--ink);max-height:9.5rem;overflow:auto;
background:var(--surface-2);border-radius:8px;padding:.55rem .7rem}

/* empty state */
.hero{padding:3.5rem 0 1.5rem}
html body .stApp .hero h1{font-size:2.4rem;font-weight:700;letter-spacing:-.025em;margin:0 0 .6rem;line-height:1.1;color:var(--ink)}
html body .stApp .hero p{font-size:1.05rem;color:var(--muted);max-width:34rem;line-height:1.6;margin:0 0 2rem}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;max-width:44rem}
.step{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem}
html body .stApp .step b{display:block;margin-bottom:.25rem;color:var(--ink)}
html body .stApp .step span{font-size:.88rem;color:var(--muted);line-height:1.5}
@media(max-width:700px){.steps{grid-template-columns:1fr}
[data-testid="stChatMessage"]:has(.role-user){margin-left:0}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.session_state.setdefault("messages", [])


# ------------------------------------------------------------------ backend
def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def mock_rag_pipeline(query):
    """Dummy answer + sources so the UI can be tested with no backend."""
    answer = (
        f"This is a simulated answer to “{query}”. In the real pipeline the text "
        "comes from the language model, grounded only in the passages below (Source: sample.pdf, Page 3)."
    )
    sources = [
        {"source": "sample.pdf", "page": 3, "score": 4.21,
         "text": "Employees are eligible for a 401(k) match of up to 5% of base salary after 90 days."},
        {"source": "sample.pdf", "page": 12, "score": 2.07,
         "text": "Matching contributions vest over three years, with one third vesting each anniversary."},
    ]
    return answer, sources


@st.cache_resource(show_spinner=False)
def load_models():
    from sentence_transformers import CrossEncoder, SentenceTransformer
    import config
    return SentenceTransformer(config.EMBED_MODEL), CrossEncoder(config.RERANK_MODEL)


def index_document(pdf):
    """Returns (index, n_chunks, n_pages)."""
    if USE_MOCK:
        time.sleep(1.2)
        return "mock", 42, 12
    from ingest import chunk_pages, load_pdf
    from retriever import HybridIndex
    embedder, reranker = load_models()
    pages = load_pdf(pdf.getvalue())
    chunks = chunk_pages(pages, pdf.name)
    if not chunks:
        raise ValueError("No readable text found. Scanned PDFs need OCR first.")
    index = HybridIndex(embedder, reranker)
    index.build(chunks)
    return index, len(chunks), len(pages)


def answer_query(index, query):
    """Returns (stream_or_None, sources, debug_hits). None means the guardrail refused."""
    if USE_MOCK:
        answer, sources = mock_rag_pipeline(query)
        return stream_text(answer), sources, []
    from rag import retrieve, stream_answer
    hits, relevant = retrieve(index, query)
    if not relevant:
        return None, [], hits
    sources = [{"source": c.source, "page": c.page, "score": s, "text": c.text} for c, s in relevant]
    return stream_answer(query, relevant), sources, hits


def refusal_text():
    if USE_MOCK:
        return "I don't have enough information in the provided documents to answer that."
    import config
    return config.REFUSAL


# ------------------------------------------------------------------ UI helpers
def render_sources(sources):
    if not sources:
        return
    with st.expander(f"📄 View Sources ({len(sources)})"):
        blocks = "".join(
            f"""<div class="src"><div class="src-head"><span class="src-page">Page {s['page']}</span>
            <span>{html.escape(s['source'])}</span><span>· match {s['score']:.2f}</span></div>
            <div class="src-text">{html.escape(s['text'])}</div></div>"""
            for s in sources
        )
        st.markdown(blocks, unsafe_allow_html=True)


def render_html(markup):
    if hasattr(st, "html"):
        st.html(markup)
    else:
        st.markdown(markup, unsafe_allow_html=True)


def clear_chat():
    st.session_state.messages = []


def ask(text):
    st.session_state.pending = text


def reset_document():
    for k in ("index", "loaded", "n_chunks", "n_pages"):
        st.session_state.pop(k, None)
    st.session_state.messages = []


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    mark = (
        f'<img class="brand-img" src="data:image/png;base64,{ICON_B64}">'
        if ICON_B64 else '<span class="brand-mark">P</span>'
    )
    render_html(
        f'<a class="brand" href="./" target="_self">{mark}<span class="brand-text">'
        '<span class="brand-name">Page Wise</span>'
        '<span class="brand-sub">Answers with page citations</span></span></a>'
    )
    pdf = st.file_uploader("Upload a PDF", type="pdf", label_visibility="collapsed")

    if pdf is None and "loaded" in st.session_state:
        reset_document()

    if pdf is not None and st.session_state.get("loaded") != pdf.name:
        try:
            with st.status("Indexing document...", expanded=False) as status:
                index, n_chunks, n_pages = index_document(pdf)
                status.update(label="Document ready", state="complete")
            st.session_state.update(
                index=index, loaded=pdf.name, n_chunks=n_chunks, n_pages=n_pages, messages=[]
            )
            st.toast("Document indexed", icon="✅")
        except Exception as e:
            st.error(f"Couldn't read this PDF. {e}")

    if "loaded" in st.session_state:
        st.markdown(
            f'<div class="doc-card"><div class="doc-name">{html.escape(st.session_state.loaded)}</div>'
            f'<div class="doc-meta">{st.session_state.n_pages} pages · '
            f'{st.session_state.n_chunks} passages indexed</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="side-label">Conversation</div>', unsafe_allow_html=True)
    st.button(
        "Clear chat history", key="clear", on_click=clear_chat,
        disabled=not st.session_state.messages, use_container_width=True,
    )

# ------------------------------------------------------------------ main
has_doc = "index" in st.session_state

if not has_doc:
    st.markdown(
        """<div class="hero"><h1>Ask your documents anything.</h1>
        <p>Upload a PDF and get answers written from its own text, each one linked to the pages it came from.</p>
        <div class="steps">
        <div class="step"><b>1. Upload</b><span>Add a text-based PDF in the sidebar.</span></div>
        <div class="step"><b>2. Ask</b><span>Type a question in plain language.</span></div>
        <div class="step"><b>3. Verify</b><span>Open View Sources to check the exact passages.</span></div>
        </div></div>""",
        unsafe_allow_html=True,
    )
elif not st.session_state.messages:
    st.markdown(
        f'<div class="hero" style="padding-top:2rem"><h1>{html.escape(st.session_state.loaded)}</h1>'
        "<p>Ready. Ask a question below, or start with one of these.</p></div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for col, text in zip(cols, ["Summarize the main points", "What are the key deadlines?",
                                "List the main requirements"]):
        col.button(text, key=f"s_{text}", on_click=ask, args=(text,), use_container_width=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<span class="role-{m["role"]}"></span>', unsafe_allow_html=True)
        st.markdown(m["content"])
        render_sources(m.get("sources"))

typed = st.chat_input(
    "Ask a question about your document" if has_doc else "Upload a PDF to start asking questions",
    disabled=not has_doc,
)
query = (typed or st.session_state.pop("pending", None) or "").strip()

if query:
    if not has_doc:
        st.warning("Upload a PDF in the sidebar before asking a question.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown('<span class="role-user"></span>', unsafe_allow_html=True)
            st.markdown(query)

        with st.chat_message("assistant"):
            st.markdown('<span class="role-assistant"></span>', unsafe_allow_html=True)
            try:
                with st.status("Analyzing document...", expanded=False) as status:
                    stream, sources, hits = answer_query(st.session_state.index, query)
                    status.update(
                        label=f"Found {len(sources)} relevant passage{'s' if len(sources) != 1 else ''}"
                        if sources else "No relevant passages found",
                        state="complete",
                    )
                if stream is None:
                    answer = refusal_text()
                    st.markdown(answer)
                    if SHOW_DEBUG and hits:
                        with st.expander("Debug: closest passages"):
                            for c, s in hits:
                                st.write(f"**score {s:.2f}**, page {c.page}")
                                st.caption(c.text[:300])
                else:
                    answer = st.write_stream(stream)
                    render_sources(sources)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as e:
                st.error(f"Something went wrong while answering. {e}")