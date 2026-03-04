

from src.llm import generate_answer
from src.retrieval.search import Retriever

import json, os, hashlib

CACHE_PATH = "answer_cache.json"

def cache_key(topic: str | None, q: str, model: str) -> str:
    raw = f"{model}::{topic or 'all'}::{q.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

TOPICS = ["kubernetes", "oneagent", "dem"]
def normalize_topic(raw: str):
    s = (raw or "").strip().lower()

    if s in ("", "all", "*"):
        return None  # your Retriever expects None for "all topics"

    if s in ("kubernetes", "k8s", "kube"):
        return "kubernetes"

    if s in ("oneagent", "oa"):
        return "oneagent"

    if s in ("dem",):
        return "dem"

    if s == "exit":
        return "exit"

    return "INVALID"

import re

def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://\S+", text or "")
    # clean trailing punctuation
    cleaned = []
    for u in urls:
        u = u.rstrip(").,;]")
        cleaned.append(u)
    # dedupe preserve order
    seen = set()
    out = []
    for u in cleaned:
        if u not in seen:
            out.append(u)
            seen.add(u)
    return out

def build_llm_context(res_text: str) -> tuple[str, list[str]]:
    """
    Returns:
      context_for_llm: str  (includes numbered sources + evidence)
      urls: list[str]       (same order as [1], [2], ...)
    """
    urls = extract_urls(res_text)

    sources_block = ["SOURCES (cite using [1], [2], ...):"]
    for i, u in enumerate(urls, start=1):
        sources_block.append(f"[{i}] {u}")

    # Keep evidence readable: remove overly noisy whitespace
    evidence = (res_text or "").strip()
    evidence = re.sub(r"\n{3,}", "\n\n", evidence)

    context = "\n".join(sources_block) + "\n\nEVIDENCE (use only this):\n" + evidence
    return context, urls

def confidence_from_urls(urls: list[str]) -> str:
    n = len(urls)
    if n >= 4:
        return "High"
    if n >= 2:
        return "Medium"
    return "Low"

def startup_banner():
    print("""
============================================
            TraceSage AI
 Documentation Intelligence Assistant
============================================
KB       : data/seed_urls.txt
VectorDB : chroma_db (Chroma)
LLM      : llama3.1:8b (Ollama)
============================================
""".strip())
    print()

    
DOCS_JSONL_PATH = "data/raw/docs.jsonl"

def read_docs_jsonl():
    """Loads docs from docs.jsonl (each line is a JSON object)."""
    docs = []
    if not os.path.exists(DOCS_JSONL_PATH):
        return docs
    with open(DOCS_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                docs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return docs

#keyword fall back context if retrieval misses key docs. This scans docs.jsonl for keyword matches and returns the most relevant full doc texts as fallback context for the LLM.
def keyword_fallback_context(question: str, max_docs: int = 2) -> str:
    import re

STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","as","by","at","from","is","are","was","were",
    "be","been","being","it","this","that","these","those","how","what","why","when","where","which","can","could",
    "should","would","do","does","did","i","we","you","they","he","she","them","my","our","your"
}

def extract_keywords(question: str, max_keywords: int = 10) -> list[str]:
    """
    Generic keyword extraction:
    - lowercase
    - keep alphanum tokens
    - drop stopwords
    - prefer longer, more specific tokens
    """
    q = (question or "").lower()
    tokens = re.findall(r"[a-z0-9][a-z0-9\-_/]{2,}", q)  # keeps things like "crashloopbackoff", "dynakube", "k8s"
    tokens = [t for t in tokens if t not in STOPWORDS]

    # Prefer unique tokens, longer first (more specific)
    uniq = []
    seen = set()
    for t in sorted(tokens, key=lambda x: (-len(x), x)):
        if t not in seen:
            seen.add(t)
            uniq.append(t)
        if len(uniq) >= max_keywords:
            break
    return uniq


#adding cleaned whitespace and a snippet of the doc text for better readability in the LLM context. This is used when the keyword fallback finds relevant docs from docs.jsonl, providing a more human-friendly context for the LLM to work with.
import re

def _clean_ws(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()
def keyword_fallback_context(question: str, max_docs: int = 2, snippet_chars: int = 700) -> str:
    """
    Generic fallback:
    - scans docs.jsonl
    - scores by keyword matches in url/title/text
    - returns formatted snippets (NOT full doc text)
    """
    docs = read_docs_jsonl()
    if not docs:
        return ""

    keywords = extract_keywords(question, max_keywords=10)
    if not keywords:
        return ""

    scored = []
    for d in docs:
        url = (d.get("url") or "").lower()
        title = (d.get("title") or "").lower()
        text = (d.get("text") or "").lower()

        score = 0
        for kw in keywords:
            if kw in url:   score += 8
            if kw in title: score += 5
            if kw in text:  score += 1

        if score > 0:
            scored.append((score, d))

    if not scored:
        return ""

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [d for _, d in scored[:max_docs]]

    # Pretty output like Evidence Snippets
    blocks = []
    for i, d in enumerate(top, start=1):
        t = _clean_ws(d.get("title") or "(no title)")
        u = (d.get("url") or "").strip()
        txt = _clean_ws(d.get("text") or "")
        snippet = txt[:snippet_chars] + ("..." if len(txt) > snippet_chars else "")
        blocks.append(f"[F{i}] {t}\nURL: {u}\nSnippet: {snippet}\n")
    print(f"[FALLBACK] Used keyword fallback. keywords={keywords} returned_docs={len(top)}")
    return "\n".join(blocks)

#dedupe urls in the combined context to avoid overwhelming the LLM with repeated sources. This is especially useful when both topic-filtered and all-topics retrieval return overlapping results, ensuring a cleaner context for the LLM.
def dedupe_sources(context: str) -> str:
    seen = set()
    cleaned = []

    for line in context.splitlines():
        if "http" in line:
            urls = line.strip()

            if urls in seen:
                continue

            seen.add(urls)
        cleaned.append(line)
    return "\n".join(cleaned)
           
    

def main():
    r = Retriever(persist_dir="chroma_db", collection_name="dt_public_docs")
    startup_banner()

    print("Topics:", ", ".join(TOPICS))
    print("Type 'exit' to quit.\n")

    while True:
        raw = input("Topic (kubernetes/oneagent/dem or blank): ")
        topic = normalize_topic(raw)

        if topic == "exit":
         break

        if topic == "INVALID":
            print("Invalid topic. Try: kubernetes/k8s/kube, oneagent/oa, dem, or blank for all.\n")
            continue
        q = input("Question: ").strip()
        if q.lower() == "exit":
            break

        cache = load_cache()
        model_name = "llama3.1:8b"
        key = cache_key(topic, q, model_name)

        # ✅ Check cache first
        if key in cache:
            print("\n✅ Using cached answer\n")
            print(cache[key])
            continue

        # ✅ Retrieve evidence
        # ✅ Retrieve evidence (increase recall)
        res = r.query(q, topic=topic, k=15)

        # ✅ If topic-specific retrieval is weak, fallback to ALL topics too
        # (this helps when the doc got classified under a different topic or "unknown")
        res_all = ""
        if topic is not None:
            res_all = r.query(q, topic=None, k=12)

        # Combine both retrievals
        combined_context = ""
        combined_context += "=== TOP SOURCES (topic-filtered) ===\n" + str(res) + "\n"
        if res_all:
            combined_context += "\n=== TOP SOURCES (all-topics fallback) ===\n" + str(res_all) + "\n"

        # ✅ Keyword fallback from docs.jsonl if the key doc still doesn’t show up
        fallback_ctx = keyword_fallback_context(q, max_docs=2)

        if fallback_ctx:
    
            combined_context += "\n=== FALLBACK DOCS (keyword match) ===\n" + fallback_ctx + "\n"
        combined_context = dedupe_sources(combined_context)
        print(combined_context[:2000])  # keep for demo transparency

        print("\n🤖 Generating grounded answer...\n")
        ai_answer = generate_answer(q, combined_context)

        print("====== AI ANSWER ======\n")
        print(ai_answer)
        print("\n=======================\n")
        confidence = confidence_from_urls(combined_context)
        print(f"Confidence based on sources: {confidence}\n")

        # ✅ Save to cache
        cache[key] = ai_answer
        save_cache(cache)


if __name__ == "__main__":
    main()
