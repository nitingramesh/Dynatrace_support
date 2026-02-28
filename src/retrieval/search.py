from typing import Optional, Dict, Any, List, Tuple

import chromadb
from sentence_transformers import SentenceTransformer


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

        return self.col.query(
            query_embeddings=q_emb,
            n_results=k,
            where=where,
        )


def format_support_pack(res: Dict[str, Any]) -> str:
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    lines: List[str] = []
    lines.append("\n==============================")
    lines.append("Dynatrace Support Copilot (POC)")
    lines.append("==============================\n")

    # top sources
    lines.append("Top Sources:\n")
    for i, m in enumerate(metas, start=1):
        title = m.get("title", "Untitled")
        url = m.get("url", "")
        topic = m.get("topic", "")
        lines.append(f"{i}. [{topic.upper()}] {title}")
        if url:
            lines.append(f"   🔗 {url}")
        lines.append("")

    # evidence snippets
    lines.append("Evidence Snippets:\n")
    for i, (d, m) in enumerate(zip(docs, metas), start=1):
        snippet = (d or "").strip().replace("\n", " ")
        snippet = snippet[:400]
        lines.append(f"{i}) {snippet}...")
        
        url = m.get("url", "")
        if url:
            lines.append(f"   Read full documentation → {url}")
        lines.append("")
    return "\n".join(lines)
