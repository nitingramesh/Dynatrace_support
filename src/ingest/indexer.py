from typing import Any, Dict, List

import chromadb
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm

from .chunk import chunk_text

def build_chunks(docs: List[Dict[str, Any]], chunk_size: int = 1600, overlap: int = 200):
    chunks = []
    for d in docs:
        topic = d.get("topic", "unknown")
        url = d.get("url", "")
        title = d.get("title", "")
        source_type = d.get("source_type", "docs")
        text = d.get("text", "")

        doc_chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        for i, ch in enumerate(doc_chunks):
            chunks.append({
                "id": f"{topic}::{i}::{url}",
                "text": ch,
                "metadata": {
                    "topic": topic,
                    "source_type": source_type,
                    "title": title,
                    "url": url,
                    "chunk_index": i,
                }
            })
    return chunks

def index_docs(
    docs: List[Dict[str, Any]],
    persist_dir: str = "chroma_db",
    collection_name: str = "dt_public_docs",
    model_name: str = "BAAI/bge-small-en-v1.5",
    batch_size: int = 32,
    reset: bool = True,
):
    chunks = build_chunks(docs)
    embedder = SentenceTransformer(model_name)
    client = chromadb.PersistentClient(path=persist_dir)

    if reset:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    col = client.get_or_create_collection(collection_name)

    for i in tqdm(range(0, len(chunks), batch_size)):
        batch = chunks[i:i+batch_size]
        texts = [b["text"] for b in batch]
        ids = [b["id"] for b in batch]
        metas = [b["metadata"] for b in batch]
        embs = embedder.encode(texts, normalize_embeddings=True).tolist()

        col.add(ids=ids, documents=texts, metadatas=metas, embeddings=embs)

    return {"docs": len(docs), "chunks": len(chunks), "collection": collection_name}
if __name__ == "__main__":
    import json

    with open("data/raw/docs.jsonl", "r", encoding="utf-8") as f:
        docs = [json.loads(line) for line in f if line.strip()]

    index_docs(
        docs=docs, 
        persist_dir="chroma_db", 
        collection_name="dt_public_docs", 
        reset=False
        )