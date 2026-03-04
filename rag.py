import hashlib
import re
from pathlib import Path
from docx import Document

PROMPT_V = "1"


def _hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def normalize_query(q):
    q = q.lower().strip()
    q = re.sub(r"\s+", " ", q)
    return q


def stable_filters(filters):
    if not filters:
        return ""
    items = [f"{k}={filters[k]}" for k in sorted(filters.keys())]
    return "&".join(items)


# Retrieval cache key: normalized query + filters
def retrieval_cache_key(query, filters):
    return f"retrieval|q={normalize_query(query)}|f={stable_filters(filters)}"


# Response cache key: query + context hash + prompt version
def response_cache_key(query, ctx_hash):
    return f"response|q={normalize_query(query)}|ctx={ctx_hash}|pv={PROMPT_V}"


def context_hash(chunks):
    s = "|".join([f"{c['doc_id']}:{c['doc_version']}:{c['chunk_id']}" for c in chunks])
    return _hash(s)


def load_docs(folder_path):
    folder = Path(folder_path)
    docs = []
    versions = []

    for file in sorted(folder.glob("*.docx")):
        doc = Document(str(file))
        text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

        doc_version = _hash(text)

        docs.append({
            "doc_id": file.name,
            "text": text,
            "version": doc_version
        })

        versions.append(f"{file.name}:{doc_version}")

    corpus_version = _hash("|".join(versions))
    return docs, corpus_version


def retrieve(query, docs, k=2):
    q_words = set(normalize_query(query).split())
    scored = []

    for d in docs:
        paragraphs = [p.strip() for p in d["text"].split("\n") if p.strip()]

        for i, para in enumerate(paragraphs):
            p_words = set(normalize_query(para).split())
            score = len(q_words & p_words)

            if score > 0:
                scored.append((score, {
                    "doc_id": d["doc_id"],
                    "doc_version": d["version"],
                    "chunk_id": i,
                    "text": para
                }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]


def generate_answer(query, chunks):
    if not chunks:
        return f"PROMPT_V={PROMPT_V}\nQ: {query}\nNo relevant text found.\n"

    lines = [
        f"PROMPT_V={PROMPT_V}",
        f"Q: {query}",
        "Context:"
    ]

    for c in chunks:
        lines.append(f"- {c['doc_id']}: {c['text']}")

    return "\n".join(lines)