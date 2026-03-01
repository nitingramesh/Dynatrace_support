from typing import Optional, Dict, Any, List, Tuple

import chromadb
from sentence_transformers import SentenceTransformer

# dynatrace-support-copilot/src/retrieval/search.py

from typing import Optional, Dict, Any
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
            n_results=15,   # pull more for reranking
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        enriched = []
        query_terms = q.lower().split()

        for doc, meta, dist in zip(docs, metas, dists):

            text = doc.lower()
            keyword_score = sum(1 for term in query_terms if term in text)

            # embedding similarity (distance smaller = better)
            embedding_score = 1 - dist

            final_score = embedding_score + (0.15 * keyword_score)

            enriched.append({
                "doc": doc,
                "meta": meta,
                "dist": dist,
                "score": final_score
            })

        # Sort by new score
        enriched.sort(key=lambda x: x["score"], reverse=True)

        top = enriched[:k]

        # Build deduped results with confidence
        seen_urls = set()
        items = []

        for x in top:
            meta = x["meta"]
            doc = x["doc"]
            dist = x["dist"]

            url = (meta or {}).get("url")
            if not url:
                continue
            if url in seen_urls:
                continue

            confidence = round(1 - float(dist), 3)  # simple proxy
            items.append((meta, doc, confidence))
            seen_urls.add(url)

        # If nothing matched, return a friendly message (NOT None)
        if not items:
            return "\nNo results found for that query/topic.\n"

        lines: List[str] = []
        lines.append("\n==============================")
        lines.append("Dynatrace Support Copilot (POC)")
        lines.append("==============================\n")

        # top sources
        lines.append("Top Sources:\n")
        for i, (m, doc, conf) in enumerate(items, start=1):
            title = m.get("title", "Untitled")
            url = m.get("url", "")
            topic_val = m.get("topic", "")
            lines.append(f"   Confidence: {conf}")
            lines.append(f"{i}. [{topic_val.upper()}] {title}")
            if url:
                lines.append(f"   🔗 {url}")
            lines.append("")

        # evidence snippets
        lines.append("")
        lines.append("Evidence Snippets:")
        lines.append("==================")

        for i, (m, doc, conf) in enumerate(items, start=1):
            title = m.get("title", "Untitled")
            url = m.get("url", "")
            topic_val = m.get("topic", "")

            lines.append(f"\n[{i}] {topic_val.upper()} | conf={conf}")
            lines.append(f"Title: {title}")
            if url:
                lines.append(f"URL:   {url}")

            snippet = clean_snippet(doc, url=url)
            if snippet:
                lines.append("Snippet:")
                lines.append("  " + snippet.replace("\n", "\n  "))
            else:
                lines.append("Snippet: (empty)")
            lines.append("")

        return "\n".join(lines)
from typing import Dict, Any

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
