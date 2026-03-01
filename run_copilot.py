from src.retrieval.search import Retriever

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

        res = r.query(q, topic=topic, k=5)
        print(res)

if __name__ == "__main__":
    main()
