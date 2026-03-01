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
def main():
    r = Retriever(persist_dir="chroma_db", collection_name="dt_public_docs")

    print("\nDynatrace Support Copilot (POC)")
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
        res = r.query(q, topic=topic, k=5)
        print(res)  # sources + snippets

        # ✅ Generate grounded answer ONCE
        print("\n🤖 Generating grounded answer...\n")
        ai_answer = generate_answer(q, res)

        print("====== AI ANSWER ======\n")
        print(ai_answer)
        print("\n=======================\n")

        # ✅ Save to cache
        cache[key] = ai_answer
        save_cache(cache)


if __name__ == "__main__":
    main()
