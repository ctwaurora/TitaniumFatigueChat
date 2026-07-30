import json
from pathlib import Path
from typing import Dict, List

from .pdf_skill import extract_text_from_pdf, chunk_text


CHUNKS_PATH = Path("data/chunks.jsonl")


def _load_chunks() -> List[Dict]:
    if not CHUNKS_PATH.exists():
        return []

    chunks = []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                chunks.append(json.loads(line))
            except Exception:
                continue
    return chunks


def _save_chunks(chunks: List[Dict]) -> None:
    CHUNKS_PATH.parent.mkdir(exist_ok=True)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for item in chunks:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def index_pdf_chunks(file_path: str, file_hash: str) -> int:
    text = extract_text_from_pdf(file_path)
    pieces = chunk_text(text, chunk_size=1000, overlap=150)

    old_chunks = _load_chunks()
    old_chunks = [c for c in old_chunks if c.get("file_hash") != file_hash]

    source_file = Path(file_path).name
    new_chunks = []

    for i, piece in enumerate(pieces):
        new_chunks.append(
            {
                "chunk_id": f"{file_hash}_{i}",
                "file_hash": file_hash,
                "source_file": source_file,
                "text": piece,
            }
        )

    all_chunks = old_chunks + new_chunks
    _save_chunks(all_chunks)

    return len(new_chunks)


def keyword_retrieve(query: str, top_k: int = 5) -> List[Dict]:
    chunks = _load_chunks()
    if not chunks:
        return []

    query_terms = [t.strip().lower() for t in query.replace("，", " ").replace(",", " ").split() if t.strip()]

    scored = []
    for chunk in chunks:
        text = chunk.get("text", "")
        lower_text = text.lower()

        score = 0
        for term in query_terms:
            if term and term in lower_text:
                score += 1

        for char in query:
            if "\u4e00" <= char <= "\u9fff" and char in text:
                score += 0.1

        if score > 0:
            item = dict(chunk)
            item["score"] = score
            scored.append(item)

    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored[:top_k]


def get_evidence_text(query: str, top_k: int = 5) -> str:
    results = keyword_retrieve(query, top_k=top_k)
    parts = []
    for i, item in enumerate(results):
        parts.append(
            f"[证据{i+1}] 来源：{item.get('source_file', '未知')}\n{item.get('text', '')}"
        )
    return "\n\n".join(parts)