TraceSage = Meaning

TraceSage = A wise AI that understands system traces and helps diagnose problems.


TraceSage is a local, documentation-driven AI assistant designed to help support engineers quickly surface relevant troubleshooting paths, identify likely causes, and reference official documentation with citations.



Unlike generic AI chatbots, TraceSage only answers using curated documentation and community sources defined in `data/seed_urls.txt`.



This ensures:

- Grounded answers

- Source transparency

- No hallucinated troubleshooting steps

- Controlled knowledge boundaries



---



## 🎯 Purpose



Support engineers spend significant time:

- Searching Dynatrace documentation

- Scanning community posts

- Reviewing troubleshooting guides

- Cross-referencing multiple sources



TraceSage accelerates this process by:



1. Ingesting curated documentation sources

2. Converting them into a searchable knowledge base

3. Retrieving relevant evidence snippets

4. Generating grounded answers with citations

5. Caching responses for repeated queries



---



## 🧠 Architecture

seed_urls.txt

↓

Ingestion (scripts/ingest_urls.py)

↓

docs.jsonl

↓

Vector Index (ChromaDB)

↓

Retriever (Top Sources + Evidence)

↓

Local LLM (Ollama - llama3.1:8b)

↓

Grounded Answer with Citations



Ask questions related to:

- Kubernetes deployment troubleshooting
- Dynatrace OneAgent issues
- DEM synthetic monitoring
- Licensing / DPS usage
- Cluster behavior

TraceSage will:

- Retrieve top relevant sources
- Show evidence snippets
- Generate a grounded answer
- Cite documentation sources
- Cache responses for performance

---

## 🔍 Why Not Use a Generic AI?

TraceSage:

- Does NOT browse the internet
- Does NOT hallucinate undocumented fixes
- Uses ONLY curated documentation
- Provides citation transparency
- Runs fully locally (no external API cost)

---

## 📈 Vision

Future enhancements may include:

- Topic-specific agent routing (Kubernetes Agent, OneAgent Agent, DEM Agent)
- MCP server implementation for tool-based integration
- Automated URL discovery
- Structured troubleshooting trees
- Confidence scoring
- Web-based UI dashboard

---

## 🛡️ Security & Data Control

- Runs entirely locally
- No proprietary ticket data required
- Controlled documentation ingestion
- No external LLM API usage

---

## 👨‍💻 Author

Built as a Proof of Concept to enhance support efficiency through documentation intelligence.

---

## 🧩 License

Internal Proof-of-Concept – Not production-ready.
