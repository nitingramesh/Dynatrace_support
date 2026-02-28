from src.retrieval.search import Retriever, format_support_pack

TOPICS = ["kubernetes", "oneagent", "dem"]

def main():
    r = Retriever(persist_dir="chroma_db", collection_name="dt_public_docs")

    print("\nDynatrace Support Copilot (POC)")
    print("Topics:", ", ".join(TOPICS))
    print("Type 'exit' to quit.\n")

    while True:
        topic = input("Topic (kubernetes/oneagent/dem or blank): ").strip().lower()
        if topic == "exit":
            break
        if topic == "":
            topic = None
        elif topic not in TOPICS:
            print("Invalid topic. Try again.\n")
            continue

        q = input("Question: ").strip()
        if q.lower() == "exit":
            break

        res = r.query(q, topic=topic, k=5)
        print(format_support_pack(res))

if __name__ == "__main__":
    main()
