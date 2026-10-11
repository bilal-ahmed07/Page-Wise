from dataclasses import dataclass
import pymupdf as fitz  # PyMuPDF
import config


@dataclass
class Chunk:
    text: str
    source: str
    page: int


def load_pdf(data: bytes) -> list[tuple[int, str]]:
    doc = fitz.open(stream=data, filetype="pdf")
    return [(i + 1, page.get_text()) for i, page in enumerate(doc)]


def chunk_pages(pages, source: str) -> list[Chunk]:
    """Sliding word window per page, so every chunk maps to exactly one page."""
    chunks, step = [], config.CHUNK_WORDS - config.CHUNK_OVERLAP
    for page_no, text in pages:
        words = text.split()
        for start in range(0, max(len(words), 1), step):
            piece = " ".join(words[start:start + config.CHUNK_WORDS])
            if len(piece.split()) >= 15:  # drop headers/page-number noise
                chunks.append(Chunk(piece, source, page_no))
            if start + config.CHUNK_WORDS >= len(words):
                break
    return chunks
