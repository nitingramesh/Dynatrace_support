from typing import Optional, Dict, Any, List, Tuple

import chromadb
from sentence_transformers import SentenceTransformer

# dynatrace-support-copilot/src/retrieval/search.py

import textwrap
import re


def clean_snippet(text: str, url: str = "", max_chars: int = 380, width: int = 92) -> str:
    if not text:
        return ""

    s = text.strip()

    # Remove URL if it appears verbatim in the snippet
    if url:
        s = s.replace(url, "")

    # Collapse whitespace/newlines
    s = re.sub(r"\s+", " ", s).strip()

    # Trim length
    if len(s) > max_chars:
        s = s[:max_chars].rsplit(" ", 1)[0] + "..."

    # Wrap for terminal readability
    return textwrap.fill(s, width=width)


class Retriever:
    def __init__(
        self,
        persist_dir: str = "chroma_db",
        collection_name: str = "dt_public_docs",
        model_name: str = "BAAI/bge-small-en-v1.5",
    ):
        self.embedder = SentenceTransformer(model_name)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.col = self.client.get_or_create_collection(collection_name)

    def query(self, q: str, topic: Optional[str] = None, k: int = 5):
        q_emb = self.embedder.encode([q], normalize_embeddings=True).tolist()
        where = {"topic": topic} if topic else None

        results = self.col.query(
            query_embeddings=q_emb,
            n_results=max(k * 3, 15),
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        enriched = []
        query_terms = q.lower().split()

        for doc, meta, dist in zip(docs, metas, dists):
            text = (doc or "").lower()
            title = (meta or {}).get("title", "")
            url = (meta or {}).get("url", "")

            keyword_score = 0

            for term in query_terms:
                if term in title.lower():
                    keyword_score += 3
                if term in url.lower():
                    keyword_score += 4
                if term in text:
                    keyword_score += 1

            embedding_score = 1 - dist
            final_score = embedding_score + (0.15 * keyword_score)

            enriched.append({
                "text": doc,
                "title": title,
                "url": url,
                "topic": (meta or {}).get("topic", ""),
                "score": final_score,
                "distance": dist,
                "metadata": meta or {},
            })

        enriched.sort(key=lambda x: x["score"], reverse=True)

        seen_urls = set()
        final_docs = []

        for item in enriched:
            url = item.get("url")

            if url and url in seen_urls:
                continue

            if url:
                seen_urls.add(url)

            final_docs.append(item)

            if len(final_docs) >= k:
                break

        return final_docs


def format_support_pack(res: Dict[str, Any]) -> str:
    """
    Format retrieval results into a readable support report.
    """

    if not res or not res.get("documents"):
        return "No relevant documents found."

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    lines = []
    lines.append("=== Dynatrace Support Copilot (POC) ===")
    lines.append("")

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists), start=1):

        title = meta.get("title", "Untitled")
        url = meta.get("url", "")
        topic = meta.get("topic", "unknown")

        confidence = round(1 - float(dist), 3)

        lines.append(f"[{i}] {topic.upper()} | conf={confidence}")
        lines.append(f"Title: {title}")

        if url:
            lines.append(f"URL: {url}")

        lines.append("")
        lines.append("Snippet:")
        lines.append(doc.strip())
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)